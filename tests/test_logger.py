import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logger

def test_logger_creates_logfile(tmp_path, monkeypatch):
    # 動態設定 logs 目錄
    logger.set_log_dir(tmp_path)
    logger.logger.info("test123")
    files = list(tmp_path.glob("*.log"))
    assert files
