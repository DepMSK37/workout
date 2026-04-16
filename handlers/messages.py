from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
import asyncio

from db.queries import log_exercise, complete_workout
from utils.exercises import get_exercise
from utils.nutrition import get_random_nutrition_tip
from .workout_fsm import WorkoutStates

# We will import send_exercise_card from commands avoiding circular if we be careful, or better re-implement/share.
from .commands import send_exercise_card

router = Router()

@router.message(F.text == "✅ Завершил", WorkoutStates.in_progress)
async def exercise_finished_msg(message: Message, state: FSMContext):
    await message.answer("Отлично! Сколько повторений ты сделал? (введи цифру)", reply_markup=ReplyKeyboardRemove())
    await state.set_state(WorkoutStates.waiting_for_reps)

@router.message(WorkoutStates.waiting_for_reps, F.text)
async def process_reps(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введи число (количество повторений).")
        return

    reps = int(message.text)
    data = await state.get_data()
    
    workout_id = data.get("workout_id")
    exercise_idx = data.get("current_exercise_idx", 0)
    round_num = data.get("current_round", 1)
    total_reps = data.get("total_reps", 0)
    
    exercise = get_exercise(exercise_idx)
    
    # Log exercise
    await log_exercise(workout_id, exercise["name"], reps)
    
    # Update total reps
    await state.update_data(total_reps=total_reps + reps)
    
    await state.set_state(WorkoutStates.resting)
    
    msg = await message.answer("⏳ Отдыхаем 1 минуту...")
    
    # Sleep 60s
    await asyncio.sleep(60)
    
    # Проверяем, не сбросил ли юзер тренировку во время отдыха
    current_state = await state.get_state()
    if current_state != WorkoutStates.resting.state:
        return
    
    # Move to next exercise / round
    exercise_idx += 1
    if exercise_idx >= 5:
        # Round complete
        exercise_idx = 0
        round_num += 1
        
    if round_num > 3:
        # Workout complete
        new_data = await state.get_data()
        final_reps = new_data.get("total_reps", 0)
        tonnage = final_reps * 10  # 10 kg total (2 dumbbells x 5kg)
        
        await complete_workout(workout_id)
        
        tip = get_random_nutrition_tip()
        stats_text = (
            "🎉 <b>Тренировка завершена! Вы отлично поработали!</b>\n\n"
            f"💪 Общий тоннаж: {tonnage} кг (исходя из веса 5 кг на руку)\n"
            f"🔄 Выполнено кругов: 3\n\n"
            f"🍏 <b>Совет для восстановления:</b>\n{tip}"
        )
        await message.answer(stats_text, parse_mode="HTML")
        await state.clear()
    else:
        # Next exercise
        await state.update_data(current_exercise_idx=exercise_idx, current_round=round_num)
        await send_exercise_card(message, state)
