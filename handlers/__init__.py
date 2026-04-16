from aiogram import Router

from .commands import router as commands_router
from .messages import router as messages_router

def get_handlers_router() -> Router:
    router = Router()
    router.include_router(commands_router)
    router.include_router(messages_router)
    return router
