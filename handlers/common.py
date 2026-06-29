from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import types

from keyboards.panel import admin_panel 

router = Router()




@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    kb = admin_panel
    keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            )
    print(f"User ID: {message.from_user.id}")
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n"
        f"Я слежу за сервером каждую минуту. Ты можешь проверить его вручную через /check.",
        reply_markup=keyboard
    )
