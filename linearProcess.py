'''
linearProcess.py
- Core algorithm for linearizing planning window in production
@ Jiahao (Derek) Ye
'''

import pandas as pd
import numpy as np
import sys

def globalPlanner(subGroup, max_preBuildDays):
    '''
    process data based on site-product pairs
    @params:
        subGroup (DataFrameGroupBy): pandas DataFrameGroupBy object
        max_preBuildDays (int): Pre Build-Days
    Returns:
        the input subGroup with "demand" column filled 
        and the additional "produce" column filled with linearized production
    '''
    # input validation check
    #inputCheck(subGroup)
    
    subSiteProd = subGroup.copy()  # data process
    keydates = subGroup.dropna()   # look-up table for key dates
    ''' BELOW LINE MODIFIED '''
    initial_KDay = keydates['day'].values[0]  # store the actual first key date, i.e., initial plan window 
    
    keydates['prevKDay'] = keydates['day'].shift(1) # add previous key date info for future reference
    ''' BELOW LINE MODIFIED '''
    keydates['prevKDay'] = keydates['prevKDay'].fillna(subSiteProd['day'].values[0]) # set the "previous key date" of the first actual key date as the first day in the column
    keydates['plan_window'] = keydates['day'] - keydates['day'].shift(1)  # calculate days production window
    ''' BELOW LINE MODIFIED '''
    keydates['plan_window'] = keydates['plan_window'].fillna(initial_KDay-subSiteProd['day'].values[0])
    
    # gives the earlist allowed day to begin production given curr day, curr planning window, and prev key date
    def earlist_startDate(curr_day, plan_window, prevKDay):
        if plan_window < max_preBuildDays:
            return prevKDay   
        else: return curr_day - max_preBuildDays     
    # boradcast earlist_startDate() to calculate earlist day to begin production for every planning window
    keydates['startDay'] = keydates.apply(lambda x: earlist_startDate(x['day'],x['plan_window'], x['prevKDay']), axis = 1)
    ''' BELOW LINE MODIFIED '''
    keydates['startDay'] = keydates['startDay'].clip(lower=subSiteProd['day'].values[0])  # address inital stage (when could've begun already)
    
    # pass along the above infos to every day so that every row has a reference evaluate to its stage
    subSiteProd = pd.merge(subSiteProd, keydates, on=['site','product','day','demand'], how='outer')
    subSiteProd['demand'] = subSiteProd['demand'].interpolate(method='ffill') # frontfill/paddling demand
    subSiteProd['plan_window'] = subSiteProd['plan_window'].interpolate(method='backfill').astype(int)
    subSiteProd['prevKDay'] = subSiteProd['prevKDay'].interpolate(method='backfill').astype(int)
    subSiteProd['startDay'] = subSiteProd['startDay'].interpolate(method='backfill').astype(int)
    subSiteProd['init_demand'] = keydates['demand'].values[0]
    subSiteProd['demand'] = subSiteProd['demand'].fillna(0)

    def update(day, start, plan_window, prevKDay, demand, init_demand):
        '''A MECE Update Rule based on cases'''
        # BASE CASE A: initial stage
        if demand == 0:
            if day >= start:    # if should've begun production
                ''' BELOW LINE MODIFIED '''
                interval = (plan_window-(start-prevKDay))+1
                return init_demand/interval*(day-start+1)
            else:               # if it's too early to start
                return 0
        # BASE CASE B: key date
        if day == prevKDay+plan_window:
            return demand
        # GENERAL CASE: 
        if plan_window > max_preBuildDays and day < start:   # if it's too early, halt production
            return demand
        if plan_window < max_preBuildDays:
            return np.nan  # should've begun production, return NaN for future linearization using pd.interpolate()
    
    # boradcast update() to calculate primitive produce column
    subSiteProd['produce'] = subSiteProd.apply(lambda x: update(x['day'],x['startDay'],x['plan_window'],x['prevKDay'],x['demand'],x['init_demand']), axis=1)
    # linearize the remaining production window
    linearized = subSiteProd.interpolate(method='linear')
    # output formatting
    linearized_subSiteProd = linearized.drop(columns=['prevKDay','plan_window','startDay','init_demand'])
    linearized_subSiteProd['demand'] = linearized_subSiteProd['demand'].astype(int)
    linearized_subSiteProd['produce'] = linearized_subSiteProd['produce'].astype(int)
    return linearized_subSiteProd

def linearize(filepath, pre_buildDays):
    data = pd.read_csv(filepath)
    max_preBuildDays = int(pre_buildDays) # change maximum allowed pre-build days here MUST > 0
    result = data.groupby(['site', 'product'], as_index=False).apply(globalPlanner, max_preBuildDays=max_preBuildDays).reset_index(drop=True)
    # fill in the original file
    result = pd.merge(data, result, on=['site','product','day'], how='left', suffixes=('_drop', '_rename'))
    result = result.drop(columns='demand_drop')
    result = result.rename(columns={"demand_rename":"demand"})
    return result