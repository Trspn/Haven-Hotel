import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from admin import Admin
from customer import Customer
from room import Room
from item_service import ItemService
from service_provider import ServiceProvider

class Controller:
    def __init__(self, admin_name: str):
        self.admin = Admin(admin_name)
        self.setup_rooms()
        self.setup_services()

    def setup_rooms(self):
        room1 = Room("101")
        room2 = Room("102")
        self.admin.add_room(room1)
        self.admin.add_room(room2)

    def setup_services(self):
        hotel_provider = ServiceProvider("Hotel")
        hotel_provider.add_item(ItemService("Hot Beverage", 2.50))
        hotel_provider.add_item(ItemService("Cold Beverage", 3.00))
        hotel_provider.add_item(ItemService("Traditional Breakfast", 15.00))
        hotel_provider.add_item(ItemService("Buffet Dinner", 25.00))
        hotel_provider.add_item(ItemService("Spa Experience", 50.00))
        self.admin.add_service_provider(hotel_provider)

    def create_customer(self, name: str, customer_id: str):
        customer = Customer(name, customer_id)
        self.admin.add_customer(customer)
        self.admin.add_reservation(customer_id)
        return customer

    def check_in_customer(self, customer_id: str, room_number: str, payment_done: bool = False):
        success = self.admin.check_in(customer_id, room_number, payment_done)
        return success, f"Check-in {'successful' if success else 'failed'} for customer {customer_id} in room {room_number}."

    def check_out_customer(self, customer_id: str):
        success = self.admin.check_out(customer_id)
        return success, f"Check-out {'successful' if success else 'failed'} for customer {customer_id}."

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
    
class HotelManagementGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotel Management System")
        self.controller = None
        self.customer_counter = 1

        self.create_admin_screen()

    def create_admin_screen(self):
        self.clear_window()

        tk.Label(self.root, text="Enter Admin Name:", font=("Arial", 14)).pack(pady=10)
        self.admin_name_entry = tk.Entry(self.root, font=("Arial", 12))
        self.admin_name_entry.pack(pady=5)

        tk.Button(self.root, text="Create Admin", command=self.initialize_admin, font=("Arial", 12)).pack(pady=10)

    def initialize_admin(self):
        admin_name = self.admin_name_entry.get().strip()
        if not admin_name:
            messagebox.showerror("Error", "Admin name cannot be empty.")
            return

        self.controller = Controller(admin_name)
        self.show_main_menu()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        self.clear_window()

        tk.Label(self.root, text=f"Welcome, {self.controller.admin.name}!", font=("Arial", 16)).pack(pady=10)

        tk.Button(self.root, text="Create Customer", command=self.show_create_customer, font=("Arial", 12)).pack(pady=5)
        tk.Button(self.root, text="Check-in Customer", command=self.show_check_in, font=("Arial", 12)).pack(pady=5)
        tk.Button(self.root, text="Check-out Customer", command=self.show_check_out, font=("Arial", 12)).pack(pady=5)
        tk.Button(self.root, text="Provide Service", command=self.show_provide_service, font=("Arial", 12)).pack(pady=5)
        tk.Button(self.root, text="Generate Service Record", command=self.show_generate_service_record, font=("Arial", 12)).pack(pady=5)
        tk.Button(self.root, text="View Room Occupancy", command=self.show_room_occupancy, font=("Arial", 12)).pack(pady=5)
        tk.Button(self.root, text="Manage Cards", command=self.show_manage_cards_menu, font=("Arial", 12)).pack(pady=5)
        tk.Button(self.root, text="Exit", command=self.root.quit, font=("Arial", 12)).pack(pady=5)

    def show_create_customer(self):
        self.clear_window()

        tk.Label(self.root, text="Create a New Customer", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.root, text="Customer Name:", font=("Arial", 12)).pack()
        self.customer_name_entry = tk.Entry(self.root, font=("Arial", 12))
        self.customer_name_entry.pack(pady=5)

        tk.Button(self.root, text="Create Customer", command=self.create_customer_action, font=("Arial", 12)).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.show_main_menu, font=("Arial", 12)).pack()

    def create_customer_action(self):
        customer_name = self.customer_name_entry.get().strip()
        if not customer_name:
            messagebox.showerror("Error", "Customer name cannot be empty.")
            return

        customer_id = f"CUST{self.customer_counter:03d}"
        self.customer_counter += 1
        self.controller.create_customer(customer_name, customer_id)
        messagebox.showinfo("Success", f"Customer {customer_name} (ID: {customer_id}) created successfully.")
        self.show_main_menu()

    def show_check_in(self):
        self.clear_window()

        tk.Label(self.root, text="Check-in Customer", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.root, text="Select Customer:", font=("Arial", 12)).pack()
        customer_ids = [c.customer_id for c in self.controller.admin.customers]
        if not customer_ids:
            tk.Label(self.root, text="No customers available. Please create a customer first.", font=("Arial", 12)).pack()
            tk.Button(self.root, text="Back", command=self.show_main_menu, font=("Arial", 12)).pack(pady=10)
            return

        self.customer_combobox = ttk.Combobox(self.root, values=customer_ids, font=("Arial", 12))
        self.customer_combobox.pack(pady=5)
        self.customer_combobox.set(customer_ids[0] if customer_ids else "")

        tk.Label(self.root, text="Select Room:", font=("Arial", 12)).pack()
        room_numbers = [r.room_number for r in self.controller.admin.rooms]
        self.room_combobox = ttk.Combobox(self.root, values=room_numbers, font=("Arial", 12))
        self.room_combobox.pack(pady=5)
        self.room_combobox.set(room_numbers[0] if room_numbers else "")

        self.payment_var = tk.BooleanVar()
        tk.Checkbutton(self.root, text="Payment Done", variable=self.payment_var, font=("Arial", 12)).pack(pady=5)

        tk.Button(self.root, text="Check-in", command=self.check_in_action, font=("Arial", 12)).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.show_main_menu, font=("Arial", 12)).pack()

    def check_in_action(self):
        customer_id = self.customer_combobox.get()
        room_number = self.room_combobox.get()
        payment_done = self.payment_var.get()

        if not customer_id or not room_number:
            messagebox.showerror("Error", "Please select a customer and a room.")
            return

        success, message = self.controller.check_in_customer(customer_id, room_number, payment_done)
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

    def show_check_out(self):
        self.clear_window()

        tk.Label(self.root, text="Check-out Customer", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.root, text="Select Customer:", font=("Arial", 12)).pack()
        customer_ids = [c.customer_id for c in self.controller.admin.customers]
        if not customer_ids:
            tk.Label(self.root, text="No customers available.", font=("Arial", 12)).pack()
            tk.Button(self.root, text="Back", command=self.show_main_menu, font=("Arial", 12)).pack(pady=10)
            return

        self.customer_combobox = ttk.Combobox(self.root, values=customer_ids, font=("Arial", 12))
        self.customer_combobox.pack(pady=5)
        self.customer_combobox.set(customer_ids[0] if customer_ids else "")

        tk.Button(self.root, text="Check-out", command=self.check_out_action, font=("Arial", 12)).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.show_main_menu, font=("Arial", 12)).pack()

    def check_out_action(self):
        customer_id = self.customer_combobox.get()

        if not customer_id:
            messagebox.showerror("Error", "Please select a customer.")
            return

        success, message = self.controller.check_out_customer(customer_id)
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

    def show_provide_service(self):
        self.clear_window()

        tk.Label(self.root, text="Provide Service to Room", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.root, text="Select Customer:", font=("Arial", 12)).pack()
        customer_ids = [c.customer_id for c in self.controller.admin.customers if c.stay and c.stay.is_active]
        if not customer_ids:
            tk.Label(self.root, text="No checked-in customers available.", font=("Arial", 12)).pack()
            tk.Button(self.root, text="Back", command=self.show_main_menu, font=("Arial", 12)).pack(pady=10)
            return

        self.provide_service_customer_combobox = ttk.Combobox(self.root, values=customer_ids, font=("Arial", 12))
        self.provide_service_customer_combobox.pack(pady=5)
        self.provide_service_customer_combobox.set(customer_ids[0] if customer_ids else "")

        hotel_provider = self.controller.admin.get_service_provider("Hotel")
        service_names = [item.name for item in hotel_provider.items] if hotel_provider else []
        if not service_names:
            tk.Label(self.root, text="No services available.", font=("Arial", 12)).pack()
            tk.Button(self.root, text="Back", command=self.show_main_menu, font=("Arial", 12)).pack(pady=10)
            return

        tk.Label(self.root, text="Select Service:", font=("Arial", 12)).pack()
        self.service_combobox = ttk.Combobox(self.root, values=service_names, font=("Arial", 12))
        self.service_combobox.pack(pady=5)
        self.service_combobox.set(service_names[0] if service_names else "")

        tk.Button(self.root, text="Add Service to Room", command=self.add_service_action, font=("Arial", 12)).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.show_main_menu, font=("Arial", 12)).pack()

    def add_service_action(self):
        customer_id = self.provide_service_customer_combobox.get()
        service_name = self.service_combobox.get()

        if not customer_id or not service_name:
            messagebox.showerror("Error", "Please select a customer and a service.")
            return

        success, message = self.controller.add_service_to_room(customer_id, service_name)
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

    def show_generate_service_record(self):
        self.clear_window()

        tk.Label(self.root, text="Generate Service Record", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.root, text="Select Customer:", font=("Arial", 12)).pack()
        customer_ids = [c.customer_id for c in self.controller.admin.customers if c.stay and c.stay.is_active]
        if not customer_ids:
            tk.Label(self.root, text="No checked-in customers available.", font=("Arial", 12)).pack()
            tk.Button(self.root, text="Back", command=self.show_main_menu, font=("Arial", 12)).pack(pady=10)
            return

        self.service_record_customer_combobox = ttk.Combobox(self.root, values=customer_ids, font=("Arial", 12))
        self.service_record_customer_combobox.pack(pady=5)
        self.service_record_customer_combobox.set(customer_ids[0] if customer_ids else "")

        tk.Button(self.root, text="Generate Report", command=self.generate_service_record_action, font=("Arial", 12)).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.show_main_menu, font=("Arial", 12)).pack()

    def generate_service_record_action(self):
        customer_id = self.service_record_customer_combobox.get()
        if not customer_id:
            messagebox.showerror("Error", "Please select a customer.")
            return

        report = self.controller.generate_customer_service_record(customer_id)
        messagebox.showinfo("Service Record", report)

    def show_room_occupancy(self):
        self.clear_window()

        tk.Label(self.root, text="Room Occupancy Details", font=("Arial", 14)).pack(pady=10)

        occupancy_details = self.controller.get_room_occupancy_details()
        details_label = tk.Label(self.root, text=occupancy_details, font=("Courier New", 10), justify='left') # Use Courier New for better alignment
        details_label.pack(padx=10, pady=10)

        tk.Button(self.root, text="Back", command=self.show_main_menu, font=("Arial", 12)).pack(pady=10)

    def show_manage_cards_menu(self):
        self.clear_window()

        tk.Label(self.root, text="Manage Cards by Room", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.root, text="Select Room:", font=("Arial", 12)).pack()
        room_numbers = [r.room_number for r in self.controller.admin.rooms]
        if not room_numbers:
            tk.Label(self.root, text="No rooms available.", font=("Arial", 12)).pack()
            tk.Button(self.root, text="Back", command=self.show_main_menu, font=("Arial", 12)).pack(pady=10)
            return

        self.manage_cards_room_combobox = ttk.Combobox(self.root, values=room_numbers, font=("Arial", 12), state="readonly")
        self.manage_cards_room_combobox.pack(pady=5)
        self.manage_cards_room_combobox.set(room_numbers[0] if room_numbers else "")
        self.manage_cards_room_combobox.bind("<<ComboboxSelected>>", self.update_card_list)

        self.card_list_label = tk.Label(self.root, text="Cards in Room:", font=("Arial", 12))
        self.card_list_label.pack(pady=5)
        self.card_list_scrollbar = tk.Scrollbar(self.root)
        self.card_list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.card_list = tk.Listbox(self.root, yscrollcommand=self.card_list_scrollbar.set, font=("Arial", 10))
        self.card_list.pack(pady=5, fill=tk.BOTH, expand=True)
        self.card_list_scrollbar.config(command=self.card_list.yview)

        tk.Button(self.root, text="Add Card to Room", command=self.add_card_to_room_action, font=("Arial", 12)).pack(pady=5)
        tk.Button(self.root, text="Delete Selected Card", command=self.delete_card_action, font=("Arial", 12)).pack(pady=5)
        tk.Button(self.root, text="Activate Selected Card", command=self.activate_selected_card_action, font=("Arial", 12)).pack(pady=5)
        tk.Button(self.root, text="Deactivate Selected Card", command=self.deactivate_selected_card_action, font=("Arial", 12)).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.show_main_menu, font=("Arial", 12)).pack(pady=10)

        # Initial population of the card list if rooms exist
        if room_numbers:
            self.update_card_list(None)

    def update_card_list(self, event=None):
        selected_room = self.manage_cards_room_combobox.get()
        cards = self.controller.get_cards_for_room(selected_room)
        self.card_list.delete(0, tk.END)
        for card in cards:
            status = "Active" if card.is_active else "Inactive"
            self.card_list.insert(tk.END, f"ID: {card.card_id} ({status})")

    def add_card_to_room_action(self):
        selected_room = self.manage_cards_room_combobox.get()
        if not selected_room:
            messagebox.showerror("Error", "Please select a room.")
            return

        new_card_id = simpledialog.askstring("Add Card", f"Enter ID for new card for Room {selected_room}:")
        if new_card_id:
            new_card = self.controller.add_card_to_room(selected_room, new_card_id)
            if new_card:
                self.update_card_list()
            else:
                messagebox.showerror("Error", "Failed to add card.")

    def delete_card_action(self):
        selected_room = self.manage_cards_room_combobox.get()
        selected_index = self.card_list.curselection()
        if not selected_room or not selected_index:
            messagebox.showerror("Error", "Please select a room and a card to delete.")
            return

        card_info = self.card_list.get(selected_index[0])
        card_id = card_info.split(" ")[1]  # Extract card ID

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Card {card_id} from Room {selected_room}?"):
            if self.controller.delete_card(card_id):
                self.update_card_list()
                messagebox.showinfo("Success", f"Card {card_id} deleted.")
            else:
                messagebox.showerror("Error", f"Could not delete card {card_id}.")

    def activate_selected_card_action(self):
        selected_index = self.card_list.curselection()
        if not selected_index:
            messagebox.showerror("Error", "Please select a card to activate.")
            return

        card_info = self.card_list.get(selected_index[0])
        card_id = card_info.split(" ")[1]

        if self.controller.activate_card(card_id):
            self.update_card_list()
            messagebox.showinfo("Success", f"Card {card_id} activated.")
        else:
            messagebox.showerror("Error", f"Could not activate card {card_id}.")

    def deactivate_selected_card_action(self):
        selected_index = self.card_list.curselection()
        if not selected_index:
            messagebox.showerror("Error", "Please select a card to deactivate.")
            return

        card_info = self.card_list.get(selected_index[0])
        card_id = card_info.split(" ")[1]

        if self.controller.deactivate_card(card_id):
            self.update_card_list()
            messagebox.showinfo("Success", f"Card {card_id} deactivated.")
        else:
            messagebox.showerror("Error", f"Could not deactivate card {card_id}.")

def main():
    root = tk.Tk()
    app = HotelManagementGUI(root)
    root.geometry("600x650") # Increased window size
    root.mainloop()

if __name__ == "__main__":
    main()

def main():
    root = tk.Tk()
    app = HotelManagementGUI(root)
    root.geometry("600x600") # Increased window size to accommodate more content
    root.mainloop()

if __name__ == "__main__":
    main()