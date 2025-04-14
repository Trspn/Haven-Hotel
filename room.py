class Room:
    def __init__(self, room_number: str):
        self.room_number = room_number
        self.service_record: list['ItemService'] = []
        self.pending_services: list['ItemService'] = []

    def add_service(self, item: 'ItemService'):
        if item not in self.service_record:
            self.service_record.append(item)

    def get_service_charges(self) -> float:
        return sum(item.price for item in self.service_record)

    def __str__(self):
        return f"Room {self.room_number}"

    def __eq__(self, other):
        if not isinstance(other, Room):
            return False
        return self.room_number == other.room_number

    def to_dict(self):
        return {
            "room_number": self.room_number,
            "service_record": [item.to_dict() for item in self.service_record],
            "pending_services": [item.to_dict() for item in self.pending_services]
        }

    @classmethod
    def from_dict(cls, data):
        room = cls(data["room_number"])
        from item_service import ItemService
        room.service_record = [ItemService.from_dict(item) for item in data["service_record"]]
        room.pending_services = [ItemService.from_dict(item) for item in data["pending_services"]]
        return room