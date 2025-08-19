import os
import time
import pytest
from fingerprint import ProcessedSet
from watcher import FolderWatcher

TEST_DATA = """\
======測試通知======
這是測試內容
"""

def test_folder_new_file_triggers_notification(tmp_path):
    processed_path = tmp_path / "processed.json"
    events = []
    contents = []
    def on_created(path):
        if not (path.endswith('.txt') or path.endswith('.print')):
            return
        stat = os.stat(path)
        fp = f'{os.path.basename(path)}:{stat.st_size}:{stat.st_mtime}'
        processed = ProcessedSet(str(processed_path))
        if fp in processed:
            return
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        events.append(os.path.basename(path))
        contents.append(text)
        processed.add(fp)
    def on_modified(path):
        pass
    watcher = FolderWatcher(str(tmp_path), on_created, on_modified)
    watcher.start()
    try:
        file1 = tmp_path / "a.print"
        file1.write_text(TEST_DATA)
        time.sleep(0.5)
        assert events == ["a.print"]
        assert "測試通知" in contents[0]
    finally:
        watcher.stop()
