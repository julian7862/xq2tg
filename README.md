# XQ2TG Desktop App

跨平台桌面應用，支援 Windows 10/11 & macOS 13+。

## 主要功能
- 監控資料夾新檔案/異動，自動分段推送 Telegram
- PySide6 UI，支援 Bot Token 驗證、資料夾選擇、日誌面板
- 設定檔 config.toml，跨平台儲存
- 日誌保留 7 天，例外不中斷

## 安裝依賴
```bash
pip install -r requirements.txt
```

## 測試
```bash
pytest --cov=xq2tg tests/
```

## 打包
- Windows: PyInstaller
- macOS: BeeWare Briefcase

## 目錄結構
```
xq2tg/
  config.py
  logger.py
  parser.py
  ...
tests/
  test_config.py
  test_logger.py
  test_parser.py
requirements.txt
README.md
```
