from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    print(f"User ID: {message.from_user.id}")
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n"
        f"Я слежу за сервером каждую минуту. Ты можешь проверить его вручную через /check."
    )
