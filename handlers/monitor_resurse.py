from datetime import datetime, timezone, timedelta

from aiogram import F, Router
from aiogram.types import Message

from config.config import ADMIN_CHAT_ID
from services.checker import check_server_resurse 

router = Router()


@router.message(F.text == "/resurse")
async def check_health_handler(message: Message) -> None:
    if not ADMIN_CHAT_ID or message.from_user.id != ADMIN_CHAT_ID:
        await message.answer("У вас нет доступа к этой информации.")
        return

    waiting_msg = await message.answer("🔄 Опрашиваю сервер...")
    is_ok, details = await check_server_resurse()

    status_icon = (
        "🟢 <b>Сервер доступен!</b>" if is_ok else "🔴 <b>Сервер недоступен!</b>"
    )
    tz_minsk = timezone(timedelta(hours=3))
    current_time = datetime.now(tz_minsk).strftime("%H:%M:%S")

    await waiting_msg.edit_text(
        f"{status_icon}\n\n{details}\n\n🕒 <i>Проверено в: {current_time}</i>",
        parse_mode="HTML",
    )


