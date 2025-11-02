from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from keyboards.reply import get_main_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    keyboard = get_main_keyboard(user_id)
    
    await message.answer(
        "👋 Salom!\n\n"
        "So'rovnomaga ovoz berish yoki yangi so'rovnoma yaratish uchun kerakli tugmani tanlang:",
        reply_markup=keyboard
    )

