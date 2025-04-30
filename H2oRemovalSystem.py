import numpy as np

# Define a class for the VAPOR H2O removal system
class  H2oRemovalSystem:
    def __init__(self, removal_rate):
        self.removal_rate = removal_rate

    def remove_h2o(self, h2o_level):
        h2o_removed = min(h2o_level, self.removal_rate)
        return h2o_removed