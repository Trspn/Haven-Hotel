from datetime import datetime
from typing import Optional, List
from item_service import ItemService

class Stay:
    def __init__(self, customer: 'Customer', room: 'Room', start_date: datetime, length: int):
        self.customer = customer
        self.room = room
        self.start_date = start_date
        self.length = length  # New attribute for stay duration in days/nights
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