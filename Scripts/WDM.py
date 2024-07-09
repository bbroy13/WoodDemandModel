import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import dynamic_stock_model as dsm
import seaborn as sns

# Load in datasets (update the path to your data directory)
path = 'C:\\Users\\bbroy\\OneDrive - UBC\\PhD poposal\\Dynamic MFA of buildings\\Bldg_Stock-master\\Bldg_Stock-master\\InputData\\' 
RECS_Weights = pd.read_csv(path +'RECS_Area_weights.csv')
CBECS_Area = pd.read_csv(path+'CBECS_Area.csv')
CBECS_Weights = pd.read_csv(path+'RECS_Area_weights.csv')
data_pop = pd.read_csv(path+'CAN_pop_forecast.csv')
energy_requirement= pd.read_csv(path+'E_requirement.csv')

# Define common parameters
year1 = 1900
year2 = 2100
years = np.linspace(year1, year2, num=(year2-year1+1), endpoint=True)
BldgLife_mean = 57.23
myLT = {'Type': 'Weibull', 'Shape': np.array([1.9]), 'Scale': np.array([BldgLife_mean])}

# Wood Material Density (kg/m^2) per Building Type
Mat_density = {
    "Single-detached": 53.48, 
    "High-rise": 25.17,
    "Low-mid-rise": 25.17,
    "Others": 163.0,  
}
building_types = ["Single-detached", "High-rise", "Low-mid-rise", "Others"]
proportions = [0.536, 0.099, 0.18, 0.185]

# Initialize dictionaries to store results for each building type and scenario
building_inflow_results = {bldg_type: {} for bldg_type in building_types}

# Define scenarios for FA_elasticity_res
scenarios = {
    "Original": 42.87,
    "Reduced": 30.0
}

# Loop through scenarios
for scenario_name, FA_elasticity_res in scenarios.items():

    # Get population data 
    CAN_pop = interp1d(data_pop.Year, data_pop.SSP2, kind='cubic')(years)
    FA_stock = CAN_pop * FA_elasticity_res

    # Calculate initial stock for each building type
    S_0_res_2020_by_type = {}
    for i, bldg_type in enumerate(building_types):
        S_0_res_2020_by_type[bldg_type] = np.flipud(RECS_Weights.Res_Weight * CAN_pop[115] * FA_elasticity_res * proportions[i])

    for bldg_type in building_types:
        # Stock for specific building type
        FA_stock_type = FA_stock * proportions[building_types.index(bldg_type)]
        
        # Dynamic Stock Model (per building type)
        US_Bldg_DSM = dsm.DynamicStockModel(t=years, s=FA_stock_type, lt=myLT)
        US_Bldg_DSM.dimension_check()
        
        S_C = US_Bldg_DSM.compute_evolution_initialstock(InitialStock=S_0_res_2020_by_type[bldg_type], SwitchTime=116)
        S_C, O_C, I = US_Bldg_DSM.compute_stock_driven_model()
        O = US_Bldg_DSM.compute_outflow_total()
        
        # Calculate cumulative inflow
        cumulative_inflow = np.cumsum(I)
        
        # Store results
        building_inflow_results[bldg_type][scenario_name] = cumulative_inflow

# Calculate percentage reduction in cumulative inflow
percent_reduction = {}
for bldg_type in building_types:
    original_inflow = building_inflow_results[bldg_type]["Original"]
    reduced_inflow = building_inflow_results[bldg_type]["Reduced"]
    inflow_reduction = original_inflow - reduced_inflow
    percent_reduction[bldg_type] = (inflow_reduction / original_inflow) * 100

# Plotting histogram for percentage reduction in cumulative inflow
fig, ax = plt.subplots(figsize=(10, 6))

x_pos = np.arange(len(building_types))
reduction_percentages = [percent_reduction[bldg_type] for bldg_type in building_types]

ax.bar(x_pos, reduction_percentages, align='center', alpha=0.7)
ax.set_xlabel('Building Category')
ax.set_ylabel('Percentage Reduction in Cumulative Inflow (%)')
ax.set_title('Percentage Reduction in Cumulative Inflow for Each Building Category')
ax.set_xticks(x_pos)
ax.set_xticklabels(building_types)
ax.grid(True)

plt.tight_layout()
plt.show()
 