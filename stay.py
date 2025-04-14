from datetime import datetime
from typing import Optional

class Stay:
    def __init__(self, customer: 'Customer', room: 'Room', start_date: datetime, length: int):
        self.customer = customer
        self.room = room
        self.start_date = start_date
        self.length = length
        self.end_date: Optional[datetime] = None
        self.is_active = False

    def end_stay(self, end_date: datetime):
        self.end_date = end_date
        self.is_active = False

    def __str__(self):
        return f"Stay for {self.customer.name} in {self.room} from {self.start_date} for {self.length} days"

    def to_dict(self):
        return {
            "customer_id": self.customer.customer_id,
            "room": self.room.to_dict(),
            "start_date": self.start_date.isoformat(),
            "length": self.length,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "is_active": self.is_active
        }

    @classmethod
    def from_dict(cls, data, customers, room_map):
        customer = next((c for c in customers if c.customer_id == data["customer_id"]), None)
        if not customer:
            raise ValueError(f"Customer with ID {data['customer_id']} not found during deserialization")
        room_number = data["room"]["room_number"]
        room = room_map.get(room_number)
        if not room:
            raise ValueError(f"Room with number {room_number} not found in room_map during deserialization")
        start_date = datetime.fromisoformat(data["start_date"])
        stay = cls(customer, room, start_date, data["length"])
        stay.is_active = data["is_active"]
        if data["end_date"]:
            stay.end_date = datetime.fromisoformat(data["end_date"])
        return stay