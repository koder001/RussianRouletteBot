from aiogram import types
from game.roulette_game import RouletteGame, HandcuffResult, GameStatus
from game.item_manager import Item
from utils import get_or_create_user_game
from database import update_game_stats
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database import get_user_stats, get_top_players
from lexicon import HELP_TEXT
import asyncio


def create_main_menu_keyboard(game: RouletteGame) -> ReplyKeyboardMarkup:
    """Создание клавиатуры главного меню"""
    item_buttons = [KeyboardButton(text=item.value) for item in Item if game.player.items.items[item] > 0]
    main_buttons = [
        [KeyboardButton(text="/self"), KeyboardButton(text="/dealer")]
    ]
    if item_buttons:
        main_buttons.append(item_buttons)
    return ReplyKeyboardMarkup(keyboard=main_buttons, resize_keyboard=True)


async def send_message(message: types.Message, text: str) -> None:
    """Отправка сообщения с клавиатурой"""
    game = get_or_create_user_game(message)
    keyboard = create_main_menu_keyboard(game)
    await message.answer(text, reply_markup=keyboard)


async def send_reload_message(message: types.Message, game: RouletteGame) -> None:
    """Отправка сообщений о перезарядке"""
    await asyncio.sleep(0.2)
    if game.weapon.is_gun_reloaded:
        await send_message(message, game.get_reload_status())


async def handle_status(message: types.Message, game: RouletteGame) -> None:
    """Обработка статусов игры"""
    result_message = {
        GameStatus.LOSS: "Вам нанесли смертельный урон. 💀",
        GameStatus.WIN: "Вы одержали полную победу! Игра завершена.",
        GameStatus.LEVEL_UP: f"Вы победили и переходите на {game.level} уровень!",
        GameStatus.PLAYER_HIT: f"Бах! Игрок: {game.player.health_bar}",
        GameStatus.DEALER_HIT: f"Бах! Дилер: {game.dealer.health_bar}",
        GameStatus.NO_DAMAGE: "Клац!"
    }

    await send_message(message, result_message[game.game_status])


async def end_game(message: types.Message, game: RouletteGame) -> bool:
    """Завершение игры при выигрыше или проигрыше"""
    if game.game_status in (GameStatus.LOSS, GameStatus.WIN):
        win = game.game_status == GameStatus.WIN
        await message.answer("Игра завершена. Используйте /game для начала новой игры.")
        await update_game_stats(message.from_user.id, win=win)
        return True
    return False


async def handle_handcuffs(message: types.Message, game: RouletteGame) -> None:
    """Обработка результатов использования наручников"""
    if game.handcuff_status == HandcuffResult.PLAYER_HANDCUFFED:
        await send_message(message, "Вы пропускаете ход.")
        await dealer_turn(message, game)

    if game.handcuff_status == HandcuffResult.DEALER_HANDCUFFED:
        await send_message(message, "Дилер пропускает ход.")
    elif game.handcuff_status == HandcuffResult.DEALER_TURN:
        await dealer_turn(message, game)


async def process_shoot(message: types.Message, game: RouletteGame) -> None:
    """Обработка результата выстрела"""

    await handle_status(message, game)
    if await end_game(message, game):
        return
    await send_reload_message(message, game)
    await handle_handcuffs(message, game)


async def dealer_turn(message: types.Message, game: RouletteGame) -> None:
    """Ход дилера"""
    target, use_item = game.dealer_turn()
    # Создаем список задач для отправки сообщений об использовании предметов
    tasks = []
    for item in use_item:
        tasks.append(asyncio.create_task(send_message(message, item)))
        await asyncio.sleep(0.2)

    # Ожидаем завершения всех задач
    await asyncio.gather(*tasks)

    await send_turn_message(message, target, game)
    await asyncio.sleep(0.5)
    await process_shoot(message, game)


async def send_turn_message(message: types.Message, target, game: RouletteGame) -> None:
    """Отправка сообщений по результатам выстрела"""
    if target == game.player:
        await send_message(message, "Дилер выстрелил в вас.")
    else:
        await send_message(message, "Дилер выстрелил в себя.")


async def roll_trigger(message: types.Message, target) -> None:
    """Нажатие на курок"""
    game = get_or_create_user_game(message)
    game.process_shoot(game.player, target)
    await process_shoot(message, game)


async def start_or_reset_game(message: types.Message) -> None:
    """Начало или сброс игры"""
    game = get_or_create_user_game(message)
    game.reset_game()
    await send_message(message, "Игра началась.")
    await send_reload_message(message, game)


async def handle_item_usage(message: types.Message) -> None:
    """Обработка использования предмета"""
    game = get_or_create_user_game(message)
    item = next(item for item in Item if item.value == message.text)
    if not game.player.use_item(item):
        await send_message(message, "У вас нет этого предмета.")
        return

    item_messages = {
        Item.DISCARD: f"Вы выкинули {game.weapon.last_bullet_type} патрон.",
        Item.MAGNIFYING_GLASS: f"Это {game.weapon.last_bullet_type} патрон.",
        Item.MEDKIT: f"Игрок: {game.player.health_bar}",
        Item.HANDCUFFS: "Дилер пропустит следующий ход.",
        Item.SAW: "Урон от следующего патрона удвоен."
    }
    await send_message(message, item_messages.get(item, ""))
    await send_reload_message(message, game)


async def show_current_game_status(message: types.Message):
    """Показать статус игры"""
    game = get_or_create_user_game(message)
    await send_message(message, game.get_status())


async def show_total_game_stats(message: types.Message):
    stats = await get_user_stats(message.from_user.id)
    stats_message = (
        f"Сыграно игр: {stats[1]}\n"
        f"Победы: {stats[2]}\n"
        f"Поражения: {stats[3]}\n"
    )
    await message.answer(stats_message)


async def send_help_message(message: types.Message) -> None:
    """Отправка описания игры и инструкций пользователю"""
    await message.answer(HELP_TEXT, parse_mode="HTML")


async def show_top_players(message: types.Message):
    """Отображение топ-10 игроков по количеству побед"""
    top_players = await get_top_players()

    top_players_message = "🏆 <b>Топ-10 игроков по количеству побед:</b>\n\n"

    for rank, (user_id, wins) in enumerate(top_players, start=1):
        user = await message.bot.get_chat(user_id)
        top_players_message += f"{rank}. {user.full_name} - {wins} побед\n"

    await message.answer(top_players_message, parse_mode="HTML")
