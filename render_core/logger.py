import logging, os
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_PATH = LOG_DIR / "render_log.txt"

# Logger chung
logger = logging.getLogger("studio")
logger.setLevel(logging.INFO)

# File handler
_fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
_fh.setLevel(logging.INFO)
_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
_fh.setFormatter(_formatter)

# Tránh add nhiều lần nếu reload
if not logger.handlers:
    logger.addHandler(_fh)

# UI handler động
class UiHandler(logging.Handler):
    def __init__(self, cb):
        super().__init__()
        self.cb = cb
        self.setFormatter(_formatter)
    def emit(self, record):
        try:
            msg = self.format(record)
            self.cb(msg)
        except Exception:
            pass


def attach_ui_logger(cb):
    """Gắn callback UI để nhận log realtime."""
    # Xoá handler UI cũ nếu có
    to_remove = [h for h in logger.handlers if isinstance(h, UiHandler)]
    for h in to_remove:
        logger.removeHandler(h)
    logger.addHandler(UiHandler(cb))

__all__ = ["logger", "attach_ui_logger", "LOG_PATH"]