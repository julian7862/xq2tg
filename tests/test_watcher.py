import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tempfile
import shutil
import time
import pytest
from pathlib import Path
from watcher import FolderWatcher

def test_watcher_detects_created_and_modified(tmp_path):
    events = []
    def on_created(path):
        events.append(("created", Path(path).name))
    def on_modified(path):
        events.append(("modified", Path(path).name))
    
    # 建立監控資料夾
    test_dir = tmp_path / "watch"
    test_dir.mkdir()
    watcher = FolderWatcher(str(test_dir), on_created, on_modified)
    watcher.start()
    try:
        # 建立新檔案
        f = test_dir / "a.txt"
        f.write_text("hi")
        time.sleep(0.5)
        # 修改檔案
        f.write_text("hi2")
        time.sleep(0.5)
    finally:
        watcher.stop()
    # 至少要有 created 和 modified 事件
    created = any(e[0] == "created" for e in events)
    modified = any(e[0] == "modified" for e in events)
    assert created and modified
