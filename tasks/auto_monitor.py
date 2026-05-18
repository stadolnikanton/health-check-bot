import asyncio
import logging

from aiogram import Bot

from config.config import ADMIN_CHAT_ID
from services.checker import check_server_status

server_is_healthy = True


async def auto_monitor_task(bot: Bot) -> None:
    global server_is_healthy

    await asyncio.sleep(5)

    while True:
        is_ok, details = await check_server_status()

        if not is_ok and server_is_healthy:
            server_is_healthy = False
            error_msg = f"🚨 <b>АЛЕРТ: Сервер упал!</b>\n\n{details}"
            try:
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID, text=error_msg, parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"Не удалось отправить алерт админу: {e}")

        elif is_ok and not server_is_healthy:
            server_is_healthy = True
            recovery_msg = f"✅ <b>Ура! Сервер снова онлайн!</b>\n\n{details}"
            try:
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID, text=recovery_msg, parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"Не удалось отправить сообщение о восстановлении: {e}")

        await asyncio.sleep(60)
