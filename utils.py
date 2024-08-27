from game.roulette_game import RouletteGame
from aiogram import types 

# Глобальный словарь игр пользователей
user_games = {}


def get_or_create_user_game(message: types.Message) -> RouletteGame:
    """Получение или создание новой игры для пользователя"""
    user_id = message.from_user.id
    if user_id not in user_games:
        user_games[user_id] = RouletteGame()
    return user_games[user_id]
