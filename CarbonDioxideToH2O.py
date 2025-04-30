import numpy as np
import random
from collections import namedtuple

class CarbonDioxideToH2O:
    conversion_rates = {
        "carbondioxide" : 1.10,  # CO₂ consumption rate (grams per mole)
        "methane": 0.40,         # CH4 production rate (grams per mole)
        "h2": 0.2,               # H₂ consumption rate (grams per mole per reaction)
        "gray_water": 0.90       # Gray water produced per mole reaction
    }
    
    def __init__(self, carbondioxide_capacity=10.0, h2_capacity=10.0, methane_capacity=10.0, gray_water_capacity=10.0):
        self.carbondioxide_capacity = carbondioxide_capacity
        self.h2_capacity = h2_capacity
        self.methane_capacity = methane_capacity
        self.gray_water_capacity = gray_water_capacity
       
        self.co2_storage = 0.0  # CO₂ storage
        self.h2_amount = 0.0    # Hydrogen storage 
        self.methane_amount = 0.0  #  CH₄ storage 
        self.gray_water_amount = 0.0  # Gray water storage 
        self.sabatier_processor = None  # Reference to SabatierProcessor
        self.gray_h2o_processor = None  # Reference to GrayH₂O  Recycling Processor
        self.incremental_h2_growth = 0.0  # Track the H₂ growth based on the reaction
        self.carbondioxide_convertion_rate = 0.5425 # carbon dioxide convertion rate from the carbon dioxide separator
        self.next_exception_cycle = 77
        self.exception_decrement = 1
 
        # Reaction behavior
        self.carbon_dioxide_export_counter = 0
        self.carbon_dioxide_export_interval = 3

        # Capacities
        self.carbondioxide_capacity = carbondioxide_capacity
        self.h2_capacity = h2_capacity
        self.methane_capacity = methane_capacity
        self.gray_water_capacity = gray_water_capacity

        # Hydrogen recovery timing
        self.h2_growth_count = 0
        self.oxygen_recovery_convertion_rate = 0.10
        # Metrics
        self.total_gray_water_produced = 0.0

        # Track cycles for hydrogen growth behavior
        self.cycle_count = 0
        self.next_cycle_double = False 
        self.last_incremental_h2 =0.0

    def receive_hydrogen(self, amount: float):
     before = self.h2_amount 
     # conversion rate apply for the hydrogen growth
     converted_h2_amount = amount * (self.oxygen_recovery_convertion_rate / self.conversion_rates["h2"]) 
     self.h2_amount = min(self.h2_amount + converted_h2_amount, self.h2_capacity)  
     return self.h2_amount - before
    
    def receive_co2(self, amount):
     if self.co2_storage + amount <= self.carbondioxide_capacity:
        # carbon dioxide it is receive at 50% of the production rate
        self.co2_storage += amount /((self.carbondioxide_convertion_rate/self.conversion_rates["carbondioxide"] )/0.50)
     else:
        overflow = self.co2_storage + amount - self.carbondioxide_capacity 
        self.co2_storage =self.carbondioxide_capacity 
        return overflow
   
    def perform_sabatier_reaction(self):
        methane = 0
        gray_water = 0

        if self.co2_storage == 0 :
            return 0, 0, 0, 0, 0, 0, 0, 0, 0 

        # Limit CO₂ usage percentage 50% 
        self.co2_usage_percentage = random.choice([0.50, 0.60,1.00, 1.50,1.10,0.70])

        co2_available = self.co2_storage * self.co2_usage_percentage
        co2_available_for_reaction = self.co2_storage   
        max_reactions_by_co2 = co2_available_for_reaction / self.conversion_rates["carbondioxide"] 
        max_reactions_by_h2 = self.h2_amount / self.conversion_rates["h2"]

        # 1:4 CO₂-to-H₂ ratio
        num_reactions = min(max_reactions_by_co2, max_reactions_by_h2)
        co2_used = num_reactions * self.conversion_rates["carbondioxide"] 
        h2_used = num_reactions * self.conversion_rates["h2"]

        # Calculate methane and gray water produced based on used CO₂ and H₂ 
        self.methane_amount = num_reactions * self.conversion_rates["methane"]
        self.gray_water_amount = num_reactions * self.conversion_rates["gray_water"]
        self.total_gray_water_produced += self.gray_water_amount
        
        self.co2_storage -= co2_used
        self.h2_amount -= h2_used 

        # Handle CO₂ export interval during the reaction
        self.carbon_dioxide_export_counter += 1

        # First export happens after 2 cycles, then every cycle after that
        if self.carbon_dioxide_export_counter >= self.carbon_dioxide_export_interval:
            co2_exported = co2_available  # Exported CO₂ is equal to the CO₂ used
            self.carbon_dioxide_export_counter = 2  # Reset counter after export
        else:
            co2_exported = 0 
   
    # Increment hydrogen  
        base_increment = h2_used / (self.conversion_rates["h2"] / self.oxygen_recovery_convertion_rate)

    # Hydrogen growth/decreasing tracking
        current_cycle = self.cycle_count
        adjusted_increment = 0.0

        if current_cycle < 4:
    # First 3 cycles: normal growth
         adjusted_increment = base_increment
        elif current_cycle == 3:
         adjusted_increment = base_increment
        elif current_cycle == 4:
         adjusted_increment = base_increment
        elif current_cycle == 5:
         adjusted_increment = -base_increment
        elif current_cycle == 6:
         adjusted_increment = base_increment * 2
         
        elif current_cycle == self.next_exception_cycle:
          adjusted_increment = base_increment

         # Next exception
          next_interval = 77 - self.exception_decrement
          self.exception_decrement += 1
          self.next_exception_cycle += next_interval

        else:
        # From cycle 7 onward: repeat 
           pattern_position = (current_cycle - 7) % 2
           if pattern_position == 0:
            adjusted_increment = -base_increment
           else:
            adjusted_increment = base_increment * 2

        self.incremental_h2_growth += adjusted_increment

        # Update for next cycle
        self.last_incremental_h2 = base_increment
        self.cycle_count += 1

        return methane, gray_water, self.methane_amount, self.gray_water_amount, co2_exported,  h2_used, co2_used, self.incremental_h2_growth
     
    def transfer_methane_to_sabatier(self):
        
        if self.sabatier_processor and self.methane_amount > 0:
         self.sabatier_processor.receive_methane(self.methane_amount)
         self.methane_amount = 0.0 
        
    def send_gray_h2o_to_recycling(self, gray_h2o_recycling_processor):
     gray_h2o_added = gray_h2o_recycling_processor.receive_gray_water(self.gray_water_amount, source="co2")
     self.gray_water_amount = 0.0
     return gray_h2o_added  
        
    def get_methane_level(self):
        return self.sabatier_processor.get_methane_level() if self.sabatier_processor else 0
    
    def get_co2_level(self):
        return self.co2_storage

    def get_gray_water_level(self):
     if self.gray_h2o_processor:
        return self.gray_h2o_processor.get_gray_water_level()
     return 0
