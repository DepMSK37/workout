from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_menu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🏋️‍♂️ Начать тренировку")
    builder.button(text="📊 Моя история")
    builder.button(text="🔄 Сбросить статистику")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)
