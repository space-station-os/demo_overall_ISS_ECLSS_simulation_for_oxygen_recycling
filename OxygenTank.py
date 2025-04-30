class OxygenTank:
    
    
    def __init__(self, initial_o2, capacity, human_tank, consumption_rate_per_hour, oxygen_conversion_rate=0.10,
                 increase_cycles=0, decrease_cycles=721, reset_value_after_decrease=None, reset_value_initial=None):
        self.o2_level = initial_o2  
        self.capacity = capacity 
        self.human_tank = human_tank  # Reference to Human Tank
        self.consumption_rate_per_hour = consumption_rate_per_hour  # O2 consumption rate per hour
        self.oxygen_conversion_rate = oxygen_conversion_rate  # Conversion rate for O2 recovery
        self.increase_cycles = increase_cycles  # Number of cycles to increase oxygen (6 cycles)
        self.decrease_cycles = decrease_cycles  # Number of cycles to decrease oxygen after increase
        self.oxygen_recovery = 0  # Default recovery value
        self.reset_value_after_decrease = reset_value_after_decrease  # Value to reset to after decrease cycles
        self.reset_value_initial = reset_value_initial 
        self.initial_capacity=100 # Reference from the main loop
        self.total_entered_o2 = initial_o2  # Total oxygen added to the tank
        self.total_transferred_o2 = 0  # Total oxygen transferred to the human tank
        self.cycle_counter = 0  # Counter to track the cycle number
        self.decrease_counter = 0  # Counter to track decrease cycles

    def add_oxygen(self, oxygen_amount):
        available_capacity = self.capacity - self.o2_level
        added = min(oxygen_amount, available_capacity)
        self.o2_level += added
        self.total_entered_o2 += added
        return self.o2_level

    def transfer_o2(self, oxygen_recovery=0.0):
        self.reset_value_initial = self.initial_capacity +( oxygen_recovery-(oxygen_recovery-self.consumption_rate_per_hour))
        self.oxygen_recovery = oxygen_recovery
        if self.cycle_counter < min(self.increase_cycles, 9):
           # Increase phase
         increase_amount = (oxygen_recovery - self.consumption_rate_per_hour)
         self.o2_level = min(self.capacity, self.o2_level + increase_amount)  # Avoid overflow
         self.cycle_counter += 1
           
        elif self.cycle_counter >= self.increase_cycles: 
            # Decrease phase after increase cycles
            if self.decrease_counter == 0 and self.reset_value_initial is not None:
                self.o2_level = self.reset_value_initial  # Reset oxygen level at the start of decrease phase

            if self.decrease_counter < self.decrease_cycles:
                # Decrease in oxygen level after cycle 6
                decrease_amount =(self.consumption_rate_per_hour - oxygen_recovery)
                self.o2_level -= decrease_amount  # Apply the decrease
                self.decrease_counter += 1

            # Oxygen transfer to human tank
            if self.o2_level > 0:
                # Transfer oxygen to human tank
                transfer_amount = max(self.o2_level, self.consumption_rate_per_hour)
                self.human_tank.receive_o2(transfer_amount)
                self.total_transferred_o2 = transfer_amount  # Track transferred oxygen

        return self.o2_level, self.total_transferred_o2


    def get_o2_level(self):
        return self.o2_level
    

    def get_total_oxygen_status(self):
        return self.total_entered_o2, self.total_transferred_o2
