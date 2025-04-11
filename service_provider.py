from typing import List
from item_service import ItemService

class ServiceProvider:
    def __init__(self, name: str):
        self.name = name
        self.items: List[ItemService] = []

    def add_item(self, item: ItemService):
        self.items.append(item)

    def get_items(self) -> List[ItemService]:
        return self.items

    def __str__(self):
        return f"Service Provider: {self.name}"