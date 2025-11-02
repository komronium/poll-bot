from aiogram.fsm.state import State, StatesGroup


class CreatePollStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_candidates = State()
    waiting_for_confirmation = State()
