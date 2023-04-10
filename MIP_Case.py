# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 13:48:29 2022

@author: m22elyas
"""
from itertools import chain, combinations,product,permutations
import numpy as np
from tqdm import tqdm
from statistics import NormalDist
import pandas as pd
from gurobipy import GRB,Model,LinExpr, quicksum,GurobiError
from TrCal_Case import TrCal

def MILP(inputList):
    inputList = States, Actions, F, P, R, E, Y, Tr, nStation, nTask, nEquipment, resourceCost, equipCost, r_oe, mus, sigmas, successors, r_se,takt,nItem,Threshold = inputList
    mdl=Model("MILP")
    mdl.Params.Method = 1
    # mdl.Params.NodeFileStart = 0.5

    # Decision Variables
    xindex = {}
    for i in range(nItem):
        for d in range(len(States[i])):
            for a in range(len(Actions[i][d])):
                xindex[i,a,d] = 1
    x_iad=mdl.addVars(xindex.keys(), vtype=GRB.CONTINUOUS, ub=1, name = "x_iad")
    w_es=mdl.addVars(range(nEquipment),range(nStation), vtype=GRB.BINARY, name = "w_es")
    expectedWorker = mdl.addVar(vtype=GRB.CONTINUOUS, name = "expectedWorker")
    equipCosts = mdl.addVar(vtype=GRB.CONTINUOUS, name = "equipCosts")
    penalty = mdl.addVar(vtype=GRB.CONTINUOUS, name = "penalty")
    # # Objective Function
    mdl.setObjective(quicksum(resourceCost[i][s]*F[i,s,d]*x_iad[(i,a,d)] for i in range(nItem) for d in range(len(States[i])) for a in range(len(Actions[i][d])) for s in range(nStation)) + quicksum(equipCost[s][e]*w_es[e,s] for e in range(nEquipment) for s in range(nStation)),GRB.MINIMIZE)
    
    # # Constraints      
    # # 2
    mdl.addConstrs(quicksum(TrCal(i,d,dprime,a,States,nStation,successors,Actions,takt,mus,sigmas)*x_iad[(i,a,d)] for d in range(len(States[i])) for a in range(len(Actions[i][d])) ) == quicksum(x_iad[i,aprime,dprime] for aprime in range(len(Actions[i][dprime])))for i in range(nItem)  for dprime in range(1,len(States[i])   ))   
    # # 3
    mdl.addConstrs(quicksum(x_iad[(i,a,d)]  for d in range(len(States[i])) for a in range(len(Actions[i][d])) ) == 1 for i in range(nItem))
    # # 4
    mdl.addConstrs(Y[a,s,o,i]*x_iad[i,a,d] <= quicksum(r_oe[e][o]*w_es[e,s] for e in range(nEquipment)) for i in range(nItem)  for s in range(nStation) for o in range(nTask) for d in range(len(States[i])) for a in range(len(Actions[i][d])))

    #NEW
    # mdl.addConstrs(quicksum(Y[a,s,o,i]*x_iad[i,a,d] for i in range(nItem) for d in range(len(States[i])) for a in range(len(Actions[i][d]))) <=  5000*w_es[e,s] for e in range(nEquipment)  for s in range(nStation) for o in range(nTask) )

    mdl.addConstr(expectedWorker == quicksum(resourceCost[i][s]*F[i,s,d]*x_iad[(i,a,d)] for i in range(nItem) for d in range(len(States[i])) for a in range(len(Actions[i][d])) for s in range(nStation)))
    mdl.addConstr(equipCosts == quicksum(equipCost[s][e]*w_es[e,s] for e in range(nEquipment) for s in range(nStation)))

    # Constraints for Equipment
    mdl.addConstrs(w_es[e,s]<=r_se[e][s] for e in range(nEquipment) for s in range(nStation))
    
    mdl.addConstrs(quicksum(r_se[e][s]*w_es[e,s] for e in range(nEquipment))==1 for s in range(nStation))

    # #5
    # Write in for loop!
    for i in range(nItem):
        for d in range(len(States[i])):
            for a in range(len(States[i][d])):
                s = nStation - 1
                temp = 0
                newMean = 0
                newVar = 0
                for o in Actions[i][d][a][1]:
                    newMean += mus[i,s][o]
                    newVar += sigmas[i,s][o]            
                P = 1- NormalDist(mu=newMean,sigma = newVar).cdf(takt)
                if P >= Threshold:
                    # print("This is happening")
                    mdl.addConstr(x_iad[i,a,d]==0)
   # mdl.write("MIP_S.lp")
    

    # mdl.addConstr(w_es[])
    mdl.optimize()
    try:  
        obj = mdl.objVal
        x_iad={key:x_iad[key].X for key in x_iad.keys() if x_iad[key].X>0}
        w_es={key:w_es[key].X for key in w_es.keys() if w_es[key].X>0}
        worker = expectedWorker.X
        equipCosts = equipCosts.X
    except AttributeError:
        obj = 10000000
        x_iad ={}
        w_es = {}
        worker = 0
        equipCosts = 0
    
    return(obj,x_iad,w_es,worker,equipCosts)