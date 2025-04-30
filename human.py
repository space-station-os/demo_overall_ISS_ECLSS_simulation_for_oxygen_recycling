
import numpy as np
#Define constants
# Human Breathing /Crew : 1 human 
#Model is based on the Daily Human Metabolic Load Profile, originally developed by NASA for their Crew Exploration program
#Life Support Baseline Values and Assumptions Document/February 2022

class Human:
    def __init__(self):
        self.co2_production_rate = 1.085  # kg/day Out  
        self.o2_consumption_rate = 0.895# kg/day  In 
        self.vapor_h2o_production_rate = 2.946 # kg/day out  
        self.o2_production_rate = 0  # kg/day (human do not produce oxygen)
        self.co2_consumption_rate = 0  # kg/day (human do not comsume carbondioxide)
        self.vapor_h2o_consumption_rate = 0  # kg/day (human do not comsume vapor water)
        self.o2_initial_rate = 5  # kg/day (Start point human breathing)
        self.o2_remain = self.o2_initial_rate  # kg/day
        self.co2 = {"initial": 0, "capacity": 5}
        self.o2 = {"initial": 5, "capacity": 5}
        self.vapor_h2o = {"initial": 0, "capacity": 10}

    def update_o2(self, o2_transferred):
        self.o2_remain += self.o2_initial_rate +o2_transferred
        # Ensure oxygen level does not exceed human's capacity or drop below zero
        self.o2_remain = max(0, min(self.o2_remain, self.o2["capacity"]))
        
    def __str__(self):
        return f"CO2: {self.co2['initial']}/{self.co2['capacity']} | O2: {self.o2_remain}/{self.o2['capacity']} | Vapor H2O: {self.vapor_h2o['initial']}/{self.vapor_h2o['capacity']}"