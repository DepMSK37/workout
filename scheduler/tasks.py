from aiogram import Bot
from db.queries import get_inactive_users

async def check_inactive_users(bot: Bot):
    inactive = await get_inactive_users(hours=48)
    for user in inactive:
        try:
            await bot.send_message(
                chat_id=user.telegram_id,
                text="Прошло уже 2 дня с последней тренировки! Мышцы сдуваются. Жми /start_workout"
            )
        except Exception as e:
            print(f"Failed to send push to {user.telegram_id}: {e}")
