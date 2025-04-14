from typing import List
from item_service import ItemService

class Room:
    def __init__(self, room_number: str):
        self.room_number = room_number
        # self.service_record: List[ItemService] = [] # No longer needed here

    # def add_service(self, item: ItemService, customer: 'Customer'):
    #     if not customer.card or not customer.card.is_active:
    #         raise ValueError(f"Cannot add service {item.name}. Card is not active or not assigned.")
    #     self.service_record.append(item)

    # def get_service_charges(self) -> float:
    #     return sum(item.price for item in self.service_record)

    def __str__(self):
        return f"Room {self.room_number}"