from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QFileDialog, QPlainTextEdit, QStatusBar, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QObject
from PySide6.QtGui import QIcon
import sys
import re
import os
import threading
import time
import platform
from watcher import FolderWatcher
import config

class WorkerSignals(QObject):
    log = Signal(str, str)
    status = Signal(str, str)
    finished = Signal()

class WatcherThread(QThread):
    def __init__(self, watch_dir, recursive, token, chat_id, signals):
        super().__init__()
        self.watch_dir = watch_dir
        self.recursive = recursive
        self.token = token
        self.chat_id = chat_id
        self.signals = signals
        self.processed = set()
        self._stop_event = threading.Event()
        self.loop = None

    def run(self):
        def on_created(path):
            self.handle_file(path)
        def on_modified(path):
            self.handle_file(path)
        self.watcher = FolderWatcher(self.watch_dir, on_created, on_modified, self.recursive)
        self.watcher.start()
        self.signals.status.emit("watching", "監控中")
        try:
            while not self._stop_event.is_set():
                time.sleep(0.5)
        finally:
            self.watcher.stop()
            self.signals.status.emit("paused", "已暫停")
            self.signals.finished.emit()

    def stop(self):
        self._stop_event.set()

    def handle_file(self, path):
        # 僅處理 .txt/.print 新增檔案
        if not (path.endswith('.txt') or path.endswith('.print')):
            return
        try:
            stat = os.stat(path)
            fp = f'{os.path.basename(path)}:{stat.st_size}:{stat.st_mtime}'
            if fp in self.processed:
                return
            # 嘗試用 utf-8 讀取，失敗則 fallback big5
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
            except UnicodeDecodeError:
                try:
                    with open(path, 'r', encoding='big5') as f:
                        text = f.read()
                except Exception as e:
                    self.signals.log.emit(f"檔案處理失敗: {e}", "ERROR")
                    return
            preview = text[:100].replace('\n', ' ')
            self.signals.log.emit(f"偵測到新檔案: {os.path.basename(path)}", "INFO")
            self.signals.status.emit("watching", f"新檔案: {os.path.basename(path)}")
            # 若 token/chat_id 有填寫則推送 Telegram
            if self.token and self.chat_id:
                try:
                    import asyncio
                    from xq_telegram import TelegramSender
                    async def send():
                        sender = TelegramSender(self.token, self.chat_id)
                        await sender.send_segment(text[:4096])
                    asyncio.run(send())
                    self.signals.log.emit("Telegram 傳送成功", "INFO")
                except Exception as e:
                    self.signals.log.emit(f"Telegram 傳送失敗: {e}", "ERROR")
            self.processed.add(fp)
        except Exception as e:
            self.signals.log.emit(f"檔案處理失敗: {e}", "ERROR")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XQ2TG Desktop App")
        self.resize(700, 480)
        self.central = QWidget()
        self.setCentralWidget(self.central)
        layout = QVBoxLayout(self.central)

        # 路徑選擇
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.btn_browse = QPushButton("選擇資料夾")
        self.btn_browse.clicked.connect(self.choose_folder)
        path_layout.addWidget(QLabel("監控路徑:"))
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.btn_browse)
        layout.addLayout(path_layout)

        # Telegram 設定
        tg_layout = QHBoxLayout()
        self.token_edit = QLineEdit()
        self.token_edit.setPlaceholderText("Telegram Bot Token")
        self.token_status = QLabel("❌")
        self.chatid_edit = QLineEdit()
        self.chatid_edit.setPlaceholderText("Chat ID")
        self.chatid_status = QLabel("❌")
        tg_layout.addWidget(QLabel("Bot Token:"))
        tg_layout.addWidget(self.token_edit)
        tg_layout.addWidget(self.token_status)
        tg_layout.addWidget(QLabel("Chat ID:"))
        tg_layout.addWidget(self.chatid_edit)
        tg_layout.addWidget(self.chatid_status)
        layout.addLayout(tg_layout)

        # 控制按鈕
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("啟動")
        self.btn_pause = QPushButton("暫停")
        self.btn_refresh = QPushButton("重新整理檔案列表")
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_pause)
        btn_layout.addWidget(self.btn_refresh)
        layout.addLayout(btn_layout)

        # 日誌面板 (QPlainTextEdit, 只顯示 WARN+)
        self.log_panel = QPlainTextEdit()
        self.log_panel.setReadOnly(True)
        layout.addWidget(QLabel("日誌："))
        layout.addWidget(self.log_panel)

        # 狀態列
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.set_status("待機")
        self.last_result = ""

        # Bot Token/Chat ID 即時驗證
        self.token_edit.textChanged.connect(self.check_token)
        self.chatid_edit.textChanged.connect(self.check_chatid)

        # 欄位預設值 (自動載入 config)
        try:
            cfg = config.load_config()
            self.path_edit.setText(cfg.get("watch_dir", ""))
            self.token_edit.setText(cfg.get("token", ""))
            self.chatid_edit.setText(cfg.get("chat_id", ""))
        except Exception:
            pass

        # 工作線程與信號
        self.worker = None
        self.signals = WorkerSignals()
        self.signals.log.connect(self.append_log)
        self.signals.status.connect(self.set_status)
        self.btn_start.clicked.connect(self.start_watching)
        self.btn_pause.clicked.connect(self.pause_watching)
        self.btn_refresh.clicked.connect(self.refresh_files)

    def check_token(self):
        token = self.token_edit.text().strip()
        if token.startswith("5") and len(token) > 30:
            self.token_status.setText("✅")
        else:
            self.token_status.setText("❌")

    def check_chatid(self):
        chatid = self.chatid_edit.text().strip()
        if re.fullmatch(r"-?\d{6,}", chatid):
            self.chatid_status.setText("✅")
        else:
            self.chatid_status.setText("❌")

    def choose_folder(self):
        d = QFileDialog.getExistingDirectory(self, "選擇資料夾")
        if d:
            self.path_edit.setText(d)

    def set_status(self, state, result=None):
        # 狀態列顯示狀態與最近一次傳送結果
        status_map = {
            "idle": "待機",
            "watching": "監控中",
            "paused": "暫停",
            "fail": "失敗"
        }
        msg = status_map.get(state, state)
        if result:
            msg += f" | {result}"
        self.status.showMessage(msg)
        self.last_result = result or ""

    def append_log(self, text, level="INFO"):
        self.log_panel.appendPlainText(text)
        self.log_panel.verticalScrollBar().setValue(self.log_panel.verticalScrollBar().maximum())

    def show_system_notification(self, title, message):
        # macOS: 使用 osascript
        if platform.system() == "Darwin":
            import subprocess
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", script])
        # Windows: 使用 QSystemTrayIcon
        elif platform.system() == "Windows":
            from PySide6.QtWidgets import QSystemTrayIcon
            if not hasattr(self, '_tray_icon'):
                self._tray_icon = QSystemTrayIcon(QIcon(), self)
                self._tray_icon.show()
            self._tray_icon.showMessage(title, message)
        # 其他平台可擴充

    def start_watching(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "警告", "監控已在執行中")
            return
        watch_dir = self.path_edit.text().strip()
        token = self.token_edit.text().strip()
        chat_id = self.chatid_edit.text().strip()
        # 啟動時自動寫入 config.toml
        try:
            config.save_config({
                "watch_dir": watch_dir,
                "token": token,
                "chat_id": chat_id
            })
        except Exception as e:
            self.append_log(f"設定儲存失敗: {e}", "ERROR")
        self.worker = WatcherThread(watch_dir, False, token, chat_id, self.signals)
        self.worker.start()
        self.set_status("watching", "監控中")
        self.show_system_notification("XQ2TG 啟動成功", f"開始監控：{watch_dir}")

    def pause_watching(self):
        if self.worker:
            self.worker.stop()
            self.worker.wait()
            self.set_status("paused", "已暫停")

    def refresh_files(self):
        # 手動掃描所有檔案
        watch_dir = self.path_edit.text().strip()
        processed = set()
        for fname in os.listdir(watch_dir):
            path = os.path.join(watch_dir, fname)
            if not (fname.endswith('.txt') or fname.endswith('.print')):
                continue
            stat = os.stat(path)
            fp = f'{os.path.basename(path)}:{stat.st_size}:{stat.st_mtime}'
            if fp in processed:
                continue
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
                # 僅作日誌紀錄，不再重複傳送
                self.append_log(f"檔案已掃描: {os.path.basename(path)}", "INFO")
                processed.add(fp)
            except Exception as e:
                self.append_log(f"手動掃描失敗: {e}", "ERROR")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
