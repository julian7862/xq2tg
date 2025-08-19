import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from typing import Callable, Optional

class SimpleHandler(FileSystemEventHandler):
    def __init__(self, on_created: Callable[[str], None], on_modified: Callable[[str], None]):
        self.on_created_cb = on_created
        self.on_modified_cb = on_modified

    def on_created(self, event: FileSystemEvent):
        if not event.is_directory:
            self.on_created_cb(event.src_path)

    def on_modified(self, event: FileSystemEvent):
        if not event.is_directory:
            self.on_modified_cb(event.src_path)

class FolderWatcher:
    def __init__(self, watch_dir: str, on_created: Callable[[str], None], on_modified: Callable[[str], None], recursive: bool = False):
        self.watch_dir = Path(watch_dir)
        self.observer = Observer()
        self.handler = SimpleHandler(on_created, on_modified)
        self.recursive = recursive
        self._running = False

    def start(self):
        self.observer.schedule(self.handler, str(self.watch_dir), recursive=self.recursive)
        self.observer.start()
        self._running = True

    def stop(self):
        self.observer.stop()
        self.observer.join()
        self._running = False

    def is_running(self):
        return self._running

# Example usage:
# def on_created(path):
#     print(f"Created: {path}")
# def on_modified(path):
#     print(f"Modified: {path}")
# watcher = FolderWatcher("/tmp", on_created, on_modified)
# watcher.start()
# time.sleep(10)
# watcher.stop()
