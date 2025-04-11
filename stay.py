from datetime import datetime
from typing import Optional

class Stay:
    def __init__(self, customer: 'Customer', room: 'Room', start_date: datetime):  # Use string type hints
        self.customer = customer
        self.room = room
        self.start_date = start_date
        self.end_date: Optional[datetime] = None
        self.is_active = True

    def end_stay(self, end_date: datetime):
        self.end_date = end_date
        self.is_active = False

    def __str__(self):
        return f"Stay for {self.customer.name} in {self.room} from {self.start_date}"