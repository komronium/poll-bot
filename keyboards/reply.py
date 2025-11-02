from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.helpers import is_admin


def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    """Get main menu keyboard based on user role"""
    buttons = [
        [KeyboardButton(text="📊 So'rovnomalar")]
    ]
    
    # Add create poll button for admins
    if is_admin(user_id):
        buttons.append([KeyboardButton(text="➕ So'rovnoma yaratish")])
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

