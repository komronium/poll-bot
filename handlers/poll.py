import json
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery as CBQ
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_db
from services.poll_service import PollService
from keyboards.inline import get_poll_keyboard, get_channel_check_keyboard, get_confirm_send_keyboard
from keyboards.reply import get_main_keyboard
from utils.helpers import is_admin
from config import settings

router = Router()


class CreatePollStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_candidates = State()
    waiting_for_confirmation = State()


@router.message(Command("create_poll"))
async def cmd_create_poll(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ So'rovnoma yaratish faqat adminlar uchun mumkin.")
        return
    
    await message.answer("📝 So'rovnoma matnini kiriting:")
    await state.set_state(CreatePollStates.waiting_for_question)


@router.message(lambda m: m.text == "➕ So'rovnoma yaratish")
async def create_poll_button(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ So'rovnoma yaratish faqat adminlar uchun mumkin.")
        return
    
    await message.answer("📝 So'rovnoma matnini kiriting:")
    await state.set_state(CreatePollStates.waiting_for_question)


@router.message(lambda m: m.text == "📊 So'rovnomalar")
async def show_polls(message: Message):
    from config import settings
    await message.answer(
        f"📊 So'rovnomalar {settings.CHANNEL_ID} kanalida joylashgan.\n\n"
        "Ovoz berish uchun kanalga o'tib, so'rovnomalardagi tugmalardan foydalaning."
    )


@router.message(CreatePollStates.waiting_for_question)
async def process_question(message: Message, state: FSMContext):
    await state.update_data(
        question=message.text,
        original_message_id=message.message_id,
        original_chat_id=message.chat.id
    )
    await message.answer(
        "👥 Nomzodlarni bir qatorda vergul bilan kiriting:\n\n"
        "💡 Masalan: Ali, Vali, Hasan"
    )
    await state.set_state(CreatePollStates.waiting_for_candidates)


@router.message(CreatePollStates.waiting_for_candidates)
async def process_candidates(message: Message, state: FSMContext):
    candidates_list = [c.strip() for c in message.text.split(",") if c.strip()]
    
    if len(candidates_list) < 2:
        await message.answer("❌ Kamida 2 ta nomzod bo'lishi kerak. Qayta urinib ko'ring:")
        return
    
    data = await state.get_data()
    question = data.get("question")
    
    # Create candidates dict
    candidates = {str(i+1): name for i, name in enumerate(candidates_list)}
    
    # Save poll data in state
    poll_data_preview = {
        "question": question,
        "candidates": candidates,
        "vote_counts": {cid: 0 for cid in candidates.keys()}
    }
    await state.update_data(
        candidates=candidates,
        poll_data=poll_data_preview
    )
    await state.set_state(CreatePollStates.waiting_for_confirmation)
    
    # Show preview with inline keyboard (exactly as it will appear in channel)
    preview_text = question  # Admin matni
    preview_keyboard = get_poll_keyboard(candidates, poll_data_preview["vote_counts"])
    
    # Store that this is a preview (we'll mark it in state)
    await state.update_data(is_preview=True)
    
    await message.answer(
        "📊 Kanalda qanday ko'rinadi:\n\n"
        "⬇️ Quyidagi ko'rinishda kanalga yuboriladi ⬇️"
    )
    
    # Send preview message exactly as it will appear in channel
    preview_message = await message.answer(
        preview_text,
        reply_markup=preview_keyboard
    )
    
    # Store preview message_id to handle preview votes
    await state.update_data(preview_message_id=preview_message.message_id)
    
    # Ask for confirmation
    await message.answer(
        "✅ Kanalga yuborilsinmi?",
        reply_markup=get_confirm_send_keyboard()
    )


@router.callback_query(lambda c: c.data == "confirm_send")
async def confirm_send_poll(callback: CBQ, state: FSMContext):
    data = await state.get_data()
    poll_data = data.get("poll_data")
    candidates = data.get("candidates")
    question = poll_data["question"]
    original_message_id = data.get("original_message_id")
    original_chat_id = data.get("original_chat_id")
    
    # Create poll in database
    with get_db() as db:
        poll = PollService.create_poll(db, question, candidates)
        
        bot = callback.bot
        keyboard = get_poll_keyboard(candidates, poll_data["vote_counts"])
        
        # Copy message from admin to channel
        if original_message_id and original_chat_id:
            copied_message = await bot.copy_message(
                chat_id=settings.CHANNEL_ID,
                from_chat_id=original_chat_id,
                message_id=original_message_id
            )
            
            # Edit message to add inline keyboard
            await bot.edit_message_reply_markup(
                chat_id=settings.CHANNEL_ID,
                message_id=copied_message.message_id,
                reply_markup=keyboard
            )
            
            # Update poll with message_id
            PollService.update_message_id(db, poll.id, copied_message.message_id)
        else:
            # Fallback if message_id not found
            sent_message = await bot.send_message(
                chat_id=settings.CHANNEL_ID,
                text=question,
                reply_markup=keyboard
            )
            PollService.update_message_id(db, poll.id, sent_message.message_id)
    
    await callback.answer("✅ So'rovnoma kanalga yuborildi!", show_alert=True)
    await callback.message.edit_text("✅ So'rovnoma kanalga muvaffaqiyatli yuborildi!")
    
    # Show main keyboard after creating poll
    user_id = callback.from_user.id
    await callback.message.answer(
        "🏠 Bosh menyu",
        reply_markup=get_main_keyboard(user_id)
    )
    
    await state.clear()


@router.callback_query(lambda c: c.data == "cancel_send")
async def cancel_send_poll(callback: CBQ, state: FSMContext):
    await callback.answer("❌ So'rovnoma yaratish bekor qilindi")
    await callback.message.edit_text("❌ So'rovnoma yaratish bekor qilindi.")
    
    # Show main keyboard
    user_id = callback.from_user.id
    await callback.message.answer(
        "🏠 Bosh menyu",
        reply_markup=get_main_keyboard(user_id)
    )
    
    await state.clear()


@router.callback_query(lambda c: c.data and c.data.startswith("vote_"))
async def process_vote(callback: CBQ, state: FSMContext = None):
    candidate_id = callback.data.split("_")[1]
    user_id = callback.from_user.id
    bot = callback.bot
    
    # Check if this is a preview vote (during poll creation)
    if state:
        try:
            state_data = await state.get_data()
            preview_message_id = state_data.get("preview_message_id")
            if preview_message_id and callback.message.message_id == preview_message_id:
                await callback.answer("👁️ Bu faqat ko'rinish (preview). Kanalga yuborilgandan keyin ovoz berishingiz mumkin.", show_alert=True)
                return
        except Exception:
            pass  # If state is not available, continue with normal vote processing
    
    # Check channel membership first
    try:
        chat_member = await bot.get_chat_member(
            chat_id=settings.CHANNEL_ID,
            user_id=user_id
        )
        is_member = chat_member.status in ["member", "administrator", "creator"]
    except Exception:
        is_member = False
    
    if not is_member:
        await callback.answer(
            "⚠️ Ovoz berish uchun kanalga a'zo bo'lishingiz kerak!",
            show_alert=True
        )
        # Send message to user with channel link
        try:
            await bot.send_message(
                chat_id=user_id,
                text=f"📢 So'rovnomaga ovoz berish uchun kanalga a'zo bo'ling:\n{settings.CHANNEL_ID}\n\n"
                     "A'zo bo'lgach, tekshirish tugmasini bosing:",
                reply_markup=get_channel_check_keyboard()
            )
        except Exception:
            pass
        return
    
    # Get poll message_id
    poll_message_id = callback.message.message_id
    
    with get_db() as db:
        # Check if user already voted
        if PollService.has_user_voted(db, user_id, poll_message_id):
            await callback.answer("❌ Siz allaqachon ovoz bergansiz!", show_alert=True)
            return
        
        # Record vote
        success = PollService.vote(db, user_id, poll_message_id, candidate_id)
        
        if not success:
            await callback.answer("❌ Ovoz berishda xatolik yuz berdi!", show_alert=True)
            return
        
        # Get updated poll data
        poll_data = PollService.get_poll_data(db, poll_message_id)
        if not poll_data:
            await callback.answer("❌ So'rovnoma topilmadi!", show_alert=True)
            return
        
        # Update message - admin matni o'zgarmaydi, faqat inline tugmalar yangilanadi
        keyboard = get_poll_keyboard(poll_data['candidates'], poll_data['vote_counts'])
        
        try:
            # Update only reply markup (not text) since it's a copied message
            await bot.edit_message_reply_markup(
                chat_id=callback.message.chat.id,
                message_id=poll_message_id,
                reply_markup=keyboard
            )
            await callback.answer("✅ Ovozingiz qabul qilindi!")
        except Exception as e:
            # Fallback: try to edit text and reply_markup together
            try:
                text = poll_data['question']
                await bot.edit_message_text(
                    chat_id=callback.message.chat.id,
                    message_id=poll_message_id,
                    text=text,
                    reply_markup=keyboard
                )
                await callback.answer("✅ Ovozingiz qabul qilindi!")
            except Exception:
                await callback.answer("✅ Ovoz qabul qilindi!", show_alert=True)


@router.callback_query(lambda c: c.data == "check_channel")
async def check_channel_membership(callback: CBQ):
    user_id = callback.from_user.id
    bot = callback.bot
    
    try:
        chat_member = await bot.get_chat_member(
            chat_id=settings.CHANNEL_ID,
            user_id=user_id
        )
        is_member = chat_member.status in ["member", "administrator", "creator"]
    except Exception:
        is_member = False
    
    if is_member:
        await callback.answer("✅ Kanalga a'zosiz! Endi ovoz bera olasiz.", show_alert=True)
        await callback.message.edit_text(
            "✅ Kanalga a'zosiz!\n\n"
            "Kanaldagi so'rovnomaga qaytib ovoz bering."
        )
    else:
        await callback.answer("❌ Hali kanalga a'zo emassiz. A'zo bo'ling va qayta urinib ko'ring.", show_alert=True)

