from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from .workout_fsm import WorkoutStates

router = Router()

@router.callback_query(F.data == "exercise_finished", WorkoutStates.in_progress)
async def exercise_finished_cb(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None) # remove button
    await callback.message.answer("Отлично! Сколько повторений ты сделал? (введи цифру)")
    await state.set_state(WorkoutStates.waiting_for_reps)
    await callback.answer()
