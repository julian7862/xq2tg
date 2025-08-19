import json
from pathlib import Path
from typing import Set
import threading

class ProcessedSet:
    def __init__(self, json_path: str):
        self.json_path = Path(json_path)
        self._lock = threading.Lock()
        self._set: Set[str] = set()
        self._load()

    def _load(self):
        if self.json_path.exists():
            try:
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    self._set = set(json.load(f))
            except Exception:
                self._set = set()

    def add(self, fingerprint: str):
        with self._lock:
            self._set.add(fingerprint)
            self._save()

    def __contains__(self, fingerprint: str) -> bool:
        with self._lock:
            return fingerprint in self._set

    def _save(self):
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(list(self._set), f)
        except Exception:
            pass

    def clear(self):
        with self._lock:
            self._set.clear()
            self._save()

# 用法：
# processed = ProcessedSet('processed.json')
# fp = f'{path.name}:{stat.st_size}:{stat.st_mtime}'
# if fp in processed: ...
# processed.add(fp)
