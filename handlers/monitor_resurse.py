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

    # Отправляем красивый промежуточный статус
    waiting_msg = await message.answer("⏳ <i>Опрашиваю серверные ресурсы...</i>", parse_mode="HTML")
    
    # Стучимся к FastAPI
    is_ok, details = await check_server_resurse()
    
    # Считаем точное время по Минску
    tz_minsk = timezone(timedelta(hours=3))
    current_time = datetime.now(tz_minsk).strftime("%H:%M:%S")
    
    # Собираем красивый финальный ответ
    if is_ok:
        response_text = (
            f"🟢 <b>Сервер доступен</b>\n\n"
            f"{details}\n\n"
            f"🕒 <i>Обновлено: {current_time}</i>"
        )
    else:
        response_text = (
            f"🔴 <b>Критическая ошибка опроса</b>\n\n"
            f"{details}\n\n"
            f"🕒 <i>Время сбоя: {current_time}</i>"
        )

    # Редактируем сообщение, подставляя готовый отформатированный текст
    await waiting_msg.edit_text(
        text=response_text,
        parse_mode="HTML"
    )
