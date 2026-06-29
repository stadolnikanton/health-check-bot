from datetime import datetime, timezone, timedelta

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command, or_f

from config.config import ADMIN_CHAT_ID
from keyboards.inline import get_monitor_keyboard
from services.checker import check_server_status

router = Router()

@router.message(or_f(Command("check"), F.text.lower() == "статус сервера"))
async def check_health_handler(message: Message) -> None:
    if not ADMIN_CHAT_ID or message.from_user.id != ADMIN_CHAT_ID:
        await message.answer("У вас нет доступа к этой информации.")
        return

    waiting_msg = await message.answer("🔄 Опрашиваю сервер...")
    is_ok, details = await check_server_status()

    status_icon = (
        "🟢 <b>Сервер доступен!</b>" if is_ok else "🔴 <b>Сервер недоступен!</b>"
    )
    tz_minsk = timezone(timedelta(hours=3))
    current_time = datetime.now(tz_minsk).strftime("%H:%M:%S")

    await waiting_msg.edit_text(
        f"{status_icon}\n\n{details}\n\n🕒 <i>Проверено в: {current_time}</i>",
        parse_mode="HTML",
        reply_markup=get_monitor_keyboard(),
    )


@router.callback_query(F.data == "refresh_status")
async def refresh_status_callback(callback: CallbackQuery) -> None:
    if not ADMIN_CHAT_ID or callback.from_user.id != ADMIN_CHAT_ID:
        await callback.answer("Доступ запрещен", show_alert=True)
        return

    await callback.answer("Обновляю...")

    is_ok, details = await check_server_status()
    status_icon = (
        "🟢 <b>Сервер доступен!</b>" if is_ok else "🔴 <b>Сервер недоступен!</b>"
    )
    
    tz_minsk = timezone(timedelta(hours=3))
    current_time = datetime.now(tz_minsk).strftime("%H:%M:%S")

    # Оборачиваем в try-except на случай непредвиденных таймингов
    try:
        await callback.message.edit_text(
            f"{status_icon}\n\n{details}\n\n🕒 <i>Проверено в: {current_time}</i>",
            parse_mode="HTML",
            reply_markup=get_monitor_keyboard(),
        )
    except TelegramBadRequest:
        # Если вдруг текст совпал один в один, бот просто проигнорирует ошибку
        pass
