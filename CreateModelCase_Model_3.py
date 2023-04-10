# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 09:51:52 2023

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
def CreateModel(nItem):
    #%% Read Json file
   
    with open("Case\InfraFinal.json", 'r') as f:
        dataInfra = json.load(f)
    AssemblyPlan = dataInfra['AssemblyPlans'][1]
    
    #%% Get the information for Tasks
    TaskProcessTime = []
    TaskCost = []
    TaskQulity = []
    ListofTasks = list(range(len(AssemblyPlan['ListOfTaskIDs'])))
    nTask = len(ListofTasks)
    
    
    nStation = 0
    nEquipment = 1 # Index 0 of equipment means using no equipment
    nResource = 0 
    equipList = ['None']
    stationList = []
    resourceList = []
    
    
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
                            
        
    # Task Process Time
    TaskProcessTime = np.zeros((nTask))
    for t in range(nTask):
        temp = 0
        denaminator = 0
        for s in range(nStation):
            for e in range(nEquipment):
                if Process[t][s][e] != 1000:
                    temp += Process[t][s][e]
                    denaminator+=1
        temp = temp/denaminator
        TaskProcessTime[t] = temp
        
    # Add uncertainty to the data we get
    mus = {}
    sigmas = {}
    for i in range(nItem):
        for s in range(nStation):
            mus[i,s] = [TaskProcessTime[o] for o in range(nTask)]
            if s ==0 or s==1:
                sigmas[i,s] = [1 + 5 * np.random.random() for o in range(nTask)]    
            else:
                sigmas[i,s] = [4 + 6 *np.random.random() for o in range(nTask)]  
    # Equipment Cost
    equipCost = np.zeros((nStation,nEquipment))
    resourceCost = np.zeros((nItem,nStation))
    for i in range(nItem):
        for s in range(nStation):
            temp2 = 0
            denaminator = 0
            for e in range(nEquipment):
                temp = 0
                for t in range(nTask):
                    if Cost[t][s][e] != 10000:
                        temp += Cost[t][s][e]
                        temp2 += Cost[t][s][e]
                        denaminator += 1
                equipCost[s][e] = temp
            temp2 =temp2/denaminator
            resourceCost[i][s] = temp2
        
        
    # Precedence Matrix
    successors = {}
    for i in range(1,nTask):
        successors[0,i] = [i-1]
  
    #%% Compatibility of Task and Eqipment
    r_oe = [[1 for oo in range(nTask)] for ee in range(nEquipment)]
    for e in range(nEquipment):
        for o in range(nTask):
            temp = 0
            for s in range(nStation):
                temp += Cost[o][s][e]
            if temp == nStation*10000:
                r_oe[e][o] = 0
    #%% Compatibility of Equipment and Station
    r_se = [[1 for oo in range(nStation)] for ee in range(nEquipment)]
    for e in range(nEquipment):
        for s in range(nStation):
            temp = 0
            for o in range(nTask):
                temp += Cost[o][s][e]
            if temp == nTask * 10000:
                r_se[e][s] = 0
    
    #%% Generate  States here!
    state_first_part = tuple(range(nStation)) # The first part of the States stands for the station the items is located in
    # gc.collect() 
    state_second_part = tuple(set(range(r)) for r in range(nTask)) # Second part is the set of taks that have already been done for that item
    # print("second part of state is done")
    # gc.collect() 
    States = [[element for element in product(state_first_part,state_second_part)] for i in range(nItem)] # State is all the combination of part 1 and part 2
    # gc.collect()    
    print("State loop finished")   

    #%% Generate Actions here!
    Actions = []
    for i in range(nItem):
        temp = []
        for d in range(len(States[i])):
            Actions_first_part = tuple(range(nStation)) 
            Actions_second_part = tuple(list(range(r)) for r in range(1,nTask))
            temp.append([element for element in product(Actions_first_part,Actions_second_part)])
        Actions.append(temp)
    
    print("Action loop finished")
    gc.collect()

    #%% Calculate Transition Matrix
    Tr = {}                                                   
    gc.collect()
    print("Transition is finished")
    
    #%% Define F, P, R, E, and Y: I am storing them as dictionaries for now.
    F = {}
    P = {}
    R = {}
    E = {}
    Y = {}
    for i in range(nItem):
        for d in range(len(States[i])):
            for s in range(nStation):
                F[i,s,d] = 0
                for o in range(nTask):
                    for a in range(len(Actions[i][d])):
                        Y[a,s,o,i] = 0
    for i in range(nItem):
        for d in range(len(States[i])):
            F[i,States[i][d][0],d] = 1
            for o in range(nTask):
                P[o,States[i][d][0],d] = 1
                for a in range(len(Actions[i][d])):
                   if o in Actions[i][d][a][1]:
                       R[o,States[i][d][0],a] = 1
                       Y[a,Actions[i][d][a][0],o,i] = 1

    
    
    gc.collect()
    print("F and stuff are generated")
    output = States, Actions, F, P, R, E, Y, Tr, nStation, nTask, nEquipment, resourceCost, equipCost, r_oe, mus, sigmas, successors, r_se
    return(output)

