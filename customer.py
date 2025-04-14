from stay import Stay
from card import Card

class Customer:
    def __init__(self, name: str, customer_id: str):
        self.name = name
        self.customer_id = customer_id
        self.stay: Stay = None
        self.card: Card = None

    def assign_stay(self, stay: Stay):
        self.stay = stay

    def assign_card(self, card: Card):
        self.card = card

    def to_dict(self):
        return {
            "name": self.name,
            "customer_id": self.customer_id,
            "stay": self.stay.to_dict() if self.stay else None,
            "card": self.card.to_dict() if self.card else None
        }

    @classmethod
    def from_dict(cls, data, room_map=None, card_map=None):
        customer = cls(data["name"], data["customer_id"])
        if data["card"]:
            card_id = data["card"]["card_id"]
            if card_map and card_id in card_map:
                customer.card = card_map[card_id]
            else:
                from card import Card  # Fallback if card_map is not provided or card_id not found
                customer.card = Card.from_dict(data["card"], room_map)
        # Note: `stay` will be assigned later in `admin.py` to avoid circular dependency
        return customer