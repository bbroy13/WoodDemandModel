# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 01:32:33 2024

@author: bbroy
"""

import os
import sys
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
MainPath = os.path.join(r'C:\Users\bbroy\OneDrive - UBC\PhD poposal\Dynamic MFA of buildings\demand model for wood in construction sector\WoodDemandModel\ODYM-master\ODYM-master\odym\modules')
sys.path.insert(0, MainPath)

import dynamic_stock_model as dsm

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
FA_elasticity_res = 42.87  

# Wood Material Density (kg/m^2) per Building Type
Mat_density = {
    "Single-detached": 53.48, 
    "High-rise": 25.17,
    "Low-mid-rise": 25.17,
    "Others": 163.0,  
}

# Interpolation functions for population forecast
f_SSP2 = interp1d(data_pop.Year, data_pop.SSP2, kind='cubic')

# Building Type Proportions
building_types = ["Single-detached", "High-rise", "Low-mid-rise", "Others"]
proportions = [0.536, 0.099, 0.18, 0.185]

# Initialize dictionaries to store BAU results
building_stock_results_BAU = {bldg_type: [] for bldg_type in building_types}
building_inflow_results_BAU = {bldg_type: [] for bldg_type in building_types}
building_outflow_results_BAU = {bldg_type: [] for bldg_type in building_types}

# Calculate BAU scenario
CAN_pop = f_SSP2(years)
FA_stock = CAN_pop * FA_elasticity_res

S_0_res_2020_by_type = {}
for i, bldg_type in enumerate(building_types):
    S_0_res_2020_by_type[bldg_type] = np.flipud(RECS_Weights.Res_Weight * CAN_pop[115] * FA_elasticity_res * proportions[i])

for bldg_type in building_types:
    FA_stock_type = FA_stock * proportions[building_types.index(bldg_type)]
    myLT_BAU = {'Type': 'Weibull', 'Shape': np.array([1.9]), 'Scale': np.array([57.52])}
    US_Bldg_DSM = dsm.DynamicStockModel(t=years, s=FA_stock_type, lt=myLT_BAU)
    US_Bldg_DSM.dimension_check()
    S_C = US_Bldg_DSM.compute_evolution_initialstock(InitialStock=S_0_res_2020_by_type[bldg_type], SwitchTime=116)
    S_C, O_C, I = US_Bldg_DSM.compute_stock_driven_model()
    O = US_Bldg_DSM.compute_outflow_total()
    
    building_stock_results_BAU[bldg_type] = US_Bldg_DSM.s
    building_inflow_results_BAU[bldg_type] = I
    building_outflow_results_BAU[bldg_type] = O

# Initialize dictionaries for each lifetime extension scenario
building_stock_results_LT_75 = {bldg_type: [] for bldg_type in building_types}
building_inflow_results_LT_75 = {bldg_type: [] for bldg_type in building_types}
building_outflow_results_LT_75 = {bldg_type: [] for bldg_type in building_types}

building_stock_results_LT_100 = {bldg_type: [] for bldg_type in building_types}
building_inflow_results_LT_100 = {bldg_type: [] for bldg_type in building_types}
building_outflow_results_LT_100 = {bldg_type: [] for bldg_type in building_types}

# Lifetime Extension Scenarios
lifetime_extensions = {
    75: {'stock': building_stock_results_LT_75, 'inflow': building_inflow_results_LT_75, 'outflow': building_outflow_results_LT_75},
    100: {'stock': building_stock_results_LT_100, 'inflow': building_inflow_results_LT_100, 'outflow': building_outflow_results_LT_100}
}

for BldgLife_mean in lifetime_extensions.keys():
    myLT = {'Type': 'Weibull', 'Shape': np.array([1.9]), 'Scale': np.array([BldgLife_mean])}
    
    for bldg_type in building_types:
        FA_stock_type = FA_stock * proportions[building_types.index(bldg_type)]
        US_Bldg_DSM = dsm.DynamicStockModel(t=years, s=FA_stock_type, lt=myLT)
        US_Bldg_DSM.dimension_check()
        S_C = US_Bldg_DSM.compute_evolution_initialstock(InitialStock=S_0_res_2020_by_type[bldg_type], SwitchTime=116)
        S_C, O_C, I = US_Bldg_DSM.compute_stock_driven_model()
        O = US_Bldg_DSM.compute_outflow_total()
        
        lifetime_extensions[BldgLife_mean]['stock'][bldg_type] = US_Bldg_DSM.s
        lifetime_extensions[BldgLife_mean]['inflow'][bldg_type] = I
        lifetime_extensions[BldgLife_mean]['outflow'][bldg_type] = O

# Exporting all scenario values to Excel
output_data_combined = {
    "Stock": pd.DataFrame({"Year": years}),
    "Inflow": pd.DataFrame({"Year": years}),
    "Outflow": pd.DataFrame({"Year": years}),
}

for BldgLife_mean, results in lifetime_extensions.items():
    for bldg_type in building_types:
        output_data_combined["Stock"][f"Wood_Stock_{bldg_type}_LT_{BldgLife_mean}"] = results['stock'][bldg_type] * Mat_density[bldg_type]
        output_data_combined["Inflow"][f"Wood_Inflow_{bldg_type}_LT_{BldgLife_mean}"] = results['inflow'][bldg_type] * Mat_density[bldg_type]
        output_data_combined["Outflow"][f"Wood_Outflow_{bldg_type}_LT_{BldgLife_mean}"] = results['outflow'][bldg_type] * Mat_density[bldg_type]

# Add BAU results for comparison
for bldg_type in building_types:
    output_data_combined["Stock"][f"Wood_Stock_{bldg_type}_BAU"] = building_stock_results_BAU[bldg_type] * Mat_density[bldg_type]
    output_data_combined["Inflow"][f"Wood_Inflow_{bldg_type}_BAU"] = building_inflow_results_BAU[bldg_type] * Mat_density[bldg_type]
    output_data_combined["Outflow"][f"Wood_Outflow_{bldg_type}_BAU"] = building_outflow_results_BAU[bldg_type] * Mat_density[bldg_type]

save_directory = r'C:\Users\bbroy\OneDrive - UBC\PhD poposal\Dynamic MFA of buildings\Bldg_Stock-master\Bldg_Stock-master'  # Replace with your actual path
file_name = 'wood_flows_by_building_type_LT_scenarios.xlsx'
full_path = os.path.join(save_directory, file_name)

if not os.path.exists(save_directory):
    os.makedirs(save_directory)
writer = pd.ExcelWriter(full_path, engine='xlsxwriter')

for sheet_name, df in output_data_combined.items():
    df.to_excel(writer, sheet_name=sheet_name, index=False)

writer.close()
print(f"Excel file 'wood_flows_by_building_type_LT_scenarios.xlsx' has been saved successfully.")
