import random
from typing import NamedTuple
from game.settings import (MAGAZINE_MIN_SIZE, MAGAZINE_MAX_SIZE,
                           DAMAGE_NORMAL, DAMAGE_BOOSTED)


class BulletAnalysis(NamedTuple):
    analysis_successful: bool
    is_live_bullet: bool


class Weapon:
    """Класс для управления оружием, включая патроны и их типы."""

    def __init__(self):
        self.is_damage_boosted = False
        self.last_bullet_type = None
        self._reload_gun()

    def _reload_gun(self) -> None:
        """Перезарядка оружия: генерация новых патронов и перемешивание."""
        self.magazine_size = random.randint(MAGAZINE_MIN_SIZE, MAGAZINE_MAX_SIZE)
        self.dummy_bullets = random.randint(1, self.magazine_size - 1)
        self.live_bullets = self.magazine_size - self.dummy_bullets
        self.bullets = [False] * self.dummy_bullets + [True] * self.live_bullets
        random.shuffle(self.bullets)
        self.is_gun_reloaded = True

    def pop_last_bullet(self) -> bool:
        """Выдача последнего патрона. Перезарядка при необходимости."""
        bullet = self.bullets.pop()
        self.last_bullet_type = ['холостой', 'боевой'][bullet]
        if not self.bullets:
            self._reload_gun()
        return bullet

    def analyze_bullets(self) -> BulletAnalysis:
        """Анализ патронов в оружии."""

        # Все пули холостые
        if not any(self.bullets):
            return BulletAnalysis(True, False)

        # Все пули боевые
        if all(self.bullets):
            return BulletAnalysis(True, True)

        # Анализ не удался
        return BulletAnalysis(False, None)

    def damage_bullet(self) -> int:
        """Возвращение урона в зависимости от усиления пули."""
        damage = DAMAGE_BOOSTED if self.is_damage_boosted else DAMAGE_NORMAL
        self.is_damage_boosted = False
        return damage

    def damage_boosted(self) -> None:
        """Усиление пули для следующего выстрела."""
        self.is_damage_boosted = True

    def last_bullet(self) -> bool:
        """Получение информации о последнем патроне."""
        self.last_bullet_type = ['холостой', 'боевой'][self.bullets[-1]]
        return self.bullets[-1]

    def reload_message(self) -> str:
        """Сообщение о состоянии перезарядки оружия."""
        self.is_gun_reloaded = False
        return (
            f"Перезарядка! 🔄\n"
            f"Боевых патронов: {self.live_bullets}\n"
            f"Холостых патронов: {self.dummy_bullets}\n"
        )
