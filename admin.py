from typing import List, Optional
from datetime import datetime
from customer import Customer
from room import Room
from card import Card
from stay import Stay
from item_service import ItemService

class Admin:
    def __init__(self, name: str):
        self.name = name
        self.customers: List[Customer] = []
        self.rooms: List[Room] = []
        self.reservations = {}
        self.service_providers = {} # To store service providers
        self.cards: List[Card] = [] # Keep track of all cards

    def add_service_provider(self, provider):
        self.service_providers[provider.name] = provider

    def get_service_provider(self, name: str):
        return self.service_providers.get(name)

    def add_room(self, room: Room):
        self.rooms.append(room)

    def add_customer(self, customer: Customer):
        self.customers.append(customer)

    def check_in(self, customer_id: str, room_number: str, payment_done: bool = False) -> bool:
        customer = next((c for c in self.customers if c.customer_id == customer_id), None)
        if not customer:
            print(f"Customer with ID {customer_id} not found.")
            return False

        if customer_id not in self.reservations:
            print(f"Reservation for customer {customer_id} not found.")
            return False

        if not payment_done:
            print(f"Customer {customer.name} needs to pay for the reservation.")
            payment_done = True

        if not payment_done:
            print("Payment not completed. Check-in failed.")
            return False

        room = next((r for r in self.rooms if r.room_number == room_number), None)
        if not room:
            print(f"Room {room_number} not found.")
            return False

        card = Card(card_id=f"CARD-{customer_id}", room=room)
        card.activate()
        customer.assign_card(card)
        self.cards.append(card) # Track the new card

        stay = Stay(customer, room, datetime.now())
        customer.assign_stay(stay)
        self.reservations[customer_id] = stay

        print(f"Customer {customer.name} successfully checked in to {room} and received {card}.")
        return True

    def check_out(self, customer_id: str) -> bool:
        customer = next((c for c in self.customers if c.customer_id == customer_id), None)
        if not customer or not customer.stay or not customer.stay.is_active:
            print(f"Customer {customer_id} is not checked in or has no active stay.")
            return False

        if not customer.card:
            print(f"Customer {customer.name} has no card to return.")
            return False

        if not customer.card.is_active:
            print(f"Card for {customer.name} is not active.")
            return False

        charges = customer.stay.room.get_service_charges()
        if charges > 0:
            print(f"Customer {customer.name} incurred additional charges: ${charges}")
            print(f"Customer {customer.name} paid additional charges: ${charges}")

        customer.card.deactivate()
        customer.stay.end_stay(datetime.now())
        print(f"Customer {customer.name} stay ended at {customer.stay.end_date}.")
        print(f"Customer {customer.name} successfully checked out.")
        return True

    def add_reservation(self, customer_id: str):
        self.reservations[customer_id] = None

    def add_service_to_room(self, customer_id: str, service_name: str):
        customer = next((c for c in self.customers if c.customer_id == customer_id), None)
        if not customer or not customer.stay or not customer.stay.is_active or not customer.stay.room:
            print(f"Customer {customer_id} is not checked in or has no active stay with a room.")
            return False

        room = customer.stay.room
        hotel_provider = self.get_service_provider("Hotel")
        if not hotel_provider:
            print("Hotel service provider not found.")
            return False

        service_item = next((item for item in hotel_provider.items if item.name == service_name), None)
        if not service_item:
            print(f"Service '{service_name}' not found in Hotel services.")
            return False

        try:
            room.add_service(service_item, customer)
            print(f"Service '{service_name}' added to Room {room.room_number} for Customer {customer.name}.")
            return True
        except ValueError as e:
            print(f"Error adding service: {e}")
            return False

    def generate_customer_service_record(self, customer_id: str) -> Optional[str]:
        customer = next((c for c in self.customers if c.customer_id == customer_id), None)
        if not customer or not customer.stay or not customer.stay.room:
            return f"Customer with ID {customer_id} is not checked in or has no active stay."

        service_record = customer.stay.room.service_record
        if not service_record:
            return f"No services used by Customer {customer.name} in Room {customer.stay.room.room_number}."

        report = f"--- Service Record for Customer {customer.name} (ID: {customer.customer_id}) ---\n"
        report += f"Room: {customer.stay.room.room_number}\n"
        for item in service_record:
            report += f"- {item.name}: ${item.price}\n"
        report += f"-------------------------------------------------------------------\n"
        report += f"Total Service Charges: ${customer.stay.room.get_service_charges()}\n"
        return report

    def get_room_occupancy_details(self) -> str:
        report = "--- Room Occupancy Status ---\n"
        for room in self.rooms:
            customer = next((c for c in self.customers if c.stay and c.stay.room == room and c.stay.is_active), None)
            card_info = "No card assigned"
            if customer and customer.card:
                card_info = f"Card ID: {customer.card.card_id}, Active: {customer.card.is_active}"

            customer_info = "Vacant"
            if customer:
                customer_info = f"Customer: {customer.name} (ID: {customer.customer_id})"

            report += f"Room: {room.room_number}, Status: {customer_info}, {card_info}\n"
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
            # Also need to disassociate it from the customer if it's assigned
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