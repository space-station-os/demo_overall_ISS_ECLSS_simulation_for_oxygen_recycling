import numpy as np


class GrayH2oToPureH2oRecyclingProcessor:
    def __init__(self, initial_gray_h2o=0, capacity_gray_h2o=50, initial_pure_h2o=0, capacity_pure_h2o=10, co2_to_h2o=None):
        self.gray_h2o_level = initial_gray_h2o
        self.pure_h2o_level = initial_pure_h2o
        self.capacity_gray_h2o = capacity_gray_h2o
        self.capacity_pure_h2o = capacity_pure_h2o
        self.conversion_rate = 3  # 3 kg gray H₂O → 3 kg pureH₂O
        self.vapor_conversion_rate = 2.946
        self.total_gray_water_received = 0
        self.total_pure_water_produced = 0
        self.total_gray_h2o_from_co2 = 0
        self.total_gray_h2o_from_tank = 0
        self.co2_to_h2o = co2_to_h2o
        self.total_pure_h2o_from_vapor = 0
        self.total_pure_h2o_from_co2 = 0
        self.co2_gray_conversion_rate=0.90


    def convert_vapor_h2o_to_gray_h2o(self, vapor_h2o_amount):
        converted_gray_h2o = vapor_h2o_amount 
        actual_added = self.receive_gray_water(converted_gray_h2o, 0.0)
        return actual_added

    def convert_co2_to_h2o(self):
        if self.co2_to_h2o and hasattr(self.co2_to_h2o, 'gray_water_amount'):
            converted_gray_h2o_co2 = self.co2_to_h2o.gray_water_amount     
            added_gray_h2o = self.receive_gray_water(0.0, converted_gray_h2o_co2)
            return added_gray_h2o
        return 0


    def receive_gray_water(self, convert_vapor_h2o_to_gray_h2o=0.0, convert_co2_to_h2o=0.0):
     total_input = convert_vapor_h2o_to_gray_h2o + convert_co2_to_h2o
     available_capacity = self.capacity_gray_h2o - self.gray_h2o_level

     if total_input > 0:
        gray_water_to_add = min(total_input, available_capacity)
     else:
        gray_water_to_add = max(total_input, -self.gray_h2o_level)

     if gray_water_to_add == 0:
        return 0

     if total_input > 0:
        tank_fraction = (convert_vapor_h2o_to_gray_h2o / total_input)
        co2_fraction = convert_co2_to_h2o / total_input
     else:
        tank_fraction = co2_fraction = 0

     self.total_gray_water_received += gray_water_to_add
     self.total_gray_h2o_from_tank += gray_water_to_add * tank_fraction
     self.total_gray_h2o_from_co2 += gray_water_to_add * co2_fraction

    # Adjust the gray water level (increase or decrease)
     self.gray_h2o_level += gray_water_to_add

    # Ensure the gray water level doesn't go negative
     if self.gray_h2o_level < 0:
        self.gray_h2o_level = 0
     return gray_water_to_add

    def remove_gray_water(self, convert_vapor_h2o_to_gray_h2o=0.0, convert_co2_to_h2o=0.0):
     total_output = convert_vapor_h2o_to_gray_h2o + convert_co2_to_h2o
     available_level = self.capacity_gray_h2o - self.gray_h2o_level

     if total_output <= 0:
        return 0

     gray_water_to_remove = min(total_output, available_level)
     self.total_gray_water_received -= gray_water_to_remove

    # Ensure the level does not go negative
     if self.gray_h2o_level < 0:
        self.gray_h2o_level = 0 
     return gray_water_to_remove

    def execute_purification(self, convert_vapor_h2o_to_gray_h2o=0.0):
        # Total gray water that can be purified - sum of both sources
        total_gray_to_convert = convert_vapor_h2o_to_gray_h2o + self.total_gray_h2o_from_co2

        if total_gray_to_convert <= 0:
            return 0

        # Corrected vapor H₂O conversion to pure H₂O
        corrected_vapor_pure = convert_vapor_h2o_to_gray_h2o * (self.conversion_rate / self.vapor_conversion_rate)  # Full conversion of vapor H₂O to Gray H₂O
        corrected_co2_pure = self.total_gray_h2o_from_co2 * (self.conversion_rate / self.co2_gray_conversion_rate)  # Full conversion of CO₂
        total_corrected_pure = corrected_vapor_pure + corrected_co2_pure

        # Ensure we respect the remaining capacity in the pure water tank
        max_convertible_pure = min(self.capacity_pure_h2o, total_corrected_pure)
        if max_convertible_pure <= 0:
            return 0

        if total_corrected_pure > 0:
            vapor_fraction = corrected_vapor_pure / total_corrected_pure
            co2_fraction = corrected_co2_pure / total_corrected_pure
        else:
            vapor_fraction = co2_fraction = 0

        # Calculate actual pure water contribution from each source
        pure_from_vapor = max_convertible_pure * vapor_fraction
        pure_from_co2 = max_convertible_pure * co2_fraction

        # Convert back to the required gray input used
        used_gray_from_vapor = pure_from_vapor
        used_gray_from_co2 = pure_from_co2  # 1:1 ratio

        # Ensure only the available gray water is used and does not exceed available levels
        if used_gray_from_vapor > self.total_gray_h2o_from_tank:
            used_gray_from_vapor = self.total_gray_h2o_from_tank
            pure_from_vapor = used_gray_from_vapor * (self.conversion_rate / self.vapor_conversion_rate)

        if used_gray_from_co2 > self.total_gray_h2o_from_co2:
            used_gray_from_co2 = self.total_gray_h2o_from_co2
            pure_from_co2 = used_gray_from_co2  # Full 1:1 conversion

        # Update levels
        self.pure_h2o_level += max_convertible_pure
        self.total_pure_water_produced += max_convertible_pure
        self.total_pure_h2o_from_vapor += pure_from_vapor
        self.total_pure_h2o_from_co2 += pure_from_co2

        # Decrease gray water levels based on the purification
        self.total_gray_h2o_from_tank -= used_gray_from_vapor
        self.total_gray_h2o_from_co2 -= used_gray_from_co2
        self.gray_h2o_level -= (used_gray_from_vapor + used_gray_from_co2)

        # Ensure levels don't go negative
        self.total_gray_h2o_from_tank = max(0, self.total_gray_h2o_from_tank)
        self.total_gray_h2o_from_co2 = max(0, self.total_gray_h2o_from_co2)
        self.gray_h2o_level = max(0, self.gray_h2o_level)

        return max_convertible_pure

    def transfer_pure_h2o_to_tank(self, pure_h2o_tank, purified_amount):
     available_capacity = pure_h2o_tank.capacity - pure_h2o_tank.pure_h2o_level
     transferable = min(purified_amount, available_capacity) 

    # Perform the transfer
     pure_h2o_tank.receive_pure_water(transferable)

    # Reduce only the transferred amount from internal level
     self.pure_h2o_level -= transferable
     return transferable
     
    def get_pure_water(self):
      retrieved = 0
      self.pure_h2o_level = 0
      return retrieved

    def get_total_gray_water_received(self):
        return self.total_gray_water_received

    def get_total_pure_water_produced(self):
        return self.total_pure_water_produced

    def get_status(self):
        return {
            "Gray H2O Level": self.gray_h2o_level,
            "Pure H2O Level": self.pure_h2o_level,
        }


