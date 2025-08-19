from loguru import logger
from pathlib import Path
import sys

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>")

def set_log_dir(log_dir: Path):
    global LOG_DIR
    LOG_DIR = log_dir
    LOG_DIR.mkdir(exist_ok=True)
    logger.add(str(LOG_DIR / "{time:YYYYMMDD}.log"), rotation="1 day", retention="7 days", encoding="utf-8", level="DEBUG")

logger.add(str(LOG_DIR / "{time:YYYYMMDD}.log"), rotation="1 day", retention="7 days", encoding="utf-8", level="DEBUG")

__all__ = ["logger", "set_log_dir"]
