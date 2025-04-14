import tkinter as tk
from typing import List
from tkinter import ttk, messagebox, simpledialog
from admin import Admin
from customer import Customer
from room import Room
from item_service import ItemService
from service_provider import ServiceProvider

class Controller:
    def __init__(self, admin_name: str):
        self.admin = Admin(admin_name)
        self.current_user_role = None
        self.setup_rooms()
        self.setup_services()

    def setup_rooms(self):
        room1 = Room("101")
        room2 = Room("102")
        room3 = Room("103")
        room4 = Room("104")
        room5 = Room("105")
        room6 = Room("106")
        room7 = Room("107")
        self.admin.add_room(room1)
        self.admin.add_room(room2)
        self.admin.add_room(room3)
        self.admin.add_room(room4)
        self.admin.add_room(room5)
        self.admin.add_room(room6)
        self.admin.add_room(room7)

    def setup_services(self):
        hotel_provider = ServiceProvider("Hotel")
        hotel_provider.add_item(ItemService("Hot Beverage", 2.50))
        hotel_provider.add_item(ItemService("Cold Beverage", 3.00))
        hotel_provider.add_item(ItemService("Traditional Breakfast", 15.00))
        hotel_provider.add_item(ItemService("Buffet Dinner", 25.00))
        hotel_provider.add_item(ItemService("Spa Experience", 50.00))
        self.admin.add_service_provider(hotel_provider)

    def create_reservation(self, name: str, customer_id: str, room_number: str, length: int):
        customer = Customer(name, customer_id)
        self.admin.add_customer(customer)
        room = next((r for r in self.admin.rooms if r.room_number == room_number), None)
        if not room:
            return False, f"Room {room_number} not found."
        success = self.admin.add_reservation(customer_id, room, length)
        if success:
            return True, f"Reservation for {name} (ID: {customer_id}) in room {room_number} for {length} days created successfully."
        return False, "Failed to create reservation."

    def update_reservation(self, customer_id: str, room_number: str = None, length: int = None):
        room = None
        if room_number:
            room = next((r for r in self.admin.rooms if r.room_number == room_number), None)
            if not room:
                return False, f"Room {room_number} not found."
        success = self.admin.update_reservation(customer_id, room, length)
        if success:
            return True, f"Reservation for customer {customer_id} updated successfully."
        return False, "Failed to update reservation (may be checked in or not found)."

    def delete_reservation(self, customer_id: str):
        success = self.admin.delete_reservation(customer_id)
        if success:
            return True, f"Reservation for customer {customer_id} deleted successfully."
        return False, "Failed to delete reservation (may be checked in or not found)."

    def check_in_customer(self, customer_id: str, payment_done: bool = False):
        success = self.admin.check_in(customer_id, payment_done)
        return success, f"Check-in {'successful' if success else 'failed'} for customer {customer_id}."

    def check_out_customer(self, customer_id: str):
        success, message = self.admin.check_out(customer_id)
        return success, message

    def add_service_to_room(self, customer_id: str, service_name: str):
        success = self.admin.add_service_to_room(customer_id, service_name)
        return success, f"Adding service '{service_name}' to room for customer {customer_id} was {'successful' if success else 'failed'}."

    def generate_customer_service_record(self, customer_id: str):
        report = self.admin.generate_customer_service_record(customer_id)
        return report

    def get_room_occupancy_details(self):
        return self.admin.get_room_occupancy_details()

    def get_cards_for_room(self, room_number: str):
        return self.admin.get_cards_for_room(room_number)

    def add_card_to_room(self, room_number: str, card_id: str):
        return self.admin.add_card_to_room(room_number, card_id)

    def delete_card(self, card_id: str):
        return self.admin.delete_card(card_id)

    def activate_card(self, card_id: str):
        return self.admin.activate_card(card_id)

    def deactivate_card(self, card_id: str):
        return self.admin.deactivate_card(card_id)

    def login(self, password: str) -> (bool, str):
        if password == "AD01":
            self.current_user_role = "admin"
            return True, "Logged in as admin."
        elif password == "SERV01":
            self.current_user_role = "service_provider"
            return True, "Logged in as service provider."
        return False, "Invalid password."

    def request_service(self, customer_id: str, service_name: str) -> (bool, str):
        if self.current_user_role != "admin":
            return False, "Only admins can request services."
        return self.admin.request_service(customer_id, service_name)

    def complete_service(self, customer_id: str, service_name: str) -> (bool, str):
        if self.current_user_role != "service_provider":
            return False, "Only service providers can complete service requests."
        return self.admin.complete_service(customer_id, service_name)

    def get_pending_services(self) -> List[tuple]:
        return self.admin.get_pending_services()