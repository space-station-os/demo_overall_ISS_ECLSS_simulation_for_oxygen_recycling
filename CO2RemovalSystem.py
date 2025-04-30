import numpy as np 
# Define a class for the CO₂ removal system
class CO2RemovalSystem:
    def __init__(self, removal_rate):
        self.removal_rate = removal_rate  # How much CO₂ can be removed per cycle

    def remove_co2(self, co2_level):
        # Ensure we remove CO₂ and send to the CO₂ to other systems / can be CO₂ tank or CO₂ separator or any other device 
        co2_removed = min(co2_level, self.removal_rate)
        return co2_removed
      