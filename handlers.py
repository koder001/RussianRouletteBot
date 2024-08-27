from aiogram import Router, F, types
from aiogram.filters import Command
from utils import get_or_create_user_game
from service import (
    roll_trigger, start_or_reset_game, handle_item_usage,
    show_current_game_status, show_total_game_stats,
    send_help_message, show_top_players
    )
from game.item_manager import Item

# Создание роутеров
common_router = Router()
game_router = Router()


@common_router.message(Command("start"))
async def send_welcome(message: types.Message):
    """Отправка приветственного сообщения"""
    await message.answer("Привет! Это игра в русскую рулетку. Нажмите /game, чтобы начать игру.")


@common_router.message(Command("game"))
@common_router.message(Command("reset"))
async def handle_start_or_reset_game(message: types.Message):
    """Начало новой игры или сброс текущей"""
    await start_or_reset_game(message)


@game_router.message(Command("self"))
async def roll_self(message: types.Message):
    """Выстрел в себя"""
    game = get_or_create_user_game(message)
    await roll_trigger(message, game.player)


@game_router.message(Command("dealer"))
async def roll_dealer(message: types.Message):
    """Выстрел в дилера"""
    game = get_or_create_user_game(message)
    await roll_trigger(message, game.dealer)


@game_router.message(Command("status"))
async def handle_show_current_game_status(message: types.Message):
    """Показать статус игры"""
    await show_current_game_status(message)


@game_router.message(F.text.in_([item.value for item in Item]))
async def use_selected_item(message: types.Message):
    """Использование выбранного предмета"""
    await handle_item_usage(message)


@common_router.message(Command("stats_game"))
async def handle_show_total_game_stats(message: types.Message):
    """Показать статистики"""
    await show_total_game_stats(message)


@common_router.message(Command("help"))
async def handle_help_command(message: types.Message) -> None:
    """Обработчик команды /help"""
    await send_help_message(message)


@common_router.message(Command("top"))
async def top_command(message: types.Message):
    """Команда для вывода топ-10 игроков"""
    await show_top_players(message)