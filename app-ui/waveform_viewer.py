import json
import numpy as np
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtGui import QPainter, QColor, QPen
from pydub import AudioSegment




def _load_theme():
    cfg_path = Path(__file__).parent / "ui_config.json"
    if cfg_path.exists():
        with open(cfg_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"plot_bg": "#1e1e1e", "wave_color": "#00ffcc", "spectrum_color": "#a48be0"}




def _read_audio_mono_norm(path: Path) -> np.ndarray:
    audio = AudioSegment.from_file(path)
    samples = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        samples = samples.reshape((-1, 2)).mean(axis=1)
    peak = np.max(np.abs(samples)) or 1
    return (samples / peak).astype(np.float32)




class WaveformViewer(QWidget):
    """Vẽ waveform/spectrum đơn giản bằng QPainter."""


    def __init__(self, audio_path: str = None, mode: str = "Waveform"):
        super().__init__()
        self.setMinimumHeight(360)
        self.theme = _load_theme()
        self.mode = mode
        self.data = self._load_data(audio_path)
        layout = QVBoxLayout(); layout.setContentsMargins(0, 0, 0, 0); self.setLayout(layout)


    def _load_data(self, audio_path: str):
        try:
            if audio_path and Path(audio_path).exists():
                return _read_audio_mono_norm(Path(audio_path))
        except Exception:
            pass
        return np.sin(np.linspace(0, 40, 4000, dtype=np.float32))


    def set_mode(self, mode: str):
        self.mode = mode
        self.update()
    
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(self.theme["plot_bg"]))
        w, h = self.width(), self.height()
        if w <= 2 or h <= 2 or len(self.data) < 2:
            return
        
        
        if self.mode == "Spectrum":
            arr = np.abs(np.fft.rfft(self.data))
            arr = arr / (np.max(arr) or 1.0)
            color = self.theme["spectrum_color"]
        else:
            arr = self.data
            color = self.theme["wave_color"]
        
        
        pen = QPen(QColor(color)); pen.setWidth(2); painter.setPen(pen)
        mid = h / 2
        step = max(1, int(len(arr) / max(1, w)))
        for i, x in enumerate(range(0, w - 1)):
            j = i * step
            if j + step >= len(arr):
                break
            y1 = mid - arr[j] * (h * 0.4)
            y2 = mid - arr[j + step] * (h * 0.4)
            painter.drawLine(x, int(y1), x + 1, int(y2))