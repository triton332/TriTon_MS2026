from pathlib import Path
import numpy as np
from typing import Callable, Optional
from pydub import AudioSegment
from moviepy.editor import AudioFileClip, VideoClip
from proglog import ProgressBarLogger
from .frame_gen import draw_waveform_frame
from .logger import logger


class UILogger(ProgressBarLogger):
    """Chuyển tiến độ MoviePy sang callback UI (0..100)."""
    def __init__(self, progress_cb: Optional[Callable[[int], None]] = None):
        super().__init__()
        self.progress_cb = progress_cb

    def bars_callback(self, bar, attr, value, old_value=None):
        if bar == 't':
            total = self.bars[bar].get('total') or 0
            if total and self.progress_cb:
                p = int(value / total * 100)
                self.progress_cb(min(max(p, 0), 100))


def load_audio_mono_norm(path: Path):
    logger.info(f"Loading audio: {path}")
    audio = AudioSegment.from_file(path)
    sr = audio.frame_rate
    samples = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        samples = samples.reshape((-1, 2)).mean(axis=1)
    samples = samples / (np.max(np.abs(samples)) or 1.0)
    return samples.astype('float32'), sr


def render_waveform_video(audio_path: Path, output_path: Path, *,
                          width=1280, height=720, fps=30,
                          bg="#141420", fg="#00ffcc", window_sec=0.8,
                          bitrate_kbps=6000, codec='libx264',
                          progress_cb: Optional[Callable[[int], None]] = None,
                          preview_cb: Optional[Callable[[float], None]] = None):
    audio_path = Path(audio_path)
    output_path = Path(output_path)

    logger.info(f"Render start → audio={audio_path}, out={output_path}, {width}x{height}@{fps}fps, bitrate={bitrate_kbps}k")

    samples, sr = load_audio_mono_norm(audio_path)
    audio_clip = AudioFileClip(str(audio_path))
    duration = audio_clip.duration

    def make_frame(t):
        if preview_cb:
            preview_cb(min(max(t / duration, 0.0), 1.0))
        return draw_waveform_frame(samples, sr, t, width, height, bg=bg, fg=fg, window_sec=window_sec)

    video = VideoClip(make_frame, duration=duration).set_audio(audio_clip)

    logger_mp = UILogger(progress_cb)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    video.write_videofile(
        str(output_path), fps=fps, codec=codec, audio_codec='aac',
        bitrate=f"{bitrate_kbps}k", threads=4, logger=logger_mp
    )

    logger.info("Render completed")
    if progress_cb:
        progress_cb(100)