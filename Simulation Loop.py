import numpy as np
import csv
from datetime import datetime, timedelta # For time
import pytz  # For timezone

#Import libraries 
from human import Human
from OxygenTank import OxygenTank
from CarbonDioxideSeparator import CarbonDioxideSeparator
from CarbonDioxideToH2O import CarbonDioxideToH2O
from CO2RemovalSystem import CO2RemovalSystem
from GrayH2oToPureH2oRecyclingProcessor import GrayH2oToPureH2oRecyclingProcessor
from H2oRemovalSystem import H2oRemovalSystem
from HumanResourceTank import HumanResourceTank
from OxygenRecoveryProcessor import OxygenRecoveryProcessor
from OxygenTank import OxygenTank
from SabatierSeparator import SabatierSeparator
from WaterTankSmall import WaterTankSmall
from Outside import Outside
#Model is based on the Daily Human Metabolic Load Profile, originally developed by NASA for their Crew Exploration program
#Life Support Baseline Values and Assumptions Document/February 2022
#Simulation for 1 human/Human Breathing 

# Initialize

human = Human ()
hours_per_day = 24
tank_cumulative = 0.0
gray_from_vapor = 0.0
convert_co2_to_h2o=0.0
hydrogen_recovered=0.0
pure_water_received=0.0
amount_transferred=0.0
reset_factor_value = 0.0  

# Tank Capacities 
vapor_h2o_removal_rate_per_hour=0.0
human_tank = HumanResourceTank(co2_initial=0, co2_capacity=10, o2_initial=10, o2_capacity=10, vapor_h2o_initial=0, vapor_h2o_capacity=10, gray_h2o_initial=0, gray_h2o_capacity=10)
oxygen_tank = OxygenTank(initial_o2=100, capacity=150, human_tank=human_tank, decrease_cycles=721, increase_cycles=1, reset_value_initial=None,consumption_rate_per_hour=  human.o2_consumption_rate/ hours_per_day)  # Pass the reset factor here) # kg
pure_h2o_tank = WaterTankSmall(50.0, 500.0,  decrease_cycles=1, reset_value_after_decrease=None,  reset_factor=reset_factor_value)  # kg


# Convert rates -changes: per day to per hour # Results wil be shown in hours.
co2_production_rate_per_hour = human.co2_production_rate / hours_per_day  # kg/hour
oxygen_consumption_rate_per_hour = human.o2_consumption_rate / hours_per_day  # kg/hour
oxygen_initial_rate_per_hour = human.o2_initial_rate / hours_per_day  # kg/hour
vapor_h2o_production_rate_per_hour = human.vapor_h2o_production_rate / hours_per_day  # kg/hour

# Initialize the oxygen production system
oxygen_transfer_rate_per_hour = oxygen_consumption_rate_per_hour * 1  # 1kg 
# Adjust CO₂_removal_rate for human tank 
co2_removal_rate_per_hour = co2_production_rate_per_hour * 1  # 1kg
co2_removal_system = CO2RemovalSystem(co2_removal_rate_per_hour * hours_per_day)  # kg/day

#Adjust H₂O_production_system for human tank
vapor_h2o_removal_rate_per_hour = vapor_h2o_production_rate_per_hour * 1  # 1kg per hour
vapor_h2o_removal_system = H2oRemovalSystem(vapor_h2o_removal_rate_per_hour )  # kg/day

#Initializate Carbon Dioxide Separator 
co2_separator_device = CarbonDioxideSeparator(0.0,10.0)  # kg


#Initialize the grayH₂O to pureH₂O recycling processor 
gray_h2o_processor = GrayH2oToPureH2oRecyclingProcessor (initial_gray_h2o=0, capacity_gray_h2o=50, initial_pure_h2o=0, capacity_pure_h2o=10 )  # kg

#Initialize the co2_to_h2o processor
co2_to_h2o = CarbonDioxideToH2O()  #kg

#Initialize the oxygen recovery processor 
oxygen_recovery_processor = OxygenRecoveryProcessor(oxygen_tank=oxygen_tank, co2_to_h2o=co2_to_h2o)   # kg

# Initialize Outside
outside = Outside()  #kg

#Iniitialize sabatier separator
sabatier_separator = SabatierSeparator(co2_to_h2o=co2_to_h2o,outside=outside)  #kg

