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
        "<b>👋 Assalomu alaykum!</b>\n\n"
        "Yilning eng yaxshi BT yetakchisini tanlash va ovoz berish uchun quyidagi tugmalardan birini bosing 👇",
        reply_markup=keyboard
    )
