class Room:
    def __init__(self, room_number: str):
        self.room_number = room_number

    def __str__(self):
        return f"Room {self.room_number}"

    def __eq__(self, other):
        if not isinstance(other, Room):
            return False
        return self.room_number == other.room_number

    def to_dict(self):
        return {"room_number": self.room_number}

    @classmethod
    def from_dict(cls, data):
        return cls(data["room_number"])