# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 16:40:25 2023

@author: Milad
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
    nStation = 0
    nEquipment = 1 # Index 0 of equipment means using no equipment
    equipList = ['None']
    stationList = []
    for _ in range(len(dataInfra['Node'])):
        if dataInfra['Node'][_]['Tasktype'] != 'Feeding':
            myString = dataInfra['Node'][_]['PRNodeName'].split('+')
            if len(myString)>2 and myString[2] not in equipList:
                equipList.append(myString[2])
                nEquipment+=1
            if myString[1] not in stationList:
                stationList.append(myString[1])
                nStation+=1
    #%% Get the information of Equipment and Worker
    Process = np.ones((nTask,nStation,nEquipment))*1000
    Quality = np.zeros((nTask,nStation,nEquipment))
    Cost = np.ones((nTask,nStation,nEquipment))*10000
    ListofEquipment = []
    ListofWorkers = []
    for _ in range(len(dataInfra['Node'])):
        if dataInfra['Node'][_]['Tasktype'] != 'Feeding':
            t =  int(dataInfra['Node'][_]['TaskID'])
            myString = dataInfra['Node'][_]['PRNodeName'].split('+')
            for i in range(nStation):
                for j in range(nEquipment):
                    if len(myString)>2:
                        if stationList[i] == myString[1] and equipList[j] == myString[2]:
                            Process[t][i][j] = dataInfra['Node'][_]['ProcessTime']
                            Cost[t][i][j] = dataInfra['Node'][_]['Costs']
                            Quality[t][i][j] = dataInfra['Node'][_]['MonitoringEfficiency']
                    else:
                        if stationList[i] == myString[1]:
                            Process[t][i][0] = dataInfra['Node'][_]['ProcessTime']
                            Cost[t][i][0] = dataInfra['Node'][_]['Costs']
                            Quality[t][i][0] = dataInfra['Node'][_]['MonitoringEfficiency']
                            
        
        
        
 
     
    return(Process,Quality,Cost)

ProcessDic,CostDic,QualityDic = CreateModel(4)
