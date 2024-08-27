from aiogram import BaseMiddleware
from utils import get_or_create_user_game


class GameStatusMiddleware(BaseMiddleware):
    """Middleware для проверки активности игры"""

    async def __call__(self, handler, event, data):
        game = get_or_create_user_game(event)

        # Если игра не активна, отправляем сообщение и прерываем обработку события
        if not game.game_active:
            await event.answer("В данный момент игра не активна. Используйте /game для начала новой игры.")
            return

        # Если у игрока закончились жизни, игра считается завершенной
        if game.player.lives <= 0:
            await event.answer("Игра завершена. Используйте /reset для начала новой игры.")
            return

        # Если сейчас не ход игрока, удаляем сообщение
        if not game.player.is_turn_now:
            await event.delete()
            return

        return await handler(event, data)
