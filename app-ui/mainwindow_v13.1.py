import sys, os
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QComboBox, QFileDialog,
    QTextEdit, QSpinBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Bảo đảm project-root ở sys.path (khỏi cần set PYTHONPATH thủ công)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

from waveform_viewer_v13_1 import WaveformViewer
from config_manager import load_user_theme, save_user_theme, load_user_all, save_user_render, load_user_render_defaults, load_ui_cfg
from render_core.exporter_v2 import render_waveform_video
from render_core.logger import attach_ui_logger, logger, LOG_PATH

ASSET_AUDIO = str(Path(__file__).parent / "assets" / "sample.wav")


class RenderWorker(QThread):
    progress = pyqtSignal(int)
    preview_p = pyqtSignal(float)
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)
    log_line = pyqtSignal(str)

    def __init__(self, audio_path: str, out_path: str, theme: dict, rset: dict):
        super().__init__()
        self.audio_path = audio_path
        self.out_path = out_path
        self.theme = theme
        self.rset = rset

    def run(self):
        try:
            def _progress_cb(p):
                self.progress.emit(p)
            def _preview_cb(v):
                self.preview_p.emit(v)
            def _log_cb(msg):
                self.log_line.emit(msg)

            logger.info("UI → start render")
            render_waveform_video(
                Path(self.audio_path), Path(self.out_path),
                width=self.rset["width"], height=self.rset["height"], fps=int(self.rset["fps"]),
                bg=self.theme.get("plot_bg", "#141420"),
                fg=self.theme.get("wave_color", "#00ffcc"),
                window_sec=float(self.rset["window_sec"]),
                bitrate_kbps=int(self.rset["bitrate_kbps"]),
                codec=str(self.rset.get("codec", "libx264")),
                progress_cb=_progress_cb, preview_cb=_preview_cb
            )
            self.finished.emit(self.out_path)
        except Exception as e:
            self.failed.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tri Ton Music Studio 2026 — v13.1")
        self.setGeometry(200, 120, 1300, 800)

        # Load config
        cfg = load_user_all()
        self.current_theme = cfg.get("theme", load_user_theme())
        self.rset = cfg.get("render", load_user_render_defaults())

        # Chuẩn hoá rset
        self.rset = self._normalize_rset(self.rset)

        # UI
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(); central.setLayout(layout)

        # --- Top bar: theme + mode ---
        top = QHBoxLayout()
        self.theme_select = QComboBox()
        themes = list(load_ui_cfg().get("themes", {}).keys()) or ["Soft Glow"]
        self.theme_select.addItems(themes)
        self.theme_select.setCurrentText(self.current_theme)
        self.theme_select.currentTextChanged.connect(self.on_change_theme)

        self.view_mode = QComboBox(); self.view_mode.addItems(["Waveform", "Spectrum"])
        self.view_mode.currentIndexChanged.connect(self.on_change_view)

        top.addWidget(QLabel("Theme:")); top.addWidget(self.theme_select)
        top.addWidget(QLabel("View Mode:")); top.addWidget(self.view_mode)
        layout.addLayout(top)

        # --- Render settings row ---
        row = QHBoxLayout()
        self.reso = QComboBox(); self.reso.addItems(["720p", "1080p", "2K", "4K"])
        self.fps = QComboBox(); self.fps.addItems(["24", "30", "60"]) ; self.fps.setCurrentText(str(self.rset["fps"]))
        self.bitrate = QComboBox(); self.bitrate.addItems(["4000", "6000", "12000"]) ; self.bitrate.setCurrentText(str(self.rset["bitrate_kbps"]))
        self.winsec = QDoubleSpinBox(); self.winsec.setRange(0.2, 5.0); self.winsec.setSingleStep(0.1); self.winsec.setValue(float(self.rset["window_sec"]))

        row.addWidget(QLabel("Resolution:")); row.addWidget(self.reso)
        row.addWidget(QLabel("FPS:")); row.addWidget(self.fps)
        row.addWidget(QLabel("Bitrate (kbps):")); row.addWidget(self.bitrate)
        row.addWidget(QLabel("Window (sec):")); row.addWidget(self.winsec)

        self.btn_save = QPushButton("Save Config"); self.btn_save.clicked.connect(self.on_save_config)
        row.addWidget(self.btn_save)

        self.btn_pick = QPushButton("Choose Audio…"); self.btn_pick.clicked.connect(self.pick_audio)
        row.addWidget(self.btn_pick)

        self.btn_render = QPushButton("Render Video"); self.btn_render.clicked.connect(self.start_render)
        row.addWidget(self.btn_render)
        layout.addLayout(row)

        # --- Viewer + progress ---
        self.viewer = WaveformViewer(audio_path=ASSET_AUDIO, theme_name=self.current_theme)
        layout.addWidget(self.viewer, 5)

        self.progress = QProgressBar(); self.progress.setRange(0, 100); self.progress.setValue(0)
        layout.addWidget(self.progress)

        # --- Log panel ---
        self.log = QTextEdit(); self.log.setReadOnly(True); self.log.setMinimumHeight(140)
        layout.addWidget(self.log)

        # Paths
        self.audio_path = ASSET_AUDIO
        self.output_path = str(ROOT / "dist" / "output.mp4")

        # Gắn logger UI
        attach_ui_logger(self._append_log)
        self._append_log(f"Log file → {LOG_PATH}")

    def _normalize_rset(self, r: dict):
        # Map resolution string -> (w,h)
        reso_map = {"720p": (1280, 720), "1080p": (1920, 1080), "2K": (2560, 1440), "4K": (3840, 2160)}
        reso = r.get("resolution", "1080p")
        w, h = reso_map.get(reso, (1920, 1080))
        return {
            "resolution": reso,
            "width": int(r.get("width", w)),
            "height": int(r.get("height", h)),
            "fps": int(r.get("fps", 30)),
            "bitrate_kbps": int(r.get("bitrate_kbps", 6000)),
            "window_sec": float(r.get("window_sec", 0.8)),
            "codec": str(r.get("codec", "libx264"))
        }

    def on_change_theme(self, name):
        save_user_theme(name)
        self.viewer.set_theme(name)

    def on_change_view(self):
        self.viewer.set_mode(self.view_mode.currentText())

    def pick_audio(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select audio", "", "Audio Files (*.wav *.mp3 *.flac *.ogg)")
        if path:
            self.audio_path = path
            self._append_log(f"Selected audio: {path}")
            # Cập nhật viewer với file mới
            v_parent = self.centralWidget().layout()
            idx = v_parent.indexOf(self.viewer)
            self.viewer = WaveformViewer(audio_path=self.audio_path, theme_name=self.theme_select.currentText())
            v_parent.insertWidget(idx, self.viewer, 5)

    def on_save_config(self):
        r = {
            "resolution": self.reso.currentText(),
            "fps": int(self.fps.currentText()),
            "bitrate_kbps": int(self.bitrate.currentText()),
            "window_sec": float(self.winsec.value()),
            "codec": "libx264"
        }
        save_user_render(r)
        self.rset = self._normalize_rset(r)
        self._append_log("Saved render config")

    def start_render(self):
        self.on_save_config()  # đảm bảo rset cập nhật
        Path(ROOT / "dist").mkdir(exist_ok=True)
        self.progress.setValue(0); self.btn_render.setEnabled(False)
        theme = self.viewer.theme
        self.worker = RenderWorker(self.audio_path, self.output_path, theme, self.rset)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.preview_p.connect(self.viewer.set_progress)
        self.worker.finished.connect(self.on_render_done)
        self.worker.failed.connect(self.on_render_fail)
        self.worker.log_line.connect(self._append_log)
        self.worker.start()

    def on_render_done(self, out_path):
        self.btn_render.setEnabled(True)
        self._append_log(f"Render done: {out_path}")

    def on_render_fail(self, msg):
        self.btn_render.setEnabled(True)
        self._append_log(f"Render failed: {msg}")

    def _append_log(self, text: str):
        self.log.append(text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow(); w.show()
    sys.exit(app.exec_())