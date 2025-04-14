import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from controller import Controller

class HotelManagementGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotel Management System")
        self.controller = Controller("Hotel Admin")
        self.customer_counter = 1
        self.selected_service_line = None
        self.show_login_screen()
        self.root.geometry("600x650")
        # Bind the window close event to save data
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        # Save data before closing
        self.controller.admin.save_to_file()
        self.root.destroy()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self.clear_window()
        tk.Label(self.root, text="Enter Password:", font=("Arial", 14)).pack(pady=10)
        password_entry = tk.Entry(self.root, show="*", font=("Arial", 12))
        password_entry.pack(pady=5)
        tk.Button(self.root, text="Login", command=lambda: self.process_login(password_entry.get()), font=("Arial", 12)).pack(pady=10)

    def process_login(self, password):
        success, message = self.controller.login(password)
        if success:
            # Determine the next customer ID based on existing customers
            if self.controller.admin.customers:
                last_customer_id = max(int(c.customer_id.replace("CUST", "")) for c in self.controller.admin.customers)
                self.customer_counter = last_customer_id + 1
            self.show_main_menu()
        else:
            messagebox.showerror("Error", message)

    def show_main_menu(self):
        self.clear_window()
        role = self.controller.current_user_role
        tk.Label(self.root, text=f"Welcome, {role.capitalize()}!", font=("Arial", 16)).pack(pady=10)

        if role == "admin":
            tk.Button(self.root, text="Manage Customer Reservation", command=self.show_manage_customer_reservation, font=("Arial", 12)).pack(pady=5)
            tk.Button(self.root, text="Check-in Customer", command=self.show_check_in, font=("Arial", 12)).pack(pady=5)
            tk.Button(self.root, text="Check-out Customer", command=self.show_check_out, font=("Arial", 12)).pack(pady=5)
            tk.Button(self.root, text="Request Service", command=self.show_request_service, font=("Arial", 12)).pack(pady=5)
            tk.Button(self.root, text="Generate Service Record", command=self.show_generate_service_record, font=("Arial", 12)).pack(pady=5)
            tk.Button(self.root, text="View Room Occupancy", command=self.show_room_occupancy, font=("Arial", 12)).pack(pady=5)
            tk.Button(self.root, text="Manage Cards", command=self.show_manage_cards_menu, font=("Arial", 12)).pack(pady=5)
            tk.Button(self.root, text="Logout", command=self.show_login_screen, font=("Arial", 12)).pack(pady=5)
        elif role == "service_provider":
            tk.Button(self.root, text="View Pending Service Requests", command=self.show_pending_requests, font=("Arial", 12)).pack(pady=5)
            tk.Button(self.root, text="Logout", command=self.show_login_screen, font=("Arial", 12)).pack(pady=5)

    def show_manage_customer_reservation(self):
        self.clear_window()
        tk.Label(self.root, text="Manage Customer Reservation", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.root, text="Add New Reservation", font=("Arial", 12, "bold")).pack(pady=5)
        tk.Label(self.root, text="Customer Name:", font=("Arial", 12)).pack()
        self.customer_name_entry = tk.Entry(self.root, font=("Arial", 12))
        self.customer_name_entry.pack(pady=5)
        tk.Label(self.root, text="Select Room:", font=("Arial", 12)).pack()
        room_numbers = [r.room_number for r in self.controller.admin.rooms]
        self.room_combobox = ttk.Combobox(self.root, values=room_numbers, font=("Arial", 12))
        self.room_combobox.pack(pady=5)
        self.room_combobox.set(room_numbers[0] if room_numbers else "")
        tk.Label(self.root, text="Stay Length (days):", font=("Arial", 12)).pack()
        self.length_entry = tk.Entry(self.root, font=("Arial", 12))
        self.length_entry.pack(pady=5)
        tk.Button(self.root, text="Create Reservation", command=self.create_reservation_action, font=("Arial", 12)).pack(pady=5)

        tk.Label(self.root, text="Existing Reservations", font=("Arial", 12, "bold")).pack(pady=10)
        reservations = [(cid, stay) for cid, stay in self.controller.admin.reservations.items() if stay and not stay.is_active]
        if not reservations:
            tk.Label(self.root, text="No pending reservations available.", font=("Arial", 12)).pack()
        else:
            self.reservation_combobox = ttk.Combobox(self.root, values=[f"{cid} (Room: {stay.room.room_number}, {stay.length} days)" for cid, stay in reservations], font=("Arial", 12))
            self.reservation_combobox.pack(pady=5)
            self.reservation_combobox.set([f"{cid} (Room: {stay.room.room_number}, {stay.length} days)" for cid, stay in reservations][0] if reservations else "")
            tk.Button(self.root, text="Update Reservation", command=self.show_update_reservation, font=("Arial", 12)).pack(pady=5)
            tk.Button(self.root, text="Delete Reservation", command=self.delete_reservation_action, font=("Arial", 12)).pack(pady=5)

        tk.Button(self.root, text="Back", command=self.show_main_menu, font=("Arial", 12)).pack(pady=10)

    def create_reservation_action(self):
        customer_name = self.customer_name_entry.get().strip()
        room_number = self.room_combobox.get()
        try:
            length = int(self.length_entry.get())
            if length <= 0:
                raise ValueError("Stay length must be a positive integer.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid stay length: {e}")
            return

        if not customer_name:
            messagebox.showerror("Error", "Customer name cannot be empty.")
            return
        if not room_number:
            messagebox.showerror("Error", "Please select a room.")
            return

        customer_id = f"CUST{self.customer_counter:03d}"
        self.customer_counter += 1
        success, message = self.controller.create_reservation(customer_name, customer_id, room_number, length)
        if success:
            messagebox.showinfo("Success", message)
            self.show_manage_customer_reservation()
        else:
            messagebox.showerror("Error", message)

    def show_update_reservation(self):
        selected_reservation = self.reservation_combobox.get()
        if not selected_reservation:
            messagebox.showerror("Error", "Please select a reservation to update.")
            return

        customer_id = selected_reservation.split(" ")[0]
        self.clear_window()
        tk.Label(self.root, text=f"Update Reservation for {customer_id}", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.root, text="New Room (leave blank to keep current):", font=("Arial", 12)).pack()
        room_numbers = [r.room_number for r in self.controller.admin.rooms]
        self.update_room_combobox = ttk.Combobox(self.root, values=room_numbers, font=("Arial", 12))
        self.update_room_combobox.pack(pady=5)

        tk.Label(self.root, text="New Stay Length (days, leave blank to keep current):", font=("Arial", 12)).pack()
        self.update_length_entry = tk.Entry(self.root, font=("Arial", 12))
        self.update_length_entry.pack(pady=5)

        tk.Button(self.root, text="Update", command=lambda: self.update_reservation_action(customer_id), font=("Arial", 12)).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.show_manage_customer_reservation, font=("Arial", 12)).pack(pady=5)

    def update_reservation_action(self, customer_id):
        room_number = self.update_room_combobox.get() or None
        length_input = self.update_length_entry.get()
        length = None
        if length_input:
            try:
                length = int(length_input)
                if length <= 0:
                    raise ValueError("Stay length must be a positive integer.")
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid stay length: {e}")
                return

        success, message = self.controller.update_reservation(customer_id, room_number, length)
        if success:
            messagebox.showinfo("Success", message)
            self.show_manage_customer_reservation()
        else:
            messagebox.showerror("Error", message)

    def delete_reservation_action(self):
        selected_reservation = self.reservation_combobox.get()
        if not selected_reservation:
            messagebox.showerror("Error", "Please select a reservation to delete.")
            return

        customer_id = selected_reservation.split(" ")[0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the reservation for {customer_id}?"):
            success, message = self.controller.delete_reservation(customer_id)
            if success:
                messagebox.showinfo("Success", message)
                self.show_manage_customer_reservation()
            else:
                messagebox.showerror("Error", message)

    def show_check_in(self):
        self.clear_window()
        tk.Label(self.root, text="Check-in Customer", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Select Reservation:", font=("Arial", 12)).pack()
        reservations = [(cid, stay) for cid, stay in self.controller.admin.reservations.items() if stay and not stay.is_active]
        print("Reservations available for check-in:", [(cid, str(stay)) for cid, stay in reservations])
        if not reservations:
            tk.Label(self.root, text="No pending reservations available.", font=("Arial", 12)).pack()
            tk.Button(self.root, text="Back", command=self.show_main_menu, font=("Arial", 12)).pack(pady=10)
            return
        self.reservation_combobox = ttk.Combobox(self.root, values=[f"{cid} (Room: {stay.room.room_number})" for cid, stay in reservations], font=("Arial", 12))
        self.reservation_combobox.pack(pady=5)
        self.reservation_combobox.set([f"{cid} (Room: {stay.room.room_number})" for cid, stay in reservations][0] if reservations else "")
        self.payment_var = tk.BooleanVar()
        tk.Checkbutton(self.root, text="Payment Done", variable=self.payment_var, font=("Arial", 12)).pack(pady=5)
        tk.Button(self.root, text="Check-in", command=self.check_in_action, font=("Arial", 12)).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.show_main_menu, font=("Arial", 12)).pack()

    def check_in_action(self):
        selected_reservation = self.reservation_combobox.get()
        if not selected_reservation:
            messagebox.showerror("Error", "Please select a reservation.")
            return
        customer_id = selected_reservation.split(" ")[0]
        payment_done = self.payment_var.get()
        success, message = self.controller.check_in_customer(customer_id, payment_done)
        if success:
            messagebox.showinfo("Success", message)
            self.show_main_menu()
        else:
            messagebox.showerror("Error", message)

    def show_check_out(self):
        self.clear_window()
        tk.Label(self.root, text="Check-out Customer", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Select Customer:", font=("Arial", 12)).pack()
        customer_ids = [c.customer_id for c in self.controller.admin.customers if c.stay and c.stay.is_active]
        if not customer_ids:
            tk.Label(self.root, text="No checked-in customers available.", font=("Arial", 12)).pack()
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
            self.show_main_menu()
        else:
            messagebox.showerror("Error", message)

    def show_request_service(self):
        self.clear_window()
        tk.Label(self.root, text="Request Service", font=("Arial", 14)).pack(pady=10)
        customer_ids = [c.customer_id for c in self.controller.admin.customers if c.stay and c.stay.is_active]
        if not customer_ids:
            tk.Label(self.root, text="No checked-in customers available.", font=("Arial", 12)).pack()
            tk.Button(self.root, text="Back", command=self.show_main_menu, font=("Arial", 12)).pack(pady=10)
            return
        tk.Label(self.root, text="Select Customer:", font=("Arial", 12)).pack()
        customer_combobox = ttk.Combobox(self.root, values=customer_ids, font=("Arial", 12))
        customer_combobox.pack(pady=5)
        customer_combobox.set(customer_ids[0])
        tk.Label(self.root, text="Select Service:", font=("Arial", 12)).pack()
        hotel_provider = self.controller.admin.get_service_provider("Hotel")
        service_names = [item.name for item in hotel_provider.items] if hotel_provider else []
        service_combobox = ttk.Combobox(self.root, values=service_names, font=("Arial", 12))
        service_combobox.pack(pady=5)
        service_combobox.set(service_names[0] if service_names else "")
        tk.Button(self.root, text="Request Service", 
                 command=lambda: self.request_service_action(customer_combobox.get(), service_combobox.get()), 
                 font=("Arial", 12)).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.show_main_menu, font=("Arial", 12)).pack()

    def request_service_action(self, customer_id, service_name):
        success, message = self.controller.request_service(customer_id, service_name)
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

    def show_pending_requests(self):
        self.clear_window()
        tk.Label(self.root, text="Pending Service Requests", font=("Arial", 14)).pack(pady=10)
        pending_services = self.controller.get_pending_services()
        if not pending_services:
            tk.Label(self.root, text="No pending service requests.", font=("Arial", 12)).pack()
            tk.Button(self.root, text="Back", command=self.show_main_menu, font=("Arial", 12)).pack(pady=10)
            return

        frame = tk.Frame(self.root)
        frame.pack(pady=5, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.service_text_area = tk.Text(frame, height=10, width=50, font=("Arial", 10), yscrollcommand=scrollbar.set)
        self.service_text_area.pack(pady=5, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.service_text_area.yview)

        self.service_lines = []
        for idx, (customer_id, service_name) in enumerate(pending_services, 1):
            line_text = f"Customer: {customer_id} | Service: {service_name}\n"
            self.service_text_area.insert(tk.END, line_text)
            self.service_lines.append((customer_id, service_name))

        self.service_text_area.config(state=tk.NORMAL)
        self.service_text_area.bind("<Double-1>", self.select_service_line)

        tk.Button(self.root, text="Mark Selected as Completed", 
                 command=self.complete_service_action, 
                 font=("Arial", 12)).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.show_main_menu, font=("Arial", 12)).pack()

    def select_service_line(self, event):
        index = self.service_text_area.index("@%d,%d" % (event.x, event.y))
        line_number = int(index.split('.')[0])
        if 1 <= line_number <= len(self.service_lines):
            self.selected_service_line = line_number - 1

            self.service_text_area.tag_remove("highlight", "1.0", tk.END)
            self.service_text_area.tag_add("highlight", f"{line_number}.0", f"{line_number}.end")
            self.service_text_area.tag_configure("highlight", background="yellow")

    def complete_service_action(self):
        if self.selected_service_line is None:
            messagebox.showerror("Error", "Please double-click a request to select it.")
            return

        customer_id, service_name = self.service_lines[self.selected_service_line]
        success, message = self.controller.complete_service(customer_id, service_name)
        if success:
            messagebox.showinfo("Success", message)
            self.selected_service_line = None
            self.show_pending_requests()
        else:
            messagebox.showerror("Error", message)

    def show_generate_service_record(self):
        self.clear_window()
        tk.Label(self.root, text="Generate Service Record", font=("Arial", 14)).pack(pady=10)
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
        details_label = tk.Label(self.root, text=occupancy_details, font=("Courier New", 10), justify='left')
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
        card_id = card_info.split(" ")[1]
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
    root.mainloop()

if __name__ == "__main__":
    main()