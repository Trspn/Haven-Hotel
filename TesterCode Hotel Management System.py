from datetime import datetime
from typing import List, Optional

# Base class for Items/Services
class ItemService:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

    def __str__(self):
        return f"{self.name} (${self.price})"


# Service Providers 
class ServiceProvider:
    def __init__(self, name: str):
        self.name = name
        self.items: List[ItemService] = []

    def add_item(self, item: ItemService):
        self.items.append(item)

    def get_items(self) -> List[ItemService]:
        return self.items


# Room class
class Room:
    def __init__(self, room_number: str):
        self.room_number = room_number
        self.service_record: List[ItemService] = []
        self.cards: List[Card] = []

    def assign_card(self, card: 'Card'):
        self.cards.append(card)

    def clear_card(self, card: 'Card'):
        if card in self.cards:
            self.cards.remove(card)

    def is_occupied(self) -> bool:
        return any(card.is_active for card in self.cards)

    def add_service(self, item: ItemService, customer: 'Customer'):
        if not customer.cards or not any(card.is_active for card in customer.cards):
            raise ValueError(f"Cannot add service {item.name}. No active card assigned.")
        self.service_record.append(item)

    def get_service_charges(self) -> float:
        return sum(item.price for item in self.service_record)

    def __str__(self):
        return f"Room {self.room_number}"


# Card class
class Card:
    def __init__(self, card_id: str, room: Room, stay: 'Stay'):
        self.card_id = card_id
        self.room = room
        self.stay = stay
        self.is_active = False
        self.room.assign_card(self)

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False
        self.room.clear_card(self)

    def __str__(self):
        return f"Card {self.card_id} for {self.room}"


# Stay class
class Stay:
    def __init__(self, customer, room: Room, start_date: datetime):
        self.customer = customer
        self.room = room
        self.start_date = start_date
        self.end_date: Optional[datetime] = None
        self.is_active = True
        self.cards: List[Card] = []

    def add_card(self, card: Card):
        self.cards.append(card)

    def end_stay(self, end_date: datetime):
        self.end_date = end_date
        self.is_active = False
        for card in self.cards:
            card.deactivate()

    def __str__(self):
        return f"Stay for {self.customer.name} in {self.room} from {self.start_date}"


# Customer class 
class Customer:
    def __init__(self, name: str, customer_id: str):
        self.name = name
        self.customer_id = customer_id
        self.cards: List[Card] = []
        self.stay: Optional[Stay] = None

    def assign_card(self, card: Card):
        self.cards.append(card)  
    def assign_stay(self, stay: Stay):
        self.stay = stay

    def clear_stay(self):
        self.stay = None
        self.cards = []

    def __str__(self):
        return f"Customer {self.name} (ID: {self.customer_id})"


# Admin class
class Admin:
    def __init__(self, name: str):
        self.name = name
        self.customers: List[Customer] = []
        self.rooms: List[Room] = []
        self.reservations = {}

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

        if room.is_occupied():
            existing_stay = next((card.stay for card in room.cards if card.is_active), None)
            if existing_stay and (not customer.stay or customer.stay != existing_stay):
                print(f"Room {room_number} is already occupied by another stay.")
                return False

        stay = customer.stay if customer.stay and customer.stay.is_active else Stay(customer, room, datetime.now())
        card = Card(card_id=f"CARD-{customer_id}-{len(room.cards) + 1}", room=room, stay=stay)
        card.activate()
        stay.add_card(card)
        customer.assign_card(card)
        if not customer.stay:
            customer.assign_stay(stay)
        self.reservations[customer_id] = stay

        print(f"Customer {customer.name} successfully checked in to {room} and received {card}.")
        return True

    def check_out(self, customer_id: str) -> bool:
        customer = next((c for c in self.customers if c.customer_id == customer_id), None)
        if not customer or not customer.stay or not customer.stay.is_active:
            print(f"Customer {customer_id} is not checked in or has no active stay.")
            return False

        if not customer.cards:
            print(f"Customer {customer.name} has no cards to return.")
            return False

        if not any(card.is_active for card in customer.cards):
            print(f"No active cards for {customer.name}.")
            return False

        charges = customer.stay.room.get_service_charges()
        if charges > 0:
            print(f"Customer {customer.name} incurred additional charges: ${charges}")
            print(f"Customer {customer.name} paid additional charges: ${charges}")

        customer.stay.end_stay(datetime.now())
        print(f"Customer {customer.name} stay ended at {customer.stay.end_date}.")
        print(f"Customer {customer.name} successfully checked out.")
        customer.clear_stay()
        if customer_id in self.reservations:
            del self.reservations[customer_id]
        return True

    def add_reservation(self, customer_id: str):
        self.reservations[customer_id] = None


# Main Tester Function
def main():
    admin = Admin("Admin1")
    room1 = Room("101")
    room2 = Room("102")
    admin.add_room(room1)
    admin.add_room(room2)

    customer1 = Customer("John Doe", "CUST001")
    customer2 = Customer("Jane Smith", "CUST002")
    admin.add_customer(customer1)
    admin.add_customer(customer2)

    admin.add_reservation("CUST001")
    admin.add_reservation("CUST002")

    print("\n=== Test 1: Check-in with First Card for Customer 1 ===")
    admin.check_in("CUST001", "101", payment_done=True)

    print("\n=== Test 2: Add Second Card for Customer 1 (Same Stay) ===")
    if admin.check_in("CUST001", "101", payment_done=True):
        print(f"Room 101 has {len(room1.cards)} cards: {[str(card) for card in room1.cards]}")
        print(f"Customer 1 stay has {len(customer1.stay.cards)} cards.")

    print("\n=== Test 3: Add Service with Active Card ===")
    food = ItemService("Burger", 10.0)
    try:
        customer1.stay.room.add_service(food, customer1)
        print(f"Successfully added {food} to Room {customer1.stay.room.room_number}.")
    except ValueError as e:
        print(f"Failed to add service: {e}")

    print("\n=== Test 4: Check-in Fails for Different Customer (Room Occupied) ===")
    admin.check_in("CUST002", "101", payment_done=True)

    print("\n=== Test 5: Check-out Customer 1 (Deactivates All Cards) ===")
    admin.check_out("CUST001")
    print(f"Room 101 has {len(room1.cards)} cards after check-out: {[str(card) for card in room1.cards]}")

    print("\n=== Test 6: Check-in Customer 2 After Customer 1 Checks Out ===")
    admin.add_reservation("CUST002")
    admin.check_in("CUST002", "101", payment_done=True)

if __name__ == "__main__":
    main()