# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 17:00:10 2023

@author: Milad
"""
from statistics import NormalDist
def TrCal(i,d,dprime,a,States,nStation,successors,Actions,takt,mus,sigmas):
    val = 0
    #%% Calculate Transition Matrix
    if d!=dprime and (States[i][dprime][0] == States[i][d][0] + 1 or States[i][d][0] == nStation-1):
        flag = 1
        if flag != 0 : # Here we check the precedence
            if States[i][d][0] != nStation-1:  
                route = 1
                possibility = [entry for entry in States[i][dprime][1] if entry not in States[i][d][1]] # Possible actions are calculated here
            else:
                route = 2
                possibility = [entry for entry in States[i][dprime][1]] # Possible actions are calculated here
            flag = 0
            if route == 1:
                if possibility == list(Actions[i][d][a][1]): # In this situation, all the tasks must be done!
                    newMean = 0
                    newVar = 0
                    s = Actions[i][d][a][0]
                    for o in possibility:
                        newMean += mus[i,s][o]
                        newVar += sigmas[i,s][o]**2
                    newVar = newVar**0.5
                    val = NormalDist(mu=newMean,sigma = newVar).cdf(takt)
                elif set(possibility) == set():  # In this situation, first task must not be done in Takt
                    firstTask = Actions[i][d][a][1][0]
                    s= Actions[i][d][a][0]
                    val = 1-NormalDist(mu=mus[i,s][firstTask],sigma = sigmas[i,s][firstTask]).cdf(takt)
                else:
                    happenningMu = 0
                    happeningVar = 0
                    notHappeningMu = 0
                    notHappeningVar = 0
                    s = Actions[i][d][a][0]
                    flag1 = 0
                    for o in range(len(Actions[i][d][a][1])):
                        if flag1 == 0:
                            if o<len(possibility):
                                happenningMu+=mus[i,s][Actions[i][d][a][1][o]]
                                happeningVar+=sigmas[i,s][Actions[i][d][a][1][o]]**2
                                notHappeningMu+=mus[i,s][Actions[i][d][a][1][o]]
                                notHappeningVar+=sigmas[i,s][Actions[i][d][a][1][o]]**2
                            else:
                                notHappeningMu+=mus[i,s][Actions[i][d][a][1][o]]
                                notHappeningVar+=sigmas[i,s][Actions[i][d][a][1][o]]**2       
                                flag1 = 1
                    happeningVar = happeningVar**0.5
                    notHappeningVar = notHappeningVar**0.5
                    val =  NormalDist(mu=happenningMu,sigma = happeningVar).cdf(takt) * (1-NormalDist(mu=notHappeningMu,sigma = notHappeningVar).cdf(takt))

    if 0.9>val>0.1:
        # print(val)
        sss=77
    return(val)