class Card:
    def __init__(self, card_id: str, room: 'Room'):
        self.card_id = card_id
        self.room = room
        self.is_active = False

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def __str__(self):
        return f"Card {self.card_id} for {self.room}"

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.card_id == other.card_id

    def to_dict(self):
        return {
            "card_id": self.card_id,
            "room": self.room.to_dict(),
            "is_active": self.is_active
        }

    @classmethod
    def from_dict(cls, data, room_map):
        room_data = data["room"]
        room_number = room_data["room_number"]
        room = room_map.get(room_number)
        if not room:
            raise ValueError(f"Room with number {room_number} not found in room_map during deserialization")
        card = cls(data["card_id"], room)
        card.is_active = data["is_active"]
        return card