from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from config.config import ADMIN_CHAT_ID
from keyboards.inline import get_monitor_keyboard
from services.checker import check_server_status

router = Router()


@router.message(F.text == "/check")
async def check_health_handler(message: Message) -> None:
    if not ADMIN_CHAT_ID or message.from_user.id != ADMIN_CHAT_ID:
        await message.answer("У вас нет доступа к этой информации.")
        return

    waiting_msg = await message.answer("🔄 Опрашиваю сервер...")
    is_ok, details = await check_server_status()

    status_icon = (
        "🟢 <b>Сервер доступен!</b>" if is_ok else "🔴 <b>Сервер недоступен!</b>"
    )
    await waiting_msg.edit_text(
        f"{status_icon}\n{details}",
        parse_mode="HTML",
        reply_markup=get_monitor_keyboard(),  # Прикрепляем кнопку
    )


# Обработка нажатия на инлайн-кнопку
@router.callback_query(F.data == "refresh_status")
async def refresh_status_callback(callback: CallbackQuery) -> None:
    if not ADMIN_CHAT_ID or callback.from_user.id != ADMIN_CHAT_ID:
        await callback.answer("Доступ запрещен", show_alert=True)
        return

    # Менять текст на тот же самый нельзя (aiogram выкинет ошибку),
    # поэтому сначала покажем анимацию загрузки в самом Телеграме
    await callback.answer("Обновляю...")

    is_ok, details = await check_server_status()
    status_icon = (
        "🟢 <b>Сервер доступен!</b>" if is_ok else "🔴 <b>Сервер недоступен!</b>"
    )

    # Редактируем текущее сообщение, обновляя данные и оставляя кнопку
    await callback.message.edit_text(
        f"{status_icon}\n{details}",
        parse_mode="HTML",
        reply_markup=get_monitor_keyboard(),
    )
