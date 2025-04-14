from typing import List
from item_service import ItemService

class ServiceProvider:
    def __init__(self, name: str):
        self.name = name
        self.items: List[ItemService] = []

    def add_item(self, item: ItemService):
        self.items.append(item)

    def to_dict(self):
        return {
            "name": self.name,
            "items": [item.to_dict() for item in self.items]
        }

    @classmethod
    def from_dict(cls, data):
        provider = cls(data["name"])
        provider.items = [ItemService.from_dict(item) for item in data["items"]]
        return provider