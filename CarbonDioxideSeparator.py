import numpy as np

# Define Carbon Dioxide Separator  / CO₂ Adsorption and Desorption
class CarbonDioxideSeparator:
    def __init__(self, co2_level, co2separator_capacity, conversion_rate_kg_per_co2 = 0.5425 ):
        self.co2_amount = co2_level
        self.co2_storage = 0.0  # Amount of CO₂ the separator can store
        self.co2separator_capacity = co2separator_capacity
        self.conversion_rate_kg_per_co2 = conversion_rate_kg_per_co2  

    def convert_co2_to_h2o(self, co2_amount_kg):
        if co2_amount_kg <= self.co2separator_capacity:
            return 0  
        h2o_produced = co2_amount_kg /self.conversion_rate_kg_per_co2
        return h2o_produced

    def receive_co2(self, amount):
        if self.co2_storage + amount <= self.co2separator_capacity:
            self.co2_storage = amount
        
        else:
            self.co2_storage = self.co2separator_capacity

    def transfer_co2(self, co2_to_h2o_system):
        transfer_amount = min(self.co2_storage, self.co2separator_capacity)  # Ensure not to transfer more than available
        co2_to_h2o_system.receive_co2(transfer_amount)  # Transfer CO₂ to the system
        self.co2_storage -= transfer_amount  # Decrease CO₂ storage in the separator
        return transfer_amount

    def get_current_co2_level(self):
        return self.co2_storage
    