import numpy as np
infinity = np.inf


class Outside:
    conversion_rates = {
        "carbon": 0.30,   # Carbon produced per mole of CO₂ consumed (grams per mole)
        "methane": 0.40,  # CH₄ production rate (grams per mole)
        
    }
    def __init__(self, oxygen_capacity=infinity, carbondioxide_capacity=infinity, vaporh2o_capacity=infinity, methane_capacity=infinity, carbon_capacity=infinity, grayh2o_capacity=infinity):
        self.oxygen_capacity = oxygen_capacity
        self.carbondioxide_capacity = carbondioxide_capacity
        self.vaporh2o_capacity = vaporh2o_capacity
        self.methane_capacity = methane_capacity
        self.carbon_capacity = carbon_capacity
        self.grayh2o_capacity = grayh2o_capacity

        self.oxygen_amount = 0.0
        self.carbondioxide_amount = 0.0
        self.vaporh2o_amount = 0.0
        self.methane_amount = 0.0
        self.carbon_storage = 0.0  # Carbon received from Sabatier reaction
        self.grayh2o_amount = 0.0
        
    def receive_carbon(self, carbon_amount):
        self.carbon_storage += carbon_amount  
    
    def get_oxygen_level(self):
        return self.oxygen_amount

    def get_carbondioxide_level(self):
        return self.carbondioxide_amount