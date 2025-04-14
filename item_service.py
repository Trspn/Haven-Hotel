class ItemService:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price
        self.completed = False

    def mark_completed(self):
        self.completed = True

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "completed": self.completed
        }

    @classmethod
    def from_dict(cls, data):
        item = cls(data["name"], data["price"])
        item.completed = data["completed"]
        return item