import asyncio
import logging
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN
from db.database import init_db
from handlers import get_handlers_router
from scheduler.tasks import check_inactive_users

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Initialize database
    await init_db()
    
    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Include all routers
    dp.include_router(get_handlers_router())
    
    # Setup scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_inactive_users, "interval", hours=12, kwargs={"bot": bot})
    scheduler.start()
    
    logging.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
