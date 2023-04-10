# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 15:11:46 2022

@author: Milad
"""

# from CreateModel import *
from MIP_Case import *
import time
import numpy as np
start = time.time()
import time
from gurobipy import Model, GRB, quicksum
import pandas as pd
import numpy as np
from CreateModelCase_Model_3 import *
# from SubproblemGenerator import SubproblemGenerator
# from SubproblemSolver import SubproblemSolver
from TrCal_Case import TrCal 
global States, Actions, F, P, R, E, Y, Tr, nItem, nStation, nTask, nWorkers, takt, nEquipment, alpha, equipCost, r_oe, Threshold, mus, sigmas, successors


for nItem in [1]:
    for Threshold in [0.80,0.85,0.90,0.95]:
        for takt in [40,45,50,55]:
            startGeneration = time.time()
           
            # Generate the model
            output = CreateModel(nItem)
            States, Actions, F, P, R, E, Y, Tr, nStation, nTask, nEquipment, resourceCost, equipCost, r_oe, mus, sigmas, successors, r_se = output
            finishGeneration = time.time() - startGeneration
            
            # Solve MILP
            startMIP = time.time()
            inputList = States, Actions, F, P, R, E, Y, Tr, nStation, nTask, nEquipment, resourceCost, equipCost, r_oe, mus, sigmas, successors, r_se,takt,nItem,Threshold
            objMIP,x_iad,w_es,worker,equipCost = MILP(inputList)
            finishMip = time.time() - startMIP
            print(objMIP)
            Bendersobj = 0
            finishBenders = 0
            q=open("Infra.txt", "a")
            q.write(str(Threshold) + ' ' + str(takt) +  ' '+ str(finishGeneration) + ' '+ str(objMIP) + ' ' + str(finishMip)+  ' '+ str(worker) + ' '+ str(equipCost))
            q.write('\n')                                 
            q.close()                                   
 
    