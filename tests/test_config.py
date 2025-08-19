import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tempfile
import shutil
import tomli
import pytest
import config

def test_config_read_write(tmp_path, monkeypatch):
    # 模擬 config 路徑
    monkeypatch.setattr(config, "get_config_path", lambda: tmp_path / "config.toml")
    test_cfg = {"watch_dir": "/tmp", "token": "abc", "chat_id": "123"}
    config.save_config(test_cfg)
    loaded = config.load_config()
    assert loaded == test_cfg

def test_config_default(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "get_config_path", lambda: tmp_path / "config.toml")
    loaded = config.load_config()
    assert loaded == config.DEFAULT_CONFIG
