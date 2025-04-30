import numpy as np

#Define a class for the oxygen recovery processor
class OxygenRecoveryProcessor:
    
    conversion_rates = {
            "oxygen": 0.80, 
            "h2": 0.10,              
            "pure_water": 0.90     
        } 
    def __init__(self, oxygen_tank, pure_h2o_capacity=10.0, h2_capacity=10.0, oxygen_capacity=10.0,co2_to_h2o=None):
        self.pure_h2o_capacity = pure_h2o_capacity
        self.h2_capacity = h2_capacity
        self.oxygen_capacity = oxygen_capacity
        self.oxygen_tank = oxygen_tank  # Refer to Oxygen Tank
        self.co2_to_h2o = co2_to_h2o  # Placeholder for CO₂- H₂O system 
        self.h2o_to_h2o = None  # Placeholder for CO₂-H₂O system 
        self.conversion_rate = 3  # 3 kg pure H2O → 3 kg gray H2O
        self.pure_water_received = 0.0 
        
        # Initial  amount
        self.pure_h2o_amount = 10.0  
        self.h2_amount = 0.0
        self.oxygen_amount = 0.0
            
    def receive_pure_water(self, amount):
        self.pure_water_received += amount
        return amount  # Accepting everything
    
    def extract_hydrogen(self):
     h2o_split=self.pure_water_received # for the entering amount of gray-H₂O 
     if h2o_split <= 0:
        return 0, 0, 0

    # Calculate products
     oxygen_recovered = h2o_split * self.conversion_rates["oxygen"] / self.conversion_rates["pure_water"]
     hydrogen_produced = h2o_split * self.conversion_rates["h2"] / self.conversion_rates["pure_water"]

    # Apply capacity limits
     oxygen_recovered = min(oxygen_recovered, self.oxygen_capacity - self.oxygen_amount)
     hydrogen_produced = min(hydrogen_produced, self.h2_capacity - self.h2_amount)

    # Update internal stores
     self.oxygen_amount += oxygen_recovered
     self.h2_amount += hydrogen_produced

    # Reset water received after use
     self.pure_water_received = 0.0

    # Transfer oxygen to tank
     transferred_oxygen = self.transfer_oxygen_to_tank()

    # Transfer hydrogen to CO₂-H₂O  systems
     if self.co2_to_h2o:
        self.co2_to_h2o.receive_hydrogen(hydrogen_produced)
     if self.h2o_to_h2o:
        self.h2o_to_h2o.receive_hydrogen(hydrogen_produced)

     return hydrogen_produced, oxygen_recovered, transferred_oxygen

    def provide_hydrogen(self):
        return self.h2_amount  

    def transfer_oxygen_to_tank(self):
     if self.oxygen_amount > 0:  
        # Calculate the available space in the oxygen tank
        available_capacity = self.oxygen_tank.capacity - self.oxygen_tank.o2_level   
        # Transfer oxygen to the oxygen tank, but limit to the available capacity
        transferable_oxygen = min(self.oxygen_amount, available_capacity)
        # Fianlly transfer the oxygen to the oxygen tank
        self.oxygen_amount -= transferable_oxygen # Reduce the amount of oxygen in the processor
 
        return transferable_oxygen  # Return the transferred amount

    def get_entering_oxygen(self):
        self.oxygen_amount =0
        return self.oxygen_amount
    
    def get_entering_hydrogen(self):
        self.h2_amount =0
        return self.h2_amount
    
    def get_oxygen_status(self):
     total_entered = self.oxygen_tank.get_total_oxygen_status()
     current_o2_level = self.oxygen_tank.get_o2_level()
     return {
        "total_entered": total_entered,
        "current_o2_level": current_o2_level
    }