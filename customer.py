from typing import Optional

class Customer:
    def __init__(self, name: str, customer_id: str):
        self.name = name
        self.customer_id = customer_id
        self.card: Optional['Card'] = None  # Use string type hint
        self.stay: Optional['Stay'] = None  # Use string type hint

    def assign_card(self, card: 'Card'):
        self.card = card

    def assign_stay(self, stay: 'Stay'):
        self.stay = stay

    def __str__(self):
        return f"Customer {self.name} (ID: {self.customer_id})"