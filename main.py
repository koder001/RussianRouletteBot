import asyncio
from aiogram import Bot, Dispatcher
from config import API_TOKEN
from middleware import GameStatusMiddleware
from handlers import common_router, game_router
from database import init_db

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Подключение роутеров
dp.include_router(common_router)
dp.include_router(game_router)
game_router.message.middleware(GameStatusMiddleware())


async def main():
    """Основная функция запуска бота"""
    await init_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
