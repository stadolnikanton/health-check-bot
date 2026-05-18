import asyncio
import json
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import httpx
from aiogram import Bot, Dispatcher, html
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID_ENV = os.getenv("ADMIN_CHAT_ID")
ADMIN_CHAT_ID = int(ADMIN_CHAT_ID_ENV) if ADMIN_CHAT_ID_ENV else None

HEALTH_URL = "https://health-check.stadolnik.site/health"

dp = Dispatcher()
server_is_healthy = True


async def check_server_status() -> tuple[bool, str]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(HEALTH_URL, timeout=5.0)
            if response.status_code == 200:
                try:
                    data = response.json()
                    return (
                        True,
                        f"Код: 200\nДанные: <pre><code>{json.dumps(data, ensure_ascii=False)}</code></pre>",
                    )
                except ValueError:
                    return True, f"Код: 200\nОтвет: <code>{response.text}</code>"
            else:
                return (
                    False,
                    f"Сервер вернул код ошибки: <code>{response.status_code}</code>",
                )
        except httpx.ConnectTimeout:
            return False, "Ошибка: Превышено время ожидания (Timeout)."
        except httpx.RequestError as e:
            safe_error = str(e).replace("<", "&lt;").replace(">", "&gt;")
            return False, f"Ошибка соединения: <code>{safe_error}</code>"


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    print(f"User ID: {message.from_user.id}")
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n"
        f"Я слежу за сервером каждую минуту. Ты можете проверить его вручную через /check."
    )


@dp.message(Command("check"))
async def check_health_handler(message: Message) -> None:
    if not ADMIN_CHAT_ID or message.from_user.id != ADMIN_CHAT_ID:
        await message.answer(
            f"Привет, {message.from_user.full_name}!\n"
            f"У вас нет доступа к этой информации."
        )
        return
    waiting_msg = await message.answer("🔄 Опрашиваю сервер...")
    is_ok, details = await check_server_status()

    status_icon = (
        "🟢 <b>Сервер доступен!</b>" if is_ok else "🔴 <b>Сервер недоступен!</b>"
    )
    await waiting_msg.edit_text(f"{status_icon}\n{details}", parse_mode="HTML")


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


async def main() -> None:
    bot = Bot(token=TOKEN)
    logging.basicConfig(level=logging.INFO)

    asyncio.create_task(auto_monitor_task(bot))

    print("Бот и фоновый мониторинг успешно запущены!")
    await dp.start_polling(bot)


if __name__ == "__main__":

    class HealthCheckHandler(BaseHTTPRequestHandler):

        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")

        def log_message(self, format, *args):
            return

    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Фейковый веб-сервер успешно запущен на порту {port}")

    asyncio.run(main())
