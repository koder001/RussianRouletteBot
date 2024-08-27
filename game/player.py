from game.weapon import Weapon
from game.item_manager import ItemManager, Item


class Player:
    """Класс, представляющий участника игры (игрока или дилера)."""

    def __init__(self, lives: int, weapon: Weapon):
        self.lives = lives
        self.max_lives = lives
        self.items = ItemManager()
        self.is_turn_now = True
        self.handcuffed = False
        self.weapon = weapon
        self.update_health_display()

    def set_opponent(self, opponent) -> None:
        """Установка оппонента для текущего участника."""
        self.opponent = opponent

    def use_item(self, item: Item) -> bool:
        """Использование предмета участником."""
        if self.items.items[item] > 0:
            self.items.items[item] -= 1

            if item == Item.SAW:
                self.weapon.damage_boosted()
            elif item == Item.DISCARD:
                self.weapon.pop_last_bullet()
            elif item == Item.MEDKIT:
                self.update_lives()
            elif item == Item.MAGNIFYING_GLASS:
                self.weapon.last_bullet()
            elif item == Item.HANDCUFFS:
                self.opponent.put_handcuffs()

            return True
        return False

    def update_lives(self) -> None:
        """Восстановление жизней."""
        self.update_health_display(health=1)
        self.lives = min(self.max_lives, self.lives + 1)

    def update_health_display(self, damage=0, health=0) -> None:
        """Обновление статуса здоровья"""
        health = min(health, self.max_lives - self.lives)
        heart_full = "❤"
        heart_damage = "💔"
        heart_half = "💚"
        heart_empty = "🖤"
        self.health_bar = (
            heart_full * self.lives +
            heart_damage * damage +
            heart_half * health +
            heart_empty * (self.max_lives - self.lives - damage - health)
        )

    def put_handcuffs(self) -> None:
        """Оппонента надел наручники"""
        self.handcuffed = True

    def apply_handcuffs(self) -> None:
        """Пропуск хода из-за наручников."""
        if self.handcuffed:
            self.is_turn_now = False
            self.opponent.is_turn_now = True
            self.handcuffed = False
            return True
        return False

    def shoot(self, target) -> bool:
        """Осуществление выстрела"""
        damage = self.weapon.damage_bullet()
        last_bullet = self.weapon.pop_last_bullet()

        if self != target or last_bullet:
            self.is_turn_now = False
            self.opponent.is_turn_now = True

        if last_bullet:
            target.lives -= damage
            target.update_health_display(damage=damage)

        return last_bullet