# Create  headers (for CSV files)
with open('Module.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Time', 
                    'O2  (kg)',   # Human_tank OXYGEN convertor 
                    'CO2  (kg)',   # Human_tank CARBON DIOXIDE convertor
                    'VAPOR_H2O  (kg)',  # Human_tank VAPOR WATER convertor
                    'GRAY_H2O (kg)'])  

with open('Oxygen_tank.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Time', 
                     'Oxygen Tank Capacity (kg)']) # Tank level
                                     
with open('Human.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Time',                     
                    'co2_received (kg/day)',    
                    'O2_consumption (kg/day)',     # To human
                    'H2O_received (kg/day)' ,          ])                  
                             
with open('Gray_h2o_pure_h2o_recycling_processor.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Time',                     
                    'gray_h2o (kg/day)',    
                    'pure_h2o(kg/day)',        ])          
                                    
with open('Oxygen_recovery_processor.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Time',                     
                    'pure_h2o (kg/day)',    
                    'H2 (kg/day)',    
                    'O2 (kg/day)',           ])   
      
with open('CarbonDioxide_Separator.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Time',                     
                    ' CO2(kg/day)',            ])          
                      
with open('CarbonDioxide_to_H2o.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Time',                     
                    'CO2 (kg/day)',    
                    'H2(kg/day)',    
                    'CH4 (kg/day)' ,
                    'Gray_h2o (kg/day)'])   
                                   
with open('Sabatier2.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Time',                     
                    'CH4(kg/day)',    
                    'H2(kg/day)',    
                    'C (kg/day)' ,  ])   

with open('h2o_tank_small.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Time',                        
                     'pure_h2o_tank(kg/day)' ,        ]) 
                 
with open('Outside.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Time',                        
                     'O2' ,
                     'CO2(kg/day)',    
                     'vapor_H2O_received (kg/day)',    
                     'CH4 (kg/day)' ,
                     'C(kg/day)',    
                     'gray_h2o (kg/day)' ,        ]) 

# Simulate for 30 days > - > changes up to the user 

