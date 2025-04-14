from datetime import datetime
from typing import Optional, List
from item_service import ItemService

class Stay:
    def __init__(self, customer: 'Customer', room: 'Room', start_date: datetime, length: int):
        self.customer = customer
        self.room = room
        self.start_date = start_date
        self.length = length
        self.end_date: Optional[datetime] = None
        self.is_active = False
        self.service_record: List[ItemService] = []
        self.pending_services: List[ItemService] = []

    def end_stay(self, end_date: datetime):
        self.end_date = end_date
        self.is_active = False

    def add_service(self, item: ItemService):
        if item not in self.service_record:
            self.service_record.append(item)

    def get_service_charges(self) -> float:
        return sum(item.price for item in self.service_record)

    def __str__(self):
        return f"Stay for {self.customer.name} in {self.room} from {self.start_date} for {self.length} days"

    def to_dict(self):
        return {
            "customer_id": self.customer.customer_id,
            "room": self.room.to_dict(),
            "start_date": self.start_date.isoformat(),
            "length": self.length,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "is_active": self.is_active,
            "service_record": [item.to_dict() for item in self.service_record],
            "pending_services": [item.to_dict() for item in self.pending_services]
        }

    @classmethod
    def from_dict(cls, data, customers, room_map):
        # Find the customer in the provided customers list using customer_id
        customer = next((c for c in customers if c.customer_id == data["customer_id"]), None)
        if not customer:
            raise ValueError(f"Customer with ID {data['customer_id']} not found during deserialization")
        # Use the room_map to get the existing Room object
        room_data = data["room"]
        room_number = room_data["room_number"]
        room = room_map.get(room_number)
        if not room:
            raise ValueError(f"Room with number {room_number} not found in room_map during deserialization")
        start_date = datetime.fromisoformat(data["start_date"])
        stay = cls(customer, room, start_date, data["length"])
        stay.is_active = data["is_active"]
        if data["end_date"]:
            stay.end_date = datetime.fromisoformat(data["end_date"])
        stay.service_record = [ItemService.from_dict(item) for item in data["service_record"]]
        stay.pending_services = [ItemService.from_dict(item) for item in data["pending_services"]]
        return stay