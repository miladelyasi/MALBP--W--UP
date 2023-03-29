# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 07:50:19 2023

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
    Stations = list(set(AssemblyPlan['ListOfStationIDs']))
    
    #%% Get the information for Tasks
    TaskProcessTime = []
    TaskCost = []
    TaskQulity = []
    ListofTasks = list(range(len(AssemblyPlan['ListOfTaskIDs'])))
    for currentTask in range(len(ListofTasks)):
        currentNode = int(AssemblyPlan['ListOfPrimaryNodeIDs'][str(currentTask)] )
        currentTaskPlan = dataInfra['Node'][currentNode]
        TaskProcessTime.append(currentTaskPlan['ProcessTime'])
        TaskCost.append(currentTaskPlan['Costs'])
        TaskQulity.append(currentTaskPlan['MonitoringEfficiency'])

    
    #%% Get the information of Equipment and Worker
    MyMainDic = {}
    ProcessDic = {}
    QualityDic = {}
    CostDic = {}
    ListofEquipment = []
    ListofWorkers = []
    for s in Stations:
        for _ in range(len(dataInfra['Node'])):
            myString = dataInfra['Node'][_]['PRNodeName'].split('+')
            for i in myString:
                if (i,s) in MyMainDic.keys():
                    MyMainDic[i,s] += 1
                    ProcessDic[i,s] += dataInfra['Node'][_]['ProcessTime']
                    QualityDic[i,s] += dataInfra['Node'][_]['MonitoringEfficiency']
                    if i[:8] == 'Operator':
                        CostDic[i,s] += 0.8*dataInfra['Node'][_]['Costs']
                    else:
                        CostDic[i,s] += 0.2*dataInfra['Node'][_]['Costs']
                else:
                    MyMainDic[i,s] = 1
                    ProcessDic[i,s] =  dataInfra['Node'][_]['ProcessTime']
                    QualityDic[i,s] = dataInfra['Node'][_]['MonitoringEfficiency']
                    if i[:8] == 'Operator':
                        if i not in ListofWorkers:
                            ListofWorkers.append(i)
                        CostDic[i,s] = 0.8*dataInfra['Node'][_]['Costs']
                    else:
                        if i not in ListofEquipment and i[:2]!='AN':
                            ListofEquipment.append(i)
                        CostDic[i,s] = 0.2*dataInfra['Node'][_]['Costs']
        
    
    for (i,s) in MyMainDic.keys():
        ProcessDic[i,s] = ProcessDic[i,s]/MyMainDic[i,s]
        QualityDic[i,s] = QualityDic[i,s]/MyMainDic[i,s]
        CostDic[i,s] = CostDic[i,s]/MyMainDic[i,s]
    
    #%% Store the data in numpy arrays (Extra for Ehsan's code)
    ListofEquipment.sort()
    ListofWorkers.sort()
    
    #Equipment
    EquipProcessTime = np.zeros((len(ListofEquipment),len(Stations)))
    EquipCost = np.zeros((len(ListofEquipment),len(Stations)))
    EquipQulity = np.zeros((len(ListofEquipment),len(Stations)))
    for i in range(len(ListofEquipment)):
        for s in range(len(Stations)):
            for (j,k) in MyMainDic.keys():
                if j == ListofEquipment[i] and k==Stations[s]:
                    EquipProcessTime[i][s] = ProcessDic[j,k]
                    EquipCost[i][s] = CostDic[j,k]
                    EquipQulity[i][s] = QualityDic[j,k]
    
    #Worker
    WorkerProcessTime = np.zeros((len(ListofWorkers),len(Stations)))
    WorkerCost = np.zeros((len(ListofWorkers),len(Stations)))
    WorkerQulity = np.zeros((len(ListofWorkers),len(Stations)))
    for i in range(len(ListofWorkers)):
        for s in range(len(Stations)):
            for (j,k) in MyMainDic.keys():
                if j == ListofWorkers[i] and k==Stations[s]:
                    WorkerProcessTime[i][s] = ProcessDic[j,k]
                    WorkerCost[i][s] = CostDic[j,k]
                    WorkerQulity[i][s] = QualityDic[j,k]    
    
     
    return(TaskProcessTime,TaskCost,TaskQulity,EquipProcessTime,EquipCost,EquipQulity,WorkerProcessTime,WorkerCost,WorkerQulity)

TaskProcessTime,TaskCost,TaskQulity,EquipProcessTime,EquipCost,EquipQulity,WorkerProcessTime,WorkerCost,WorkerQulity = CreateModel(4)
