# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 15:54:58 2023

@author: bbroy
"""
import os
import numpy as np
import time
import datetime
import scipy.io
import scipy.stats   
import matplotlib.pyplot as plt    
import pandas as pd
import shutil 
import uuid
import xlrd


"""
Set file path
"""    

from pathlib import Path

# `cwd`: current directory
cwd = Path('C:\\Users\\bbroy\\OneDrive - UBC\\PhD poposal\\Dynamic MFA of buildings\\demand model for wood in construction sector\\WoodDemandModel')

Project_MainPath = cwd
Input_Data        = 'InData.xls'
Path_Data   = Path.joinpath(Project_MainPath ,'Data')
Path_Results = Path.joinpath(Project_MainPath ,'Results')
Path_Script = Path.joinpath(Project_MainPath ,'Scripts')
Path_GeneralResults = Path.joinpath(Project_MainPath ,'General_Results')

"""
Rade the configuration file
"""

Project_DataFileName = Input_Data
Project_DataFilePath = Path.joinpath(Path_Data , Project_DataFileName)
Project_DataFile_WB  = xlrd.open_workbook(Project_DataFilePath)
Project_Configsheet  = Project_DataFile_WB.sheet_by_name('Model_config')

Model_name= Project_Configsheet.cell_value(0,1)
scriptConfig={}

for m in range (3,14):
    scriptConfig [Project_Configsheet.cell_value(m,0)]= [(Project_Configsheet.cell_value(m,1))]

par_Years = int (scriptConfig["EndYear"][0]- scriptConfig["StartYear"][0]) +1
par_Region = len((scriptConfig["Region"]))       
Per_Sector= len((scriptConfig["Sector"])) 
Per_Service= len((scriptConfig["Service"])) 
Per_Product= len((scriptConfig["Product"])) 
Per_Material=  len((scriptConfig["Material"])) 
Per_WasteMgt= len((scriptConfig["Recovery"])) 
Per_REStg= len((scriptConfig["RE_Strategy"])) 

    
