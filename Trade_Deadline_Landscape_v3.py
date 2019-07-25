#!/usr/bin/env python
# coding: utf-8

"""
Created on Mon June 10 2019

@author: ABooth, rossbechtel

Scrapes Fangraphs Positional WAR and 538 Projections
"""

#Imports
import re
import pandas as pd
import numpy as np

def GetTradeDeadlineLandscape():
    #538 Data
    df = pd.read_html("https://projects.fivethirtyeight.com/2019-mlb-predictions/")[0]
    teams = [re.split('(\d+)', x)[0] for x in df.iloc[:,0]]
    dfSub = df.iloc[:,np.r_[4,6,7]]
    dfSub["Team"] = teams
    dfSub.columns = ["Proj_Record", "Make_Playoffs", "Win_Division", "Club"]
    cols = dfSub.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    dfSub = dfSub[cols]

    cloneDF = dfSub

    #Positional Rankings
    positions = ["C", "1B", "2B", "SS", "3B", "LF", "CF", "RF","DH","SP","RP"]
    for pos in positions:
        print(pos)
        tempURL = "https://www.fangraphs.com/depthcharts.aspx?position=" + str(pos)
        tempDf = pd.read_html(tempURL)[-1]
        dfSub1 = tempDf.iloc[0:30,np.r_[4, 0]]
        dfSub1.columns = [pos, "Club"]
        dfSub1[pos] = dfSub1.rank(axis=0, method="first", ascending=False, numeric_only=True)
        cloneDF = pd.merge(cloneDF, dfSub1, on='Club')

    return cloneDF