import numpy as np

class SabatierSeparator:
    conversion_rates = {
        "carbon": 0.30,   # Carbon produced per mole of CO2 consumed (grams per mole)
        "methane": 0.40,  # CH4 production rate (grams per mole)
        "hydrogen": 0.10, # H2 consumption rate (grams per mole)
              
    }
    def __init__(self, h2_capacity=10.0, methane_capacity=10.0, carbon_capacity=10.0, outside=None, co2_to_h2o=None):
        self.h2_capacity = h2_capacity
        self.methane_capacity = methane_capacity
        self.carbon_capacity = carbon_capacity
        
        # Initial capacities
        self.h2_amount = 0.0
        self.carbondioxide_amount = 0.0
        self.methane_amount = 0.0 
        self.carbon_stored = 0.0  
        self.export_counter = 0  # Add a counter for export frequency
        self.total_cycles = 0
    
        self.co2_to_h2o = co2_to_h2o  # Reference to the CarbonDioxideToH2O system
        self.export_counter = 0  # Counts cycles
        self.export_threshold = 7 # First export happens after 7 cycles, then every 2 cycle (assume for starting point)
        self.methane_export_interval= 6 # First export happens after 6 cycles, then every 2 cycle (assume for starting point)
        self.methane_export_counter = 0 
        self.outside = outside
        # Initial values for exception cycle intervals
        self.next_repeat_cycle = 79  # First exception after 79 cycles
        self.repeat_interval = 79  # First exception interval
        self.first_exception = True  # Flag to track if it's the first exception
         
    def receive_methane(self, methane_received): #Receive methane from the CO₂ --> H₂O system.
        self.methane_amount = methane_received

    def process_methane(self):
        entering_carbon = 0
        entering_hydrogen = 0
        self.total_cycles += 1

        # Check repeat cycles
        if self.total_cycles == self.next_repeat_cycle:
            methane_to_process = min(self.methane_amount, self.methane_capacity)
            
            # Convert methane
            carbon_extracted = methane_to_process * (self.conversion_rates["carbon"] / self.conversion_rates["methane"])
            hydrogen_recovered = methane_to_process * (self.conversion_rates["hydrogen"] / self.conversion_rates["methane"])

            # Update internal storage
            self.methane_amount -= methane_to_process
            self.carbon_stored += carbon_extracted

            # Pass hydrogen to CO2 to H2O 
            if self.co2_to_h2o:
                self.co2_to_h2o.receive_hydrogen(hydrogen_recovered)

            # After first exception, reduce the interval to 73
            if self.first_exception:
                self.repeat_interval = 73  # First decrease after 79 cycles
                self.first_exception = False
            else:
                # After the first exception, repeat every 73 cycles
                self.repeat_interval = 73

            self.next_repeat_cycle += self.repeat_interval  # Schedule next repeat based on fixed 73 interval

            return methane_to_process, hydrogen_recovered, carbon_extracted, hydrogen_recovered,entering_carbon, entering_hydrogen

        # Normal processing for cycles 
        if self.methane_amount == 0:
            # No methane to process, return no reaction
            return 0, 0, 0, 0 ,0 # No reaction if no methane

        # Process methane and extract hydrogen and carbon
        methane_to_process = min(self.methane_amount, self.methane_capacity)

        entering_methane = 0

        # Convert methane
        carbon_extracted = methane_to_process * (self.conversion_rates["carbon"] / self.conversion_rates["methane"])
        hydrogen_recovered = methane_to_process * (self.conversion_rates["hydrogen"] / self.conversion_rates["methane"])

        # Update internal storage
        self.methane_amount -= methane_to_process
        self.carbon_stored += carbon_extracted

        if self.co2_to_h2o:
            self.co2_to_h2o.receive_hydrogen(hydrogen_recovered)

        self.export_counter += 1
        if self.export_counter >= self.export_threshold:
            self.export_carbon(methane_to_process, hydrogen_recovered)
            self.export_counter = 0
            self.export_threshold = 2  # After first export, export every 2 cycles

        self.methane_export_counter += 1
        if self.methane_export_counter >= self.methane_export_interval:
            entering_methane = methane_to_process
            self.methane_export_counter = 4
        else:
            entering_methane = 0

        return entering_methane, hydrogen_recovered, carbon_extracted, hydrogen_recovered,entering_carbon, entering_hydrogen

    def export_carbon(self, entering_methane, hydrogen_recovered):
        if self.outside and self.carbon_stored > 0:
            # Calculate export amount for carbon
            methane_reaction = entering_methane - hydrogen_recovered
            export_amount = min(self.carbon_stored, methane_reaction)
            self.outside.receive_carbon(export_amount)
            self.carbon_stored -= export_amount 
            
    
    def get_carbon_level(self):
        return self.carbon_stored
    
   
    def get_methane_level(self):
        return self.methane_amount