start_time = datetime.now(pytz.utc)
for hour in range(0,720):  # 30 days * 24 hours = 720 hours
    # Get current UTC time
    current_time = (start_time + timedelta(hours=hour)).strftime(' %Y-%m-%d %H:%M ' )
    h2o_produced = 0.0

    # Human produces CO₂ and needs O₂
    # CO₂ handling: Human --> Human Tank [for Carbon Dioxide]
    co2_produced = co2_production_rate_per_hour
    human_tank.new_co2_level(co2_produced, 0)
    
    # Transfer CO₂ from Human Tank to CO₂ Separator
    co2_transferred =  human_tank.transfer_co2(co2_produced)
    co2_separator_device.receive_co2(co2_transferred)
    co2_removed = co2_removal_system.remove_co2(co2_transferred)
    # CO₂  is sent to the CarbonDioxideToH2O processor
    co2_to_h2o.receive_co2(co2_transferred) 
   
    # H₂O handling: Human  -->  Human Tank [for gray H₂O]
    human_tank.new_vapor_h2o_level(vapor_h2o_removal_rate_per_hour)
    # Initializing gray_h2o_module to 0 to start with no gray H₂O in the Human Tank
    initial_gray_h2o = 0
    vapor_h2o_to_convert = human_tank.new_vapor_h2o_level(vapor_h2o_removal_rate_per_hour)  # Adjust H₂O level 
    gray_from_vapor = max(vapor_h2o_to_convert, 0.0)
    
    # Gray Recycling processor water purification  (entered from the Human Tank)  
    amount= gray_h2o_processor.execute_purification(convert_vapor_h2o_to_gray_h2o = vapor_h2o_production_rate_per_hour)
    decrease=pure_water_received-co2_to_h2o.gray_water_amount
    produced_pure =amount-co2_to_h2o.gray_water_amount
    # Calculate GrayH₂O amount derived from the two sources [tank, CO₂TOH₂O]
    pure_water_received = amount
    remove_water=pure_water_received-vapor_h2o_production_rate_per_hour
    
    #Perfoms GrayH2o
    if 1 <= hour <= 2:
    # Only vapor water is used
     gray_h2o_processor.receive_gray_water(
        convert_vapor_h2o_to_gray_h2o=vapor_h2o_production_rate_per_hour,
        convert_co2_to_h2o=0.0
    )
   
    elif 3 <= hour <= 4:
    # Decrease gray water in hours 3-5
 
        gray_h2o_processor.remove_gray_water(
            convert_vapor_h2o_to_gray_h2o=remove_water,
            convert_co2_to_h2o=0.0
        )

    elif hour == 5:
    # Only CO₂ gray water used
     tank_cumulative -= convert_co2_to_h2o
     gray_h2o_processor.receive_gray_water(
        convert_vapor_h2o_to_gray_h2o=0.0,
        convert_co2_to_h2o=convert_co2_to_h2o-(pure_water_received-vapor_h2o_production_rate_per_hour)
    )

    if hour <= 76:
    # Original pattern logic
     if hour >= 6:
        # Alternate manually starting from hour 6
        if (hour - 6) % 2 == 0:
            # Even-indexed hours after 6: remove gray water
            gray_h2o_processor.remove_gray_water(
                convert_vapor_h2o_to_gray_h2o=remove_water,
                convert_co2_to_h2o=0.0
            )
        else:
            # Odd-indexed hours after 7: use CO2-derived water
            tank_cumulative -= convert_co2_to_h2o
            gray_h2o_processor.receive_gray_water(
                convert_vapor_h2o_to_gray_h2o=0.0,
                convert_co2_to_h2o=convert_co2_to_h2o - (pure_water_received - vapor_h2o_production_rate_per_hour)
            )
    elif hour >= 77 and hour <= 149:
    # Reset pattern logic for hours > 77
     reset_hour = hour - 77  # Treat hour 77 as hour 1, hour 78 as hour 2, etc.

    
     if reset_hour >= 0:
        # Alternate manually 
        if (reset_hour - 6) % 2 == 0:
            # Even-indexed hours after reset: remove gray water
     
            gray_h2o_processor.remove_gray_water(
                convert_vapor_h2o_to_gray_h2o=remove_water,
                convert_co2_to_h2o=0.0
            )
        else:
            # Odd-indexed hours after reset: use CO2-derived water
            tank_cumulative -= convert_co2_to_h2o
            gray_h2o_processor.receive_gray_water(
                convert_vapor_h2o_to_gray_h2o=0.0,
                convert_co2_to_h2o=convert_co2_to_h2o - (pure_water_received - vapor_h2o_production_rate_per_hour)
            )
    
    elif hour >= 150 and hour <= 222:
     reset_hour = hour - 150  # Treat hour 151 as hour 1, hour 152 as hour 2, etc.   
     if reset_hour >= 0:
        # Alternate manually
        if (reset_hour - 6) % 2 == 0:
            gray_h2o_processor.remove_gray_water(
                convert_vapor_h2o_to_gray_h2o=remove_water,
                convert_co2_to_h2o=0.0
            )
        else:
            tank_cumulative -= convert_co2_to_h2o
            gray_h2o_processor.receive_gray_water(
                convert_vapor_h2o_to_gray_h2o=0.0,
                convert_co2_to_h2o=convert_co2_to_h2o - (pure_water_received - vapor_h2o_production_rate_per_hour)
            )
            
    elif hour >= 223 and hour <= 295:
      reset_hour = hour - 223  
    
      if reset_hour >= 0:
        if (reset_hour - 6) % 2 == 0:
            gray_h2o_processor.remove_gray_water(
                convert_vapor_h2o_to_gray_h2o=remove_water,
                convert_co2_to_h2o=0.0
            )
        else:
            tank_cumulative -= convert_co2_to_h2o
            gray_h2o_processor.receive_gray_water(
                convert_vapor_h2o_to_gray_h2o=0.0,
                convert_co2_to_h2o=convert_co2_to_h2o - (pure_water_received - vapor_h2o_production_rate_per_hour)
            )
    
    elif hour >= 296 and hour <= 368:
      reset_hour = hour - 296  
      if reset_hour >= 0:
        if (reset_hour - 6) % 2 == 0:
            gray_h2o_processor.remove_gray_water(
                convert_vapor_h2o_to_gray_h2o=remove_water,
                convert_co2_to_h2o=0.0
            )
        else:
            tank_cumulative -= convert_co2_to_h2o
            gray_h2o_processor.receive_gray_water(
                convert_vapor_h2o_to_gray_h2o=0.0,
                convert_co2_to_h2o=convert_co2_to_h2o - (pure_water_received - vapor_h2o_production_rate_per_hour)
            )
            
    elif hour >= 369 and hour <= 441:
      reset_hour = hour - 369  
      if reset_hour >= 0:
        if (reset_hour - 6) % 2 == 0:
            gray_h2o_processor.remove_gray_water(
                convert_vapor_h2o_to_gray_h2o=remove_water,
                convert_co2_to_h2o=0.0
            )
        else:
            tank_cumulative -= convert_co2_to_h2o
            gray_h2o_processor.receive_gray_water(
                convert_vapor_h2o_to_gray_h2o=0.0,
                convert_co2_to_h2o=convert_co2_to_h2o - (pure_water_received - vapor_h2o_production_rate_per_hour)
            )   
            
            
    elif hour >= 442 and hour <= 514:
      reset_hour = hour - 442  
    
      if reset_hour >= 0:
        if (reset_hour - 6) % 2 == 0:
            gray_h2o_processor.remove_gray_water(
                convert_vapor_h2o_to_gray_h2o=remove_water,
                convert_co2_to_h2o=0.0
            )
        else:
            tank_cumulative -= convert_co2_to_h2o
            gray_h2o_processor.receive_gray_water(
                convert_vapor_h2o_to_gray_h2o=0.0,
                convert_co2_to_h2o=convert_co2_to_h2o - (pure_water_received - vapor_h2o_production_rate_per_hour)
            )   
                   
    elif hour >= 515 and hour <= 587:
      reset_hour = hour - 515  
    
      if reset_hour >= 0:
        if (reset_hour - 6) % 2 == 0:
            gray_h2o_processor.remove_gray_water(
                convert_vapor_h2o_to_gray_h2o=remove_water,
                convert_co2_to_h2o=0.0
            )
        else:
            tank_cumulative -= convert_co2_to_h2o
            gray_h2o_processor.receive_gray_water(
                convert_vapor_h2o_to_gray_h2o=0.0,
                convert_co2_to_h2o=convert_co2_to_h2o - (pure_water_received - vapor_h2o_production_rate_per_hour)
            )   
                 
    elif hour >= 588 and hour <= 660:
      reset_hour = hour - 588  
      if reset_hour >= 0:
        if (reset_hour - 6) % 2 == 0:
            gray_h2o_processor.remove_gray_water(
                convert_vapor_h2o_to_gray_h2o=remove_water,
                convert_co2_to_h2o=0.0
            )
        else:
            tank_cumulative -= convert_co2_to_h2o
            gray_h2o_processor.receive_gray_water(
                convert_vapor_h2o_to_gray_h2o=0.0,
                convert_co2_to_h2o=convert_co2_to_h2o - (pure_water_received - vapor_h2o_production_rate_per_hour)
            )   
    else:
      reset_hour = hour - 661  
    
      if reset_hour >= 0:
        if (reset_hour - 6) % 2 == 0:
            gray_h2o_processor.remove_gray_water(
                convert_vapor_h2o_to_gray_h2o=remove_water,
                convert_co2_to_h2o=0.0
            )
        else:
            tank_cumulative -= convert_co2_to_h2o
            gray_h2o_processor.receive_gray_water(
                convert_vapor_h2o_to_gray_h2o=0.0,
                convert_co2_to_h2o=convert_co2_to_h2o - (pure_water_received - vapor_h2o_production_rate_per_hour)
            )             
                
    
    entered_pure_water=0
    
    # Gray Recycling processor water purification  (entered from the CO₂TOH₂O system)  
    produce_co2_gray=gray_h2o_processor.execute_purification(convert_vapor_h2o_to_gray_h2o=convert_co2_to_h2o)
    # Get the amount of pure water produce from both resources and transfer neccesary level to the small water tank 
    pure_h2o_tank.reset_factor = reset_factor_value  # Pass the new factor to the tank
    entered_water=gray_h2o_processor.transfer_pure_h2o_to_tank(pure_h2o_tank,decrease)
    amount_transferred = pure_water_received- decrease
    reset_factor_value =amount_transferred
    pure_h2o_tank.reset_factor = reset_factor_value  # Pass the new factor to the tank
 
    #Tranfer pure water from the small water tank to the Oxygen Recovery Processor 
    pure_water_total=oxygen_recovery_processor.receive_pure_water(amount_transferred)
    #Make sure the transferred pure water came from both tank + CO₂TOH₂O system
    total_pure_water = gray_h2o_processor.get_total_pure_water_produced()  
    #Only tranfer neccesary amount of pure water  
    h2o_produced = oxygen_recovery_processor.pure_h2o_amount
    # Transfer pureH₂O from the Water Small Tank to the  OxygenRecoveryProcessor --> --> pure water transformed in the Oxygen Recovery Processor to produce oxygen and Hydrogen
    hydrogen_produced, oxygen_recovered,transferred_oxygen = oxygen_recovery_processor.extract_hydrogen()
    oxygen_for_tank=oxygen_recovered
    co2_to_h2o.receive_hydrogen(hydrogen_produced)
    # COMEBACK: SIMULATION LOOP : O₂ handling loop: O₂ Tank -> Human Tank -> Human
    o2_level,total_transferred_o2= oxygen_tank.transfer_o2(oxygen_recovery=oxygen_for_tank)
    human_tank.transfer_o2_to_human(human,oxygen_consumption_rate_per_hour) 

    #Sabatier Reaction will be handle
    methane, gray_water, co2_to_h2o.methane_amount, co2_to_h2o.gray_water_amount, co2_exported, h2_used,  co2_used, co2_to_h2o.incremental_h2_growth= co2_to_h2o.perform_sabatier_reaction()
    convert_co2_to_h2o = co2_to_h2o.gray_water_amount  #Value derived from CO₂ processing-- CO₂TOH₂O system to be calculate after oxygen recovery processor-the system it is a loop 
    # Set Sabatier separator to the CO₂-H₂O processor
    co2_to_h2o.sabatier_processor = sabatier_separator
    pure_h2o_tank.manually_run_initial_cycle(gray_amount=  convert_co2_to_h2o)
    #After come back from the CO₂-H₂O processor -->  sabatier sabatier receives  CH₄ and H₂
    sabatier_separator.receive_methane(co2_to_h2o.methane_amount)
    entering_methane, hydrogen_recovered, carbon_extracted, hydrogen_recovered,entering_carbon, entering_hydrogen=sabatier_separator.process_methane()
   
    # Add hydrogen and CO₂ to the system ---> the process come back from the Gray H₂O (Handling CO₂-H₂O &  CH₄)
    hydrogen_sabatier = co2_to_h2o.receive_hydrogen(hydrogen_recovered)  # Receive hydrogen for processing in the CO₂TOH₂O system


   # create CSV files
    with open('Module.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow ([
            current_time, 
            round(human_tank.o2_level , 6),
            round(co2_transferred , 6),
            round(human_tank.vapor_h2o_level, 6),
            round(initial_gray_h2o, 6),
         ])    
    
    with open('Oxygen_tank.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([  
            current_time,                  
            round(oxygen_recovery_processor.oxygen_tank.get_o2_level(), 6),       
         ])         

    with open('Human.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([   
          current_time,
            round(human.co2_consumption_rate , 6),  #co2
            round(human.o2_remain, 6),  #o2
            round(human.vapor_h2o_consumption_rate , 6), #vapor_h2o      
        ])    
    with open('Gray_h2o_pure_h2o_recycling_processor.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([   
          current_time,
            round(gray_h2o_processor.get_total_gray_water_received() , 6),   # total gray water entering to the recycling processor
            round(gray_h2o_processor.get_pure_water(), 6),                   # total pure water before purification execution       
        ]) 

    with open('Oxygen_recovery_processor.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([   
          current_time,
            round( h2o_produced, 6),
            round(oxygen_recovery_processor.get_entering_hydrogen(), 6), 
            round(oxygen_recovery_processor.get_entering_oxygen(), 6),      
             
        ])  
        
    with open('CarbonDioxide_Separator.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([   
           current_time,
            round(co2_separator_device.get_current_co2_level(), 6),   #co2 
        ])        
          
    with open('CarbonDioxide_to_H2o.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([   
           current_time,
            round(co2_exported, 6),  #co2
            round(co2_to_h2o.incremental_h2_growth, 6), #h2
            round(methane, 6),                          #ch4 initial 
            round(gray_water , 6),                       #gray h2o initial
        ])  
  
    with open('Sabatier2.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([   
           current_time,
           round(entering_methane, 6),  
            round(entering_hydrogen, 6),  
            round(entering_carbon, 6),      
        ])   

    with open('h2o_tank_small.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([   
           current_time,
           round (pure_h2o_tank.pure_h2o_level, 6),   
        ])  
            
    with open('Outside.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([   
           current_time,
            round(outside.oxygen_amount, 6),   
            round(outside.carbondioxide_amount, 6),  
            round(outside.vaporh2o_amount, 6), 
            round(outside.methane_amount, 6), 
            round(outside.carbon_storage, 6), 
            round(outside.grayh2o_amount, 6),  
        ]) 
        
   
