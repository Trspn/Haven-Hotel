class ServiceProvider:
    def __init__(self, name: str):
        self.name = name
        self.items = []

    def add_item(self, item: 'ItemService'):
        item.provider_name = self.name  # Set the provider_name on the item
        self.items.append(item)

    def to_dict(self):
        return {
            "name": self.name,
            "items": [item.to_dict() for item in self.items]
        }

    @classmethod
    def from_dict(cls, data):
        provider = cls(data["name"])
        from item_service import ItemService
        provider.items = [ItemService.from_dict(item) for item in data["items"]]
        return provider