##########################################################################
##        Script to analyze sample size for goalie performance          ##
##         Last edited by Nick Romanchuk, December 24th, 2020           ##
##########################################################################

#Import the required packages
from statsmodels.stats.power import tt_solve_power
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from scipy import stats
import pandas as pd
import numpy as np
import requests
import time

def calc_tstat(Sample_Mean, Sample_STD, Sample_Size, Population_Mean):
    t = (Sample_Mean - Population_Mean)/(Sample_STD/np.sqrt(N))
    return t

def calc_pvalue(tstat, df, tail):
    if tail == 'One':
        pvalue = (1 - stats.t.cdf(tstat, df=df))
    elif tail == 'Two':
        pvalue = (1 - stats.t.cdf(tstat, df=df))*2
    return pvalue

def calc_confidenceinterval(sample_mean, sample_STD, Sample_Size, alpha):
    Con_lower = sample_mean - stats.norm.ppf(1-alpha/2)*sample_STD/np.sqrt(Sample_Size)
    Con_higher = sample_mean + stats.norm.ppf(1-alpha/2)*sample_STD/np.sqrt(Sample_Size)
    return Con_lower, Con_higher

#Estimated Average Goalie Save Percentage and Variability
goalie_mean = 91.1
goalie_std = 5.3

#Significance threshold
alpha = 0.05

#Calculate sample size required to reach statistical signifcance 
Sample_Significance = []
Confidence_lower = []
Confidence_higher = []
for Save in np.arange(92, 100.25, 0.25):
    for N in np.arange(1, 201, 1):
    
        ##Calculate the t-statistic
        t = calc_tstat(Save, goalie_std, N, goalie_mean)

        #Degrees of freedom
        df = N - 1

        #Calculate the p-value
        p = calc_pvalue(t, df, 'Two')

        #Record sample size needed for signifcance at alpha
        if p < alpha:
            Sample_Significance.append(N)
            Con_Lower, Con_Higher = calc_confidenceinterval(Save, goalie_std, N, alpha)
            if Con_Higher>=100.0:
                Con_Higher = 100.0
            Confidence_lower.append(Con_Lower)
            Confidence_higher.append(Con_Higher)
            break

#Reorganize into data frame
SampleSignificance = pd.DataFrame({'SV%': np.arange(92, 100.25, 0.25), 'Sample Save': Sample_Significance, 'Confidence Lower': Confidence_lower, 'Confidence Higher': Confidence_higher})
print(SampleSignificance)

#Export data dataframes to excel
SampleSignificance.to_excel(r'C:\Users\nickr\OneDrive\Desktop\LLS_Blog\GoalieHotStreak\GoalieSignificanceSampleSize.xlsx', index = False)
