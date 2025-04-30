class WaterTankSmall:
    def __init__(self, initial_value, capacity, decrease_cycles=1, reset_value_after_decrease=None, co2_to_h2o=None, reset_value_initial=None, reset_factor=None):
        # Initial value, starts just below.
        self.co2_to_h2o = co2_to_h2o if co2_to_h2o is not None else 0  
        
        self.gray_water_amount = 0
        if self.co2_to_h2o and hasattr(self.co2_to_h2o, 'gray_water_amount'):
            self.gray_water_amount = self.co2_to_h2o.gray_water_amount
        self.pure_h2o_level = max(initial_value - self.gray_water_amount, 0)
        self.capacity = capacity
        self.initial_capacity = 50
        self.decrease_cycles = decrease_cycles  # Number of cycles where we want to decrease water
        self.initial_manual_cycles_done = 0
        self.reset_value_initial = reset_value_initial
        self.decrease_counter = 0  # Counter to track how many decrease cycles have passed
        self.initial_phase = True  # Flag for the initial decrease phase
        self.manual_increase_counter = 0
        self.conversion_rate_pure_water = 3
        self.conversion_rate_oxygen_recovery = 0.90
        self.total_conversion_rate = self.conversion_rate_pure_water / self.conversion_rate_oxygen_recovery
        self.pure_h2o_capacity = 10
        self.reset_value_after_decrease = 0

        # Set the reset_factor from the main loop
        self.reset_factor = reset_factor  

    def manually_run_initial_cycle(self, gray_amount):
        if self.manual_increase_counter < 2:
            if self.reset_value_initial is not None:
                self.pure_h2o_level = self.reset_value_initial
            self.pure_h2o_level = min(self.pure_h2o_level - gray_amount, self.capacity)
            self.manual_increase_counter += 1
        if self.manual_increase_counter == 2:
            self.initial_manual_cycles_done = True

    def receive_pure_water(self, gray_amount):
        if not self.initial_manual_cycles_done:
            return self.pure_h2o_level  

        if self.decrease_counter < self.decrease_cycles:
            if self.decrease_counter < 2:
                # First two cycles: 
                if self.reset_value_initial is not None:
                    self.pure_h2o_level = self.reset_value_initial
            else:
                decrease_amount = self.gray_water_amount
                new_level = max(self.pure_h2o_level - decrease_amount, 0)
                decrease = self.pure_h2o_level - new_level
                self.pure_h2o_level = new_level

            # Calculate the reset value after decrease cycles using reset_factor passed from the main loop
            self.reset_value_after_decrease = self.initial_capacity - self.reset_factor / self.total_conversion_rate * self.pure_h2o_capacity
            self.decrease_counter += 1

            # After decreasing for the set cycles, reset
            if self.reset_value_after_decrease is not None:
                self.pure_h2o_level = self.reset_value_after_decrease
        else:
            # After decrease cycles, behave normally
            available_capacity = self.capacity - self.pure_h2o_level
            added = min(gray_amount, available_capacity)
            self.pure_h2o_level += added

        return self.pure_h2o_level

    def transfer_to_oxygen_recovery(self, amount, oxygen_recovery_processor=None):
        transferable = min(amount, self.pure_h2o_level)
        if transferable <= 0:
            return 0

        self.pure_h2o_level -= transferable
        if oxygen_recovery_processor:
            if hasattr(oxygen_recovery_processor, 'receive_pure_water'):
                accepted = oxygen_recovery_processor.receive_pure_water(transferable)
                return accepted
        return 0

    def get_status(self):
        return {
            "Current Water Level": self.pure_h2o_level,
            "Tank Capacity": self.capacity
        }



    def drain_tank(self):
        self.pure_h2o_level = 0
        return "Tank is now empty."
