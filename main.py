import asyncio
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from aiogram import Bot, Dispatcher

from config.config import TOKEN
from handlers import common, monitor
from tasks.auto_monitor import auto_monitor_task

dp = Dispatcher()

# Регистрируем роутеры из наших модулей
dp.include_routers(common.router, monitor.router)


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
