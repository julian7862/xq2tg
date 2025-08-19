import os
import tomli
import tomli_w
from pathlib import Path

DEFAULT_CONFIG = {
    "watch_dir": str(Path.home()),
    "token": "",
    "chat_id": ""
}


def get_config_path():
    if os.name == "nt":
        base = os.getenv("APPDATA")
        if not base:
            base = str(Path.home())
        config_dir = Path(base) / "xq2tg"
    else:
        config_dir = Path.home() / "Library" / "Application Support" / "xq2tg"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.toml"


def load_config():
    path = get_config_path()
    if not path.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    with open(path, "rb") as f:
        return tomli.load(f)


def save_config(cfg):
    path = get_config_path()
    with open(path, "wb") as f:
        tomli_w.dump(cfg, f)
