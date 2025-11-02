from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Dict


def get_poll_keyboard(candidates: Dict[str, str], vote_counts: Dict[str, int]) -> InlineKeyboardMarkup:
    buttons = []
    for candidate_id, candidate_name in candidates.items():
        count = vote_counts.get(candidate_id, 0)
        text = f"{candidate_name} - {count}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"vote_{candidate_id}")])
        
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_channel_check_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_channel")
    ]])


def get_confirm_send_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Yuborish", callback_data="confirm_send"),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_send")
    ]])
