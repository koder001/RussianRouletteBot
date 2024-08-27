import random
from game.player import Player
from game.weapon import Weapon, BulletAnalysis
from game.item_manager import Item


class Dealer(Player):
    """Класс, представляющий дилера."""

    def __init__(self, lives: int, weapon: Weapon):
        super().__init__(lives, weapon)
        self.is_turn_now = False
        self.target = None

    def dealer_actions(self) -> None:
        """Логика ходов дилера."""
        self.target = self.opponent
        self.used_item = []

        # Использует аптечку
        self._use_medkit()

        # Анализирует магазин
        result_analyze = self._use_discard()

        if result_analyze.analysis_successful:
            if result_analyze.is_live_bullet:
                # Если патрон боевой, использует предметы
                self._use_handcuffs()
                self._use_saw()
                return

            # Стрельба в себя, если патрон холостой
            self.target = self
            return

        self._select_target_with_randomness()

        # Если целью остался противник, возможно, используем предметы
        if self.target == self.opponent:
            self._use_random_item_on_opponent()

    def _select_target_with_randomness(self) -> None:
        """Выбор цели дилера на основе логики и случайности."""

        risk_factor = 0.3  # 30% шанс на рискованный ход

        # Если осталось больше холостых патронов, то дилер может рискнуть и выстрелить в себя
        if sum(self.weapon.bullets) > sum(self.weapon.bullets)//2 and random.random() < risk_factor:
            self.target = self
        elif self.lives <= 1 and random.random() < risk_factor:
            self.target = self
        else:
            self.target = random.choice([self, self.opponent])

    def _use_random_item_on_opponent(self) -> None:
        """Случайное использование наручников или пилы на противнике."""
        if random.choice([True, False]):
            self._use_handcuffs()
        if random.choice([True, False]):
            self._use_saw()

    def _generate_message(self, item) -> None:
        """Генерация сообщения о действии дилера."""
        messages = {
            Item.HANDCUFFS: "Дилер использовал наручники. Вы пропустите ход.",
            Item.SAW: "Дилер использовал ножовку. Урон от патрона удвоен.",
            Item.DISCARD: f"Дилер выкинул {self.weapon.last_bullet_type} патрон.",
            Item.MEDKIT: f"Дилер: {self.health_bar}",
            Item.MAGNIFYING_GLASS: "Дилер проверил патрон."
        }

        self.used_item.append(messages[item])

    def _use_handcuffs(self) -> None:
        """Использование Дилером наручников."""
        if self.use_item(Item.HANDCUFFS):
            self._generate_message(Item.HANDCUFFS)

    def _use_saw(self) -> None:
        """Использование Дилером ножовки."""
        if self.use_item(Item.SAW):
            self._generate_message(Item.SAW)

    def _use_discard(self) -> BulletAnalysis:
        """Анализ патронов и выброс последнего патрона."""
        if not (result_analyze := self._analyze_bullets()).analysis_successful and self.use_item(Item.DISCARD):
            self._generate_message(Item.DISCARD)
        return result_analyze

    def _use_medkit(self) -> None:
        """Дилер лечится."""
        while self.lives < self.max_lives and self.use_item(Item.MEDKIT):
            self._generate_message(Item.MEDKIT)

    def _analyze_bullets(self) -> BulletAnalysis:
        """Анализ патронов Дилером."""
        result_analyze = self.weapon.analyze_bullets()
        if result_analyze.analysis_successful:
            return result_analyze

        if self.use_item(Item.MAGNIFYING_GLASS):
            self._generate_message(Item.MAGNIFYING_GLASS)
            return BulletAnalysis(True, self.weapon.last_bullet())

        return BulletAnalysis(False, False)