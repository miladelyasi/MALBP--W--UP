# -*- coding: utf-8 -*-
"""
Created on Sun Apr 02 21:50:19 2023

@author: MiladElyasi
"""


from itertools import chain, combinations,product,permutations

from scipy.stats import truncnorm 

import gc
import numpy as np
import copy
rnd = np.random
rnd.seed(320)
from statistics import NormalDist
import json 


#%% States: For each item we have got a State
def CreateModel(PlanID):
    #%% Read Json file
    f = open('Case\Infraflex.json')
    dataInfra = json.load(f)    
    AssemblyPlan = dataInfra['AssemblyPlans'][PlanID-1]
    
    #%% Get the information for Tasks
    TaskProcessTime = []
    TaskCost = []
    TaskQulity = []
    ListofTasks = list(range(len(AssemblyPlan['ListOfTaskIDs'])))
    nTask = len(ListofTasks)
    

    
    #%% Get the information of Equipment and Worker
    ProcessDic = {}
    QualityDic = {}
    CostDic = {}
    ListofEquipment = []
    ListofWorkers = []
    for t in range(nTask):
        for _ in AssemblyPlan['ListOfPrimaryNodeIDs'][str(t)]:
            _ = int(_)
            myString = dataInfra['Node'][_]['PRNodeName'].split('+')
            try:
                AssemblyNode = myString[0]
                Resource = myString[1]
                Equipment = myString[2]
            except:
                IndexError
                Equipment = str(None)
            
            ProcessDic[t,AssemblyNode,Resource,Equipment] = dataInfra['Node'][_]['ProcessTime']
            CostDic[t,AssemblyNode,Resource,Equipment] = dataInfra['Node'][_]['Costs']
            QualityDic[t,AssemblyNode,Resource,Equipment] = dataInfra['Node'][_]['MonitoringEfficiency']
            
    
  
    
     
    return(ProcessDic,CostDic,QualityDic)

ProcessDic,CostDic,QualityDic = CreateModel(4)