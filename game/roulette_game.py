import random
from game.settings import MIN_ITEMS, MAX_ITEMS, LEVELS_INFO
from game.player import Player
from game.dealer import Dealer
from game.weapon import Weapon
from enum import Enum, auto


class HandcuffResult(Enum):
    PLAYER_HANDCUFFED = auto()
    DEALER_HANDCUFFED = auto()
    DEALER_TURN = auto()


class GameStatus(Enum):
    LOSS = auto()
    WIN = auto()
    LEVEL_UP = auto()
    PLAYER_HIT = auto()
    DEALER_HIT = auto()
    NO_DAMAGE = auto()


class RouletteGame:
    """Класс для управления игрой и уровнями в русскую рулетку"""

    def __init__(self):
        self.game_active = False

    def reset_game(self):
        """Сброс игры и настройка нового уровня"""
        self.level = 1
        self.game_active = True
        self._setup_level()

    def _setup_level(self):
        """Настройка текущего уровня"""
        self.game_status = None
        self.handcuff_status = None
        self.weapon = Weapon()
        self.level_info = LEVELS_INFO[self.level]
        self._initialize_participants()
        self.distribute_items()

    def _initialize_participants(self):
        """Создание участников и установка их оппонентов"""
        self.player = Player(self.level_info["lives"], self.weapon)
        self.dealer = Dealer(self.level_info["lives"], self.weapon)

        self.player.set_opponent(self.dealer)
        self.dealer.set_opponent(self.player)

    def distribute_items(self):
        """Распределение предметов между игроком и дилером"""
        if self.weapon.is_gun_reloaded:
            item_count = random.randint(MIN_ITEMS, MAX_ITEMS)
            max_items = self.level_info["max_items"]
            self.player.items.distribute_items(item_count, max_items)
            self.dealer.items.distribute_items(item_count, max_items)

    def next_level(self):
        """Переход на следующий уровень"""
        if self.level < len(LEVELS_INFO):
            self.level += 1
            self._setup_level()
        else:
            self.game_active = False

    def get_status(self):
        """Получение статуса уровня"""
        return (
            f"Раунд: {self.level}\n"
            f"Жизни игрока: {self.player.lives}\n"
            f"Жизни Дилера: {self.dealer.lives}\n"
            f"Количество патронов: {len(self.weapon.bullets)}\n"
        )

    def get_reload_status(self):
        """Получение статуса после перезарядки"""
        message = self.weapon.reload_message()
        player_items_message = self.player.items.get_current_items_message()
        dealer_items_message = self.dealer.items.get_current_items_message()

        if player_items_message:
            message += f"Игрок получает: {player_items_message}\n"

        if dealer_items_message:
            message += f"Дилер получает: {dealer_items_message}"

        return message

    def process_shoot(self, shooter, target):
        """Обработка выстрела"""
        last_bullet = shooter.shoot(target)
        self.distribute_items()
        self.game_status = self._update_game_status(target, last_bullet)
        self.handcuff_status = self._handle_handcuffs()

    def _update_game_status(self, target: Player, is_live_bullet: bool) -> GameStatus:
        """Обновление статуса игры."""
        if self.player.lives <= 0:
            return GameStatus.LOSS
        if self.dealer.lives <= 0:
            self.next_level()
            if not self.game_active:
                return GameStatus.WIN
            return GameStatus.LEVEL_UP
        if is_live_bullet:
            if target == self.player:
                return GameStatus.PLAYER_HIT
            else:
                return GameStatus.DEALER_HIT

        return GameStatus.NO_DAMAGE

    def _handle_handcuffs(self) -> HandcuffResult:
        """Проверка и обработка наручников"""
        if self.player.is_turn_now and self.player.apply_handcuffs():
            return HandcuffResult.PLAYER_HANDCUFFED
        elif self.dealer.is_turn_now and self.dealer.apply_handcuffs():
            return HandcuffResult.DEALER_HANDCUFFED
        elif self.dealer.is_turn_now:
            return HandcuffResult.DEALER_TURN

    def dealer_turn(self):
        """Действия дилера"""
        self.dealer.dealer_actions()
        self.process_shoot(self.dealer, self.dealer.target)
        return self.dealer.target, self.dealer.used_item

    def get_game_status(self):
        """Получение текущего статуса игры"""
        return {
            "player_health": self.player.health_bar,
            "dealer_health": self.dealer.health_bar,
            "player_items": self.player.items.get_current_items_message(),
            "dealer_items": self.dealer.items.get_current_items_message()
        }
