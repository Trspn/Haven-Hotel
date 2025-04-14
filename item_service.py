class ItemService:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price
        self.completed = False

    def mark_completed(self):
        self.completed = True

    def __str__(self):
        return f"{self.name} (${self.price})"