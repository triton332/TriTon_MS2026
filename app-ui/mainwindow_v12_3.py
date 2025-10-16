import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QProgressBar, QComboBox
from PyQt5.QtCore import Qt, QTimer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tri Ton Music Studio 2026 — v12.3")
        self.setGeometry(200, 150, 1280, 720)
        self.setStyleSheet("background-color: #f4f4f8;")

        # Widget chính
        self.central = QWidget()
        self.setCentralWidget(self.central)
        layout = QVBoxLayout()
        self.central.setLayout(layout)

        # Thanh chọn chế độ hiển thị
        top_bar = QHBoxLayout()
        self.view_mode = QComboBox()
        self.view_mode.addItems(["Waveform", "Spectrum"])
        top_bar.addWidget(QLabel("View Mode:"))
        top_bar.addWidget(self.view_mode)
        layout.addLayout(top_bar)

        # Khu vực preview sóng
        self.preview_label = QLabel("[Audio Visualizer Preview]")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 2px dashed #ccc; color: #777; font-size: 18px;")
        layout.addWidget(self.preview_label, 5)

        # Thanh progress
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        layout.addWidget(self.progress)

        # Nút Render demo
        self.btn_render = QPushButton("Render Demo")
        self.btn_render.clicked.connect(self.start_render)
        layout.addWidget(self.btn_render)

    def start_render(self):
        self.progress.setValue(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)

    def update_progress(self):
        val = self.progress.value() + 2
        if val <= 100:
            self.progress.setValue(val)
        else:
            self.timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())