class Card:
    def __init__(self, card_id: str, room: 'Room'):  # Use string type hint
        self.card_id = card_id
        self.room = room
        self.is_active = False

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def __str__(self):
        return f"Card {self.card_id} for {self.room}"