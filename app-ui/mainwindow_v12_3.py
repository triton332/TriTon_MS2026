import sys
from PyQt5.QtWidgets import (
QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
QPushButton, QLabel, QProgressBar, QComboBox
)
from PyQt5.QtCore import Qt, QTimer
from waveform_viewer import WaveformViewer


ASSET_AUDIO = "app-ui/assets/sample.wav"




class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Tri Ton Music Studio 2026 — v12.3")
        self.setGeometry(200, 150, 1280, 720)
        self.setStyleSheet("background-color: #f4f4f8;")
        
        
        self.central = QWidget(); self.setCentralWidget(self.central)
        self.layout = QVBoxLayout(); self.central.setLayout(self.layout)
        
        
        top_bar = QHBoxLayout()
        self.view_mode = QComboBox(); self.view_mode.addItems(["Waveform", "Spectrum"])
        self.view_mode.currentIndexChanged.connect(self.change_view)
        top_bar.addWidget(QLabel("View Mode:")); top_bar.addWidget(self.view_mode)
        self.layout.addLayout(top_bar)
        
        
        self.viewer = WaveformViewer(audio_path=ASSET_AUDIO, mode="Waveform")
        self.layout.addWidget(self.viewer, 5)
        
        
        self.progress = QProgressBar(); self.progress.setRange(0, 100); self.layout.addWidget(self.progress)
        self.btn_render = QPushButton("Render Demo"); self.btn_render.clicked.connect(self.start_render); self.layout.addWidget(self.btn_render)


    def start_render(self):
        self.progress.setValue(0)
        self.timer = QTimer(); self.timer.timeout.connect(self.update_progress); self.timer.start(100)
    
    
    def update_progress(self):
        val = self.progress.value() + 2
        if val <= 100:
            self.progress.setValue(val)
        else:
            self.timer.stop()
    
    
    def change_view(self):
        self.viewer.set_mode(self.view_mode.currentText())




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())