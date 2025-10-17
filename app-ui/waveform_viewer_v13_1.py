import json
import numpy as np
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtGui import QPainter, QColor, QPen
from pydub import AudioSegment
from scipy.ndimage import gaussian_filter1d


def _load_theme(name: str, cfg_path: Path):
    if not cfg_path.exists():
        return {"plot_bg": "#1e1e1e", "wave_color": "#00ffcc", "spectrum_color": "#a48be0", "glow_intensity": 0.4}
    data = json.loads(cfg_path.read_text(encoding="utf-8"))
    return data["themes"].get(name, data["themes"][data.get("default_theme", "Soft Glow")])


def _read_audio_mono_norm(path: Path):
    audio = AudioSegment.from_file(path)
    samples = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        samples = samples.reshape((-1, 2)).mean(axis=1)
    peak = np.max(np.abs(samples)) or 1
    return (samples / peak).astype(np.float32)


class WaveformViewer(QWidget):
    """Visualizer hỗ trợ preview tiến độ (progress marker)"""
    def __init__(self, audio_path: str = None, theme_name: str = "Soft Glow", mode: str = "Waveform"):
        super().__init__()
        self.setMinimumHeight(360)
        self.cfg_path = Path(__file__).parent / "ui_config.json"
        self.theme_name = theme_name
        self.theme = _load_theme(theme_name, self.cfg_path)
        self.mode = mode
        self.data = self._load_data(audio_path)
        self.progress = 0.0  # 0..1 (vạch chạy)
        layout = QVBoxLayout(); layout.setContentsMargins(0, 0, 0, 0); self.setLayout(layout)

    def _load_data(self, audio_path: str):
        try:
            if audio_path and Path(audio_path).exists():
                return _read_audio_mono_norm(Path(audio_path))
        except Exception:
            pass
        return np.sin(np.linspace(0, 40, 4000, dtype=np.float32))

    def set_mode(self, mode: str):
        self.mode = mode; self.update()

    def set_theme(self, theme_name: str):
        self.theme_name = theme_name
        self.theme = _load_theme(theme_name, self.cfg_path)
        self.update()

    def set_progress(self, v: float):
        self.progress = max(0.0, min(1.0, v))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(self.theme["plot_bg"]))
        w, h = self.width(), self.height()
        if w <= 2 or h <= 2 or len(self.data) < 2:
            return

        if self.mode == "Spectrum":
            arr = np.abs(np.fft.rfft(self.data, n=2048))
            arr = arr / (np.max(arr) or 1.0)
            arr = gaussian_filter1d(arr, sigma=2)
            color = QColor(self.theme["spectrum_color"])
        else:
            arr = self.data
            color = QColor(self.theme["wave_color"])

        glow_intensity = self.theme.get("glow_intensity", 0.4)
        glow_pen = QPen(color); glow_pen.setWidth(8)
        glow_pen.setColor(QColor(color.red(), color.green(), color.blue(), int(100 * glow_intensity)))
        pen = QPen(color); pen.setWidth(2)

        painter.setPen(glow_pen)
        mid = h / 2; step = max(1, int(len(arr) / max(1, w)))
        for i, x in enumerate(range(0, w - 1)):
            j = i * step
            if j + step >= len(arr): break
            y1 = mid - arr[j] * (h * 0.4)
            y2 = mid - arr[j + step] * (h * 0.4)
            painter.drawLine(x, int(y1), x + 1, int(y2))

        painter.setPen(pen)
        for i, x in enumerate(range(0, w - 1)):
            j = i * step
            if j + step >= len(arr): break
            y1 = mid - arr[j] * (h * 0.4)
            y2 = mid - arr[j + step] * (h * 0.4)
            painter.drawLine(x, int(y1), x + 1, int(y2))

        # Vẽ vạch tiến độ
        px = min(max(int(self.progress * (w - 1)), 0), w - 1)
        prog_pen = QPen(QColor('#ffffff')); prog_pen.setWidth(2)
        painter.setPen(prog_pen)
        painter.drawLine(px, 0, px, h)