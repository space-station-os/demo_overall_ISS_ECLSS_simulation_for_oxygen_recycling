import numpy as np

#Define the Human Convertion Module               
class HumanResourceTank:
    def __init__(self, co2_initial, co2_capacity, o2_initial, o2_capacity, vapor_h2o_initial, vapor_h2o_capacity, gray_h2o_initial, gray_h2o_capacity,gray_h2o_recycling=None):
        # Initialize CO2
        self.co2_level = co2_initial
        self.co2_capacity = co2_capacity

        # Initialize O2
        self.o2_level = o2_initial
        self.o2_capacity = o2_capacity
        
        # Initialize vapor H2O
        self.vapor_h2o_level = vapor_h2o_initial
        self.vapor_h2o_capacity = vapor_h2o_capacity
        
        # Initialize gray H2O
        self.gray_h2o_level = gray_h2o_initial
        self.gray_h2o_capacity = gray_h2o_capacity
        self.gray_h2o_recycling = gray_h2o_recycling  # Reference to GrayH2oToPureH2oRecyclingProcessor
        
    def new_vapor_h2o_level(self, vapor_h2o_production_rate_per_hour):
        self.vapor_h2o_level = vapor_h2o_production_rate_per_hour
        return self.vapor_h2o_level  # Return the new vapor H₂O level

    def transfer_gray_h2o_to_recycling(self):
        self.gray_h2o_amount = self.vapor_h2o_level
        if self.gray_h2o_recycling:
         transferred_gray_h2o = self.gray_h2o_recycling.receive_gray_water(self.gray_h2o_amount, source="tank")
        self.gray_h2o_level -= transferred_gray_h2o  # Reduce the transferred amount from the tank

    def new_co2_level(self, co2_produced, co2_removed):
        self.co2_level += co2_produced - co2_removed
        if self.co2_level > self.co2_capacity:
            self.co2_level = self.co2_capacity
        elif self.co2_level < 0:
            self.co2_level = 0

    def transfer_co2(self, amount):
        transferred_co2 = min(self.co2_level, amount)
        self.co2_level -= transferred_co2
        return transferred_co2

    def receive_o2(self, oxygen_amount):
        available_capacity = self.o2_capacity - self.o2_level
        self.o2_level += min(oxygen_amount, available_capacity)

        
    def transfer_o2_to_human(self, human, o2_amount):
        transferred_o2 = min(self.o2_level, o2_amount)
        self.o2_level -= transferred_o2
        human.update_o2(transferred_o2)  # Human receives oxygen
     # The human consumes oxygen based on the consumption rate at ISS (The model is based on the Daily Human Metabolic Load Profile, originally developed by NASA for their Crew Exploration program)
    
    def update_o2(self, o2_transferred_to_human, oxygen_consumption_rate_per_hour):
        self.o2_level = max(0, self.o2_level + o2_transferred_to_human - oxygen_consumption_rate_per_hour)
        
    def get_status(self):
        return {
            "CO2 Level": self.co2_level,
            "O2 Level": self.o2_level,
            "Vapor H2O Level": self.vapor_h2o_level,
            "Gray H2O Level": self.gray_h2o_level
        }
