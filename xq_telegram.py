import asyncio
from typing import Optional
from loguru import logger
from telegram import Bot
from telegram.error import RetryAfter, TelegramError

class TelegramSender:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.bot = Bot(token=token)

    async def send_segment(self, text: str, max_retries: int = 3) -> bool:
        delay = 1
        for attempt in range(max_retries):
            try:
                await self.bot.send_message(chat_id=self.chat_id, text=text, disable_web_page_preview=True)
                logger.info(f"Telegram 傳送成功: {text[:30]}...")
                return True
            except RetryAfter as e:
                logger.warning(f"Telegram 速率限制，等待 {e.retry_after} 秒 (第{attempt+1}次)")
                await asyncio.sleep(e.retry_after)
            except TelegramError as e:
                logger.error(f"Telegram 傳送失敗: {e}")
                await asyncio.sleep(delay)
                delay *= 2
            except Exception as e:
                logger.error(f"Telegram 例外: {e}")
                await asyncio.sleep(delay)
                delay *= 2
        logger.error(f"Telegram 傳送失敗 (重試{max_retries}次): {text[:30]}...")
        return False

    async def send_segments(self, segments, max_retries=3):
        results = []
        for seg in segments:
            ok = await self.send_segment(seg, max_retries=max_retries)
            results.append(ok)
        return results
