# TriTon Music Studio 2026 — Core Project (Dev Flow)


Baseline UI + Waveform preview + CI/CD artifact build. Phù hợp để mở rộng sang Spectrum/Render 4K.


## Features
- UI baseline (PyQt5): combobox Waveform/Spectrum, progress bar, nút Render demo.
- Waveform viewer (QPainter) hiển thị dữ liệu từ file hoặc sine giả lập.
- CI/CD: build zip artifact trên GitHub Actions.


## Setup
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt