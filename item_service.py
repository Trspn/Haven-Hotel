class ItemService:
    def __init__(self, name: str, price: float, provider_name: str = None):
        self.name = name
        self.price = price
        self.completed = False
        self.provider_name = provider_name  # Track which provider offers this service

    def mark_completed(self):
        self.completed = True

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "completed": self.completed,
            "provider_name": self.provider_name
        }

    @classmethod
    def from_dict(cls, data):
        item = cls(data["name"], data["price"], data.get("provider_name"))
        item.completed = data["completed"]
        return item