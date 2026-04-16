from aiogram.fsm.state import State, StatesGroup

class WorkoutStates(StatesGroup):
    in_progress = State()
    waiting_for_reps = State()
    resting = State()
