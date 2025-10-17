import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "user_config.json"
UI_CFG_PATH = Path(__file__).parent / "ui_config.json"


def load_ui_cfg():
    if UI_CFG_PATH.exists():
        return json.loads(UI_CFG_PATH.read_text(encoding="utf-8"))
    return {"themes": {}, "default_theme": "Soft Glow", "render": {}}


def load_user_theme(default: str = "Soft Glow") -> str:
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            return data.get("theme", default)
        except Exception:
            pass
    # fallback: đọc từ ui_config.json
    ui = load_ui_cfg()
    return ui.get("default_theme", default)


def save_user_theme(theme_name: str):
    data = load_user_all()
    data["theme"] = theme_name
    CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_user_render_defaults():
    ui = load_ui_cfg()
    return ui.get("render", {"resolution": "1080p", "fps": 30, "bitrate_kbps": 6000, "window_sec": 0.8, "codec": "libx264"})


def load_user_all():
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"theme": load_user_theme(), "render": load_user_render_defaults()}


def save_user_render(render_dict: dict):
    data = load_user_all()
    data["render"] = render_dict
    CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")