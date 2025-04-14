from admin import Admin
from room import Room
from customer import Customer
from card import Card
from service_provider import ServiceProvider
from item_service import ItemService
from typing import List, Optional

class Controller:
    def __init__(self, admin_name: str):
        self.admin = Admin.load_from_file(admin_name)
        self.current_user_role = None
        self.setup_initial_data()

    def setup_initial_data(self):
        # Initialize 15 rooms (101 to 115)
        if not self.admin.rooms:
            for i in range(101, 116):  # 101 to 115 inclusive
                self.admin.add_room(Room(str(i)))
        
        # Initialize two service providers
        if not self.admin.service_providers:
            # First service provider: Hotel (Room Service A)
            hotel_provider = ServiceProvider("Hotel")
            hotel_provider.add_item(ItemService("Hot Beverage", 2.50))
            hotel_provider.add_item(ItemService("Cold Beverage", 3.00))
            hotel_provider.add_item(ItemService("Traditional Breakfast", 15.00))
            hotel_provider.add_item(ItemService("Buffet Dinner", 25.00))
            hotel_provider.add_item(ItemService("Spa Experience", 50.00))
            self.admin.add_service_provider(hotel_provider)

            # Second service provider: RoomSupport (Room Service B)
            room_support_provider = ServiceProvider("RoomSupport")
            room_support_provider.add_item(ItemService("Fresh Towels", 5.00))
            room_support_provider.add_item(ItemService("Fresh Sheets", 10.00))
            room_support_provider.add_item(ItemService("Replenish Toiletries", 3.00))
            room_support_provider.add_item(ItemService("Technical Support", 20.00))
            self.admin.add_service_provider(room_support_provider)

    def login(self, password: str) -> (bool, str):
        if password == "AD01":
            self.current_user_role = "admin"
            return True, "Logged in as Admin."
        elif password == "SERV01":
            self.current_user_role = "service_provider_a"
            return True, "Logged in as Room Service A."
        elif password == "SERV02":
            self.current_user_role = "service_provider_b"
            return True, "Logged in as Room Service B."
        else:
            return False, "Invalid password."

    def create_reservation(self, customer_name: str, customer_id: str, room_number: str, length: int) -> (bool, str):
        if self.current_user_role != "admin":
            return False, "Unauthorized access."
        room = next((r for r in self.admin.rooms if r.room_number == room_number), None)
        if not room:
            return False, f"Room {room_number} not found."
        customer = Customer(customer_name, customer_id)
        self.admin.add_customer(customer)
        if self.admin.add_reservation(customer_id, room, length):
            return True, f"Reservation created for {customer_name} (ID: {customer_id}) in Room {room_number}."
        return False, "Failed to create reservation."

    def update_reservation(self, customer_id: str, room_number: str = None, length: int = None) -> (bool, str):
        if self.current_user_role != "admin":
            return False, "Unauthorized access."
        room = None
        if room_number:
            room = next((r for r in self.admin.rooms if r.room_number == room_number), None)
            if not room:
                return False, f"Room {room_number} not found."
        if self.admin.update_reservation(customer_id, room, length):
            return True, f"Reservation updated for Customer ID {customer_id}."
        return False, "Failed to update reservation."

    def delete_reservation(self, customer_id: str) -> (bool, str):
        if self.current_user_role != "admin":
            return False, "Unauthorized access."
        if self.admin.delete_reservation(customer_id):
            return True, f"Reservation deleted for Customer ID {customer_id}."
        return False, "Failed to delete reservation."

    def check_in_customer(self, customer_id: str, payment_done: bool) -> (bool, str):
        if self.current_user_role != "admin":
            return False, "Unauthorized access."
        success = self.admin.check_in(customer_id, payment_done)
        if success:
            return True, f"Customer ID {customer_id} checked in successfully."
        return False, "Failed to check in customer."

    def check_out_customer(self, customer_id: str) -> (bool, str):
        if self.current_user_role != "admin":
            return False, "Unauthorized access."
        return self.admin.check_out(customer_id)

    def request_service(self, room_number: str, service_name: str) -> (bool, str):
        if self.current_user_role != "admin":
            return False, "Unauthorized access."
        return self.admin.request_service(room_number, service_name)

    def complete_service(self, room_number: str, service_name: str, completion_details: str = None) -> (bool, str):
        if not (self.current_user_role in ["service_provider_a", "service_provider_b"]):
            return False, "Unauthorized access."
        return self.admin.complete_service(room_number, service_name, self.current_user_role, completion_details)

    def get_pending_services(self) -> List[tuple]:
        if not (self.current_user_role in ["service_provider_a", "service_provider_b"]):
            return []
        return self.admin.get_pending_services(self.current_user_role)

    def generate_customer_service_record(self, customer_id: str) -> str:
        if self.current_user_role != "admin":
            return "Unauthorized access."
        return self.admin.generate_customer_service_record(customer_id)

    def get_room_occupancy_details(self) -> str:
        if self.current_user_role != "admin":
            return "Unauthorized access."
        return self.admin.get_room_occupancy_details()

    def get_cards_for_room(self, room_number: str) -> List[Card]:
        if self.current_user_role != "admin":
            return []
        return self.admin.get_cards_for_room(room_number)

    def add_card_to_room(self, room_number: str, card_id: str) -> Optional[Card]:
        if self.current_user_role != "admin":
            return None
        return self.admin.add_card_to_room(room_number, card_id)

    def delete_card(self, card_id: str) -> bool:
        if self.current_user_role != "admin":
            return False
        return self.admin.delete_card(card_id)

    def activate_card(self, card_id: str) -> bool:
        if self.current_user_role != "admin":
            return False
        return self.admin.activate_card(card_id)

    def deactivate_card(self, card_id: str) -> bool:
        if self.current_user_role != "admin":
            return False
        return self.admin.deactivate_card(card_id)