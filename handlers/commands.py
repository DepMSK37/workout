from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from db.queries import get_or_create_user, start_workout, get_last_exercise_record, reset_user_stats, get_user_workout_history
from utils.exercises import get_exercise
from utils.keyboards import get_main_menu_keyboard
from .workout_fsm import WorkoutStates
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

async def send_exercise_card(message: Message, state: FSMContext):
    data = await state.get_data()
    exercise_idx = data.get("current_exercise_idx", 0)
    round_num = data.get("current_round", 1)
    workout_id = data.get("workout_id")
    user_id = data.get("user_id")

    exercise = get_exercise(exercise_idx)
    if not exercise:
        return

    # Check for previous record
    past_record = await get_last_exercise_record(user_id=user_id, exercise_name=exercise["name"])
    target = past_record.reps + 1 if past_record else exercise["default_target"]

    text = f"🔄 Круг {round_num}/3 | Упражнение {exercise_idx + 1}/5\n\n"
    text += f"🏋️‍♂️ <b>{exercise['name']}</b>\n"
    text += f"📖 {exercise['description']}\n"
    text += f"💡 <i>{exercise['pro_tip']}</i>\n\n"
    
    if past_record:
        text += f"📊 Прошлый рекорд: {past_record.reps} раз.\n"
    
    text += f"🎯 Цель: {target}!"

    builder = ReplyKeyboardBuilder()
    builder.button(text="✅ Завершил")

    import os
    from aiogram.types import FSInputFile
    
    gif_path = exercise.get("gif_path")
    if gif_path and os.path.exists(gif_path):
        animation = FSInputFile(gif_path)
        await message.answer_animation(
            animation=animation,
            caption=text,
            reply_markup=builder.as_markup(resize_keyboard=True),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            text, 
            reply_markup=builder.as_markup(resize_keyboard=True), 
            parse_mode="HTML"
        )
        
    await state.set_state(WorkoutStates.in_progress)

@router.message(CommandStart())
async def cmd_start(message: Message):
    user = await get_or_create_user(message.from_user.id)
    
    await message.answer(
        "Привет! Я твой бот для круговых домашних тренировок.\n"
        "Выбери действие ниже из меню👇",
        reply_markup=get_main_menu_keyboard()
    )

@router.message(Command("reset"))
@router.message(F.text == "🔄 Сбросить статистику")
async def cmd_reset(message: Message, state: FSMContext):
    user = await get_or_create_user(message.from_user.id)
    await reset_user_stats(user.id)
    await state.clear()
    
    await message.answer(
        "🔄 <b>Статистика полностью сброшена!</b>\n\n"
        "Все твои рекорды, история подходов и тоннаж были удалены.",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )

@router.message(F.text == "📊 Моя история")
async def cmd_history(message: Message):
    user = await get_or_create_user(message.from_user.id)
    history = await get_user_workout_history(user.id)
    
    if not history:
        await message.answer("У тебя пока нет завершенных тренировок. Нажми 'Начать тренировку', чтобы сделать первую запись!")
        return

    text = "📊 <b>Твоя история тренировок:</b>\n\n"
    for idx, row in enumerate(history, 1):
        completed_date = row.completed_at.strftime("%d.%m.%Y")
        total_reps = row.total_reps or 0
        tonnage = total_reps * 10
        text += f"🏋️ Тренировка {idx} ({completed_date}): <b>{tonnage} кг</b>\n"

    await message.answer(text, parse_mode="HTML")

@router.message(Command("start_workout"))
@router.message(F.text == "🏋️‍♂️ Начать тренировку")
async def cmd_start_workout(message: Message, state: FSMContext):
    user = await get_or_create_user(message.from_user.id)
    workout = await start_workout(user.id)

    # Initialize FSM data
    await state.set_data({
        "workout_id": workout.id,
        "user_id": user.id,
        "current_round": 1,
        "current_exercise_idx": 0,
        "total_reps": 0
    })

    await message.answer("🚀 Тренировка началась! Погнали!")
    await send_exercise_card(message, state)
