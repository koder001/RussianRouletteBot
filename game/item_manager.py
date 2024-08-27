import random
from enum import Enum


class Item(Enum):
    """Перечисление предметов, которые могут быть использованы в игре."""
    SAW = "🪚"
    DISCARD = "🚮"
    MEDKIT = "💉"
    MAGNIFYING_GLASS = "🔍"
    HANDCUFFS = "🔒"


class ItemManager:
    """Класс для управления предметами игрока и дилера."""

    def __init__(self):
        self.items = {item: 0 for item in Item}
        self.item_weights = {
            Item.SAW: 3,
            Item.DISCARD: 4,
            Item.MEDKIT: 4,
            Item.MAGNIFYING_GLASS: 3,
            Item.HANDCUFFS: 1
        }

    def distribute_items(self, item_count, max_items) -> None:
        """Распределение предметов среди участников."""
        self.current_items = {item: 0 for item in Item}

        weighted_items = [item
                          for item, weight in self.item_weights.items()
                          for _ in range(weight)]

        for _ in range(min(item_count, max_items - sum(self.items.values()))):
            item = random.choice(weighted_items)
            self.current_items[item] += 1
            self.items[item] += 1

    def get_current_items_message(self) -> str:
        """Получение информации о текущих предметах игрока или дилера."""
        items_message = []
        for item, count in self.current_items.items():
            if count > 0:
                items_message.append(f'{item.value} ({count})')
        return ', '.join(items_message)
