from typing import List, Optional
from datetime import datetime
from customer import Customer
from room import Room
from card import Card
from stay import Stay
from item_service import ItemService
from service_provider import ServiceProvider

class Admin:
    def __init__(self, name: str):
        self.name = name
        self.customers: List[Customer] = []
        self.rooms: List[Room] = []
        self.reservations = {}
        self.service_providers = {}
        self.cards: List[Card] = []

    def add_service_provider(self, provider):
        self.service_providers[provider.name] = provider

    def get_service_provider(self, name: str):
        return self.service_providers.get(name)

    def add_room(self, room: Room):
        self.rooms.append(room)

    def add_customer(self, customer: Customer):
        self.customers.append(customer)

    def add_reservation(self, customer_id: str, room: Room, length: int):
        customer = next((c for c in self.customers if c.customer_id == customer_id), None)
        if not customer:
            return False
        stay = Stay(customer, room, datetime.now(), length)
        stay.is_active = False
        self.reservations[customer_id] = stay
        customer.assign_stay(stay)
        return True

    def update_reservation(self, customer_id: str, room: Room = None, length: int = None):
        if customer_id not in self.reservations or not self.reservations[customer_id]:
            return False
        stay = self.reservations[customer_id]
        if stay.is_active:
            return False  # Cannot update an active (checked-in) stay
        if room:
            stay.room = room
        if length is not None:
            stay.length = length
        self.reservations[customer_id] = stay
        stay.customer.assign_stay(stay)
        return True

    def delete_reservation(self, customer_id: str):
        if customer_id not in self.reservations or not self.reservations[customer_id]:
            return False
        stay = self.reservations[customer_id]
        if stay.is_active:
            return False  # Cannot delete an active (checked-in) stay
        del self.reservations[customer_id]
        customer = next((c for c in self.customers if c.customer_id == customer_id), None)
        if customer:
            customer.stay = None
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
        card = Card(card_id=f"CARD-{customer_id}", room=room)
        card.activate()
        customer.assign_card(card)
        self.cards.append(card)

        stay.is_active = True
        customer.assign_stay(stay)
        self.reservations[customer_id] = stay

        print(f"Customer {customer.name} successfully checked in to {room} and received {card}.")
        return True

    def check_out(self, customer_id: str) -> (bool, str):
        customer = next((c for c in self.customers if c.customer_id == customer_id), None)
        if not customer or not customer.stay or not customer.stay.is_active:
            return False, f"Customer {customer_id} is not checked in or has no active stay."

        if not customer.card:
            return False, f"Customer {customer.name} has no card to return."

        if not customer.card.is_active:
            return False, f"Card for {customer.name} is not active."

        charges = customer.stay.get_service_charges()
        if charges > 0:
            print(f"Customer {customer.name} incurred additional charges: ${charges}")
            print(f"Customer {customer.name} paid additional charges: ${charges}")

        # Remove the card from the system
        self.cards.remove(customer.card)
        customer.card.deactivate()
        customer.card = None

        # End the stay and record the check-out time
        check_in_time = customer.stay.start_date
        check_out_time = datetime.now()
        customer.stay.end_stay(check_out_time)

        # Remove the reservation from the list
        if customer_id in self.reservations:
            del self.reservations[customer_id]

        message = (f"Customer {customer.name} (ID: {customer_id}) checked in at {check_in_time} "
                   f"and checked out at {check_out_time}.")
        print(message)
        return True, message

    def add_service_to_room(self, customer_id: str, service_name: str):
        customer = next((c for c in self.customers if c.customer_id == customer_id), None)
        if not customer or not customer.stay or not customer.stay.is_active:
            print(f"Customer {customer_id} is not checked in or has no active stay.")
            return False

        hotel_provider = self.get_service_provider("Hotel")
        if not hotel_provider:
            print("Hotel service provider not found.")
            return False

        service_item = next((item for item in hotel_provider.items if item.name == service_name), None)
        if not service_item:
            print(f"Service '{service_name}' not found in Hotel services.")
            return False

        try:
            customer.stay.add_service(service_item)
            print(f"Service '{service_name}' added to stay for Customer {customer.name} in Room {customer.stay.room.room_number}.")
            return True
        except Exception as e:
            print(f"Error adding service: {e}")
            return False

    def generate_customer_service_record(self, customer_id: str) -> Optional[str]:
        customer = next((c for c in self.customers if c.customer_id == customer_id), None)
        if not customer or not customer.stay:
            return f"Customer with ID {customer_id} has no active stay."

        service_record = customer.stay.service_record
        if not service_record:
            return f"No services used by Customer {customer.name} during their stay in Room {customer.stay.room.room_number}."

        report = f"--- Service Record for Customer {customer.name} (ID: {customer.customer_id}) ---\n"
        report += f"Room: {customer.stay.room.room_number}\n"
        for item in service_record:
            report += f"- {item.name}: ${item.price}\n"
        report += f"-------------------------------------------------------------------\n"
        report += f"Total Service Charges: ${customer.stay.get_service_charges()}\n"
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
            return True
        print(f"Card with ID {card_id} not found.")
        return False

    def activate_card(self, card_id: str) -> bool:
        card = next((c for c in self.cards if c.card_id == card_id), None)
        if card:
            card.activate()
            print(f"Card {card_id} activated for Room {card.room.room_number}.")
            return True
        print(f"Card with ID {card_id} not found.")
        return False

    def deactivate_card(self, card_id: str) -> bool:
        card = next((c for c in self.cards if c.card_id == card_id), None)
        if card:
            card.deactivate()
            print(f"Card {card_id} deactivated for Room {card.room.room_number}.")
            return True
        print(f"Card with ID {card_id} not found.")
        return False

    def request_service(self, customer_id: str, service_name: str) -> (bool, str):
        customer = next((c for c in self.customers if c.customer_id == customer_id), None)
        if not customer or not customer.stay or not customer.stay.is_active:
            return False, "Customer not found or not checked in."
        provider = self.get_service_provider("Hotel")
        if not provider:
            return False, "Service provider not found."
        item = next((item for item in provider.items if item.name == service_name), None)
        if not item:
            return False, "Service not found."
        customer.stay.pending_services.append(item)
        return True, f"Service '{service_name}' requested for customer {customer_id}."

    def complete_service(self, customer_id: str, service_name: str) -> (bool, str):
        customer = next((c for c in self.customers if c.customer_id == customer_id), None)
        if not customer or not customer.stay or not customer.stay.is_active:
            return False, "Customer not found or not checked in."
        pending_service = next((s for s in customer.stay.pending_services if s.name == service_name and not s.completed), None)
        if not pending_service:
            return False, "Pending service not found."
        pending_service.mark_completed()
        customer.stay.pending_services.remove(pending_service)
        customer.stay.add_service(pending_service)
        return True, f"Service '{service_name}' completed for customer {customer_id}."

    def get_pending_services(self) -> List[tuple]:
        pending = []
        for customer in self.customers:
            if customer.stay and customer.stay.is_active:
                for service in customer.stay.pending_services:
                    if not service.completed:
                        pending.append((customer.customer_id, service.name))
        return pending