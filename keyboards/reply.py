from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.helpers import is_admin


def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton(text="📊 So'rovnomalar")]]

    if is_admin(user_id):
        buttons.append([KeyboardButton(text="➕ So'rovnoma yaratish")])
        
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
