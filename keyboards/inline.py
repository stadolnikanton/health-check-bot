from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_monitor_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="🔄 Проверить статус сейчас", callback_data="refresh_status"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
