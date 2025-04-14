import json
from typing import List, Optional
from datetime import datetime
from customer import Customer
from room import Room
from card import Card
from stay import Stay
from item_service import ItemService
from service_provider import ServiceProvider

class Admin:
    DATA_FILE = "hotel_data.json"

    def __init__(self, name: str):
        self.name = name
        self.customers: List[Customer] = []
        self.rooms: List[Room] = []
        self.reservations = {}
        self.service_providers = {}
        self.cards: List[Card] = []
        self.room_services = {}
        self.room_pending_services = {}

    def save_to_file(self):
        data = self.to_dict()
        with open(self.DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    @classmethod
    def load_from_file(cls, name: str):
        try:
            with open(cls.DATA_FILE, 'r') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except FileNotFoundError:
            return cls(name)

    def to_dict(self):
        return {
            "name": self.name,
            "customers": [customer.to_dict() for customer in self.customers],
            "rooms": [room.to_dict() for room in self.rooms],
            "reservations": {cid: stay.to_dict() for cid, stay in self.reservations.items()},
            "service_providers": {name: provider.to_dict() for name, provider in self.service_providers.items()},
            "cards": [card.to_dict() for card in self.cards],
            "room_services": {room_number: [item.to_dict() for item in items] 
                             for room_number, items in self.room_services.items()},
            "room_pending_services": {room_number: [item.to_dict() for item in items] 
                                     for room_number, items in self.room_pending_services.items()}
        }

    @classmethod
    def from_dict(cls, data):
        admin = cls(data["name"])
        admin.rooms = [Room.from_dict(r) for r in data["rooms"]]
        room_map = {room.room_number: room for room in admin.rooms}
        admin.cards = [Card.from_dict(card, room_map) for card in data["cards"]]
        card_map = {card.card_id: card for card in admin.cards}
        admin.customers = [Customer.from_dict(c, room_map, card_map) for c in data["customers"]]
        admin.reservations = {
            cid: Stay.from_dict(stay_data, admin.customers, room_map)
            for cid, stay_data in data["reservations"].items()
        }
        for customer in admin.customers:
            customer.stay = admin.reservations.get(customer.customer_id)
        admin.service_providers = {name: ServiceProvider.from_dict(provider) 
                                  for name, provider in data["service_providers"].items()}
        admin.room_services = {
            room_number: [ItemService.from_dict(item) for item in items]
            for room_number, items in data.get("room_services", {}).items()
        }
        admin.room_pending_services = {
            room_number: [ItemService.from_dict(item) for item in items]
            for room_number, items in data.get("room_pending_services", {}).items()
        }
        return admin

    def add_service_provider(self, provider):
        self.service_providers[provider.name] = provider
        self.save_to_file()

    def get_service_provider(self, name: str):
        return self.service_providers.get(name)

    def add_room(self, room: Room):
        self.rooms.append(room)
        if room.room_number not in self.room_services:
            self.room_services[room.room_number] = []
        if room.room_number not in self.room_pending_services:
            self.room_pending_services[room.room_number] = []
        self.save_to_file()

    def add_customer(self, customer: Customer):
        self.customers.append(customer)
        self.save_to_file()

    def add_reservation(self, customer_id: str, room: Room, length: int):
        customer = next((c for c in self.customers if c.customer_id == customer_id), None)
        if not customer:
            return False
        stay = Stay(customer, room, datetime.now(), length)
        stay.is_active = False
        self.reservations[customer_id] = stay
        customer.assign_stay(stay)
        self.save_to_file()
        return True

    def update_reservation(self, customer_id: str, room: Room = None, length: int = None):
        if customer_id not in self.reservations or not self.reservations[customer_id]:
            return False
        stay = self.reservations[customer_id]
        if stay.is_active:
            return False
        if room:
            stay.room = room
        if length is not None:
            stay.length = length
        self.reservations[customer_id] = stay
        stay.customer.assign_stay(stay)
        self.save_to_file()
        return True

    def delete_reservation(self, customer_id: str):
        if customer_id not in self.reservations or not self.reservations[customer_id]:
            return False
        stay = self.reservations[customer_id]
        if stay.is_active:
            return False
        del self.reservations[customer_id]
        customer = next((c for c in self.customers if c.customer_id == customer_id), None)
        if customer:
            customer.stay = None
        self.save_to_file()
        return True

    def check_in(self, customer_id: str, payment_done: bool = False) -> bool:
        customer = next((c for c in self.customers if c.customer_id == customer_id), None)
        if not customer:
            print(f"Customer with ID {customer_id} not found.")
            return False

        if customer_id not in self.reservations or not self.reservations[customer_id]:
            print(f"Reservation for customer {customer_id} not found.")
            return False

        if not payment_done:
            print(f"Customer {customer.name} needs to pay for the reservation.")
            return False

        stay = self.reservations[customer_id]
        if stay.is_active:
            print(f"Customer {customer.name} is already checked in.")
            return False

        room = stay.room
        for c in self.customers:
            if c.stay and c.stay.room == room and c.stay.is_active:
                print(f"Room {room.room_number} is already occupied by another customer.")
                return False

        card = Card(card_id=f"CARD-{customer_id}", room=room)
        card.activate()
        customer.assign_card(card)
        self.cards.append(card)

        stay.is_active = True
        customer.assign_stay(stay)
        self.reservations[customer_id] = stay

        print(f"Customer {customer.name} successfully checked in to {room} and received {card}.")
        self.save_to_file()
        return True

    def check_out(self, customer_id: str) -> (bool, str):
        customer = next((c for c in self.customers if c.customer_id == customer_id), None)
        if not customer or not customer.stay or not customer.stay.is_active:
            return False, f"Customer {customer_id} is not checked in or has no active stay."

        # Check if there is at least one active card associated with the customer's room
        room = customer.stay.room
        room_cards = [card for card in self.cards if card.room == room and card.is_active]
        if not room_cards:
            return False, f"No active cards available for Room {room.room_number}. Cannot check out."

        room_number = customer.stay.room.room_number
        charges = sum(item.price for item in self.room_services.get(room_number, []))
        if charges > 0:
            print(f"Customer {customer.name} incurred additional charges: ${charges}")
            print(f"Customer {customer.name} paid additional charges: ${charges}")

        # Deactivate and remove all cards associated with the room
        all_room_cards = [card for card in self.cards if card.room == room]  # Get all cards for the room (active or not)
        for card in all_room_cards:
            card.deactivate()
            self.cards.remove(card)

        # Clear the customer's assigned card reference (if it exists)
        customer.card = None

        check_in_time = customer.stay.start_date
        check_out_time = datetime.now()
        customer.stay.end_stay(check_out_time)

        if customer_id in self.reservations:
            del self.reservations[customer_id]

        self.room_services[room_number] = []
        self.room_pending_services[room_number] = []

        message = (f"Customer {customer.name} (ID: {customer_id}) checked in at {check_in_time} "
                f"and checked out at {check_out_time}.")
        print(message)
        self.save_to_file()
        return True, message

    def add_service_to_room(self, room_number: str, service_name: str):
        room = next((r for r in self.rooms if r.room_number == room_number), None)
        if not room:
            print(f"Room {room_number} not found.")
            return False

        hotel_provider = self.get_service_provider("Hotel")
        room_support_provider = self.get_service_provider("RoomSupport")
        service_item = None
        if hotel_provider:
            service_item = next((item for item in hotel_provider.items if item.name == service_name), None)
        if not service_item and room_support_provider:
            service_item = next((item for item in room_support_provider.items if item.name == service_name), None)

        if not service_item:
            print(f"Service '{service_name}' not found in available services.")
            return False

        try:
            if room_number not in self.room_services:
                self.room_services[room_number] = []
            self.room_services[room_number].append(service_item)
            print(f"Service '{service_name}' added to Room {room.room_number}.")
            self.save_to_file()
            return True
        except Exception as e:
            print(f"Error adding service: {e}")
            return False

    def generate_customer_service_record(self, customer_id: str) -> Optional[str]:
        customer = next((c for c in self.customers if c.customer_id == customer_id), None)
        if not customer or not customer.stay:
            return f"Customer with ID {customer_id} has no active stay."

        room_number = customer.stay.room.room_number
        service_record = self.room_services.get(room_number, [])
        if not service_record:
            return f"No services used in Room {room_number} during the stay of Customer {customer.name}."

        report = f"--- Service Record for Customer {customer.name} (ID: {customer.customer_id}) ---\n"
        report += f"Room: {room_number}\n"
        for item in service_record:
            report += f"- {item.name}: ${item.price}\n"
        report += f"-------------------------------------------------------------------\n"
        report += f"Total Service Charges: ${sum(item.price for item in service_record)}\n"
        return report

    def get_room_occupancy_details(self) -> str:
        report = "--- Room Occupancy Status ---\n"
        for room in self.rooms:
            customer = next((c for c in self.customers if c.stay and c.stay.room == room and c.stay.is_active), None)
            cards = [card for card in self.cards if card.room == room]

            customer_info = "Vacant"
            if customer:
                customer_info = f"Occupied by Customer: {customer.name} (ID: {customer.customer_id})"

            report += f"Room: {room.room_number}, Status: {customer_info}\n"
            report += "  Cards:\n"
            if not cards:
                report += "    - None\n"
            else:
                for card in cards:
                    assigned_to = "Unassigned"
                    for cust in self.customers:
                        if cust.card == card:
                            assigned_to = f"Assigned to: {cust.name}"
                            break
                    report += f"    - Card ID: {card.card_id}, Active: {card.is_active}, {assigned_to}\n"
            pending = self.room_pending_services.get(room.room_number, [])
            report += f"  Pending Services: {', '.join([s.name for s in pending]) or 'None'}\n"
        report += "-----------------------------\n"
        return report

    def get_cards_for_room(self, room_number: str) -> List[Card]:
        room = next((r for r in self.rooms if r.room_number == room_number), None)
        if not room:
            return []
        return [card for card in self.cards if card.room == room]

    def add_card_to_room(self, room_number: str, card_id: str) -> Optional[Card]:
        room = next((r for r in self.rooms if r.room_number == room_number), None)
        if not room:
            print(f"Room {room_number} not found.")
            return None
        new_card = Card(card_id=card_id, room=room)
        self.cards.append(new_card)
        print(f"Card {card_id} added to Room {room_number}.")
        self.save_to_file()
        return new_card

    def delete_card(self, card_id: str) -> bool:
        card_to_delete = next((card for card in self.cards if card.card_id == card_id), None)
        if card_to_delete:
            for customer in self.customers:
                if customer.card == card_to_delete:
                    customer.card = None
                    break
            self.cards.remove(card_to_delete)
            print(f"Card {card_id} deleted.")
            self.save_to_file()
            return True
        print(f"Card with ID {card_id} not found.")
        return False

    def activate_card(self, card_id: str) -> bool:
        card = next((c for c in self.cards if c.card_id == card_id), None)
        if card:
            card.activate()
            print(f"Card {card_id} activated for Room {card.room.room_number}.")
            self.save_to_file()
            return True
        print(f"Card with ID {card_id} not found.")
        return False

    def deactivate_card(self, card_id: str) -> bool:
        card = next((c for c in self.cards if c.card_id == card_id), None)
        if card:
            card.deactivate()
            print(f"Card {card_id} deactivated for Room {card.room.room_number}.")
            self.save_to_file()
            return True
        print(f"Card with ID {card_id} not found.")
        return False

    def request_service(self, room_number: str, service_name: str) -> (bool, str):
        room = next((r for r in self.rooms if r.room_number == room_number), None)
        if not room:
            return False, f"Room {room_number} not found."

        customer = next((c for c in self.customers if c.stay and c.stay.room == room and c.stay.is_active), None)
        if not customer:
            return False, f"Room {room_number} is not occupied."

        # Search for the service across all providers
        service_item = None
        provider_name = None
        for name, provider in self.service_providers.items():
            item = next((item for item in provider.items if item.name == service_name), None)
            if item:
                service_item = ItemService(item.name, item.price, name)  # Create a new instance with provider_name
                provider_name = name
                break

        if not service_item:
            return False, f"Service '{service_name}' not found in any provider."

        if room_number not in self.room_pending_services:
            self.room_pending_services[room_number] = []
        self.room_pending_services[room_number].append(service_item)
        self.save_to_file()
        return True, f"Service '{service_name}' requested for Room {room_number} by {provider_name}."

    def complete_service(self, room_number: str, service_name: str, user_role: str, completion_details: str = None) -> (bool, str):
        provider_name = "Hotel" if user_role == "service_provider_a" else "RoomSupport"
        room = next((r for r in self.rooms if r.room_number == room_number), None)
        if not room:
            return False, f"Room {room_number} not found."
        pending_services = self.room_pending_services.get(room_number, [])
        pending_service = next((s for s in pending_services if s.name == service_name and not s.completed), None)
        if not pending_service:
            return False, "Pending service not found."
        if pending_service.provider_name != provider_name:
            return False, f"Service '{service_name}' is not managed by {provider_name}."
        
        # Mark the service as completed
        pending_service.mark_completed()
        pending_services.remove(pending_service)
        self.room_pending_services[room_number] = pending_services
        if room_number not in self.room_services:
            self.room_services[room_number] = []
        self.room_services[room_number].append(pending_service)

        # Log completion details to a text file if provided
        if completion_details:
            log_entry = f"[{datetime.now()}] Room {room_number} - Service '{service_name}' completed by {provider_name}. Details: {completion_details}\n"
            try:
                with open("service_completion_log.txt", "a") as log_file:
                    log_file.write(log_entry)
            except Exception as e:
                print(f"Error writing to service completion log: {e}")

        self.save_to_file()
        return True, f"Service '{service_name}' completed for Room {room_number}."

    def get_pending_services(self, user_role: str) -> List[tuple]:
        provider_name = "Hotel" if user_role == "service_provider_a" else "RoomSupport"
        pending = []
        for room_number, services in self.room_pending_services.items():
            for service in services:
                if not service.completed and service.provider_name == provider_name:
                    pending.append((room_number, service.name))
        return pending