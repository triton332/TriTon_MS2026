import numpy as np

def hex_to_rgb(hex_str: str):
    hex_str = hex_str.strip().lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def draw_waveform_frame(samples: np.ndarray, sr: int, t: float, w: int, h: int,
                         bg="#1e1e1e", fg="#00ffcc", window_sec=0.8, thickness=2,
                         progress: float | None = None):
    bg_rgb = np.array(hex_to_rgb(bg), dtype=np.uint8)
    fg_rgb = np.array(hex_to_rgb(fg), dtype=np.uint8)
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    frame[:] = bg_rgb

    # Cửa sổ quanh t
    half = int(window_sec * sr / 2)
    center = int(t * sr)
    start = max(0, center - half)
    end = min(len(samples), center + half)
    seg = samples[start:end]
    if len(seg) < 2:
        return frame

    seg = seg / (np.max(np.abs(seg)) or 1.0)
    idx = np.linspace(0, len(seg) - 1, w).astype(int)
    y = seg[idx]

    mid = h // 2
    amp = int(h * 0.4)
    for x in range(w):
        y_val = int(mid - y[x] * amp)
        y1, y2 = sorted((y_val - thickness, y_val + thickness))
        y1 = max(0, y1); y2 = min(h - 1, y2)
        frame[y1:y2, x, :] = fg_rgb

    # Vẽ vạch tiến độ (preview realtime trong UI)
    if progress is not None:
        px = min(max(int(progress * (w - 1)), 0), w - 1)
        frame[:, px:px+2, :] = (255, 255, 255)

    return frame