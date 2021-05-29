#Import the required packages
from statsmodels.stats.power import tt_solve_power
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from scipy import stats
import pandas as pd
import numpy as np
import requests
import time

number_interations = 500000

p_values = []
for i in range(0, number_interations, 1):

    s = np.random.normal(93.5, 5.3, 40)

    ##Calculate the t-statistic
    t = (np.mean(s) - 91.1)/(np.std(s)/np.sqrt(len(s)))

    #Degrees of freedom
    df = len(s) - 1

    #Calculate the p-value
    p = (1 - stats.t.cdf(t, df=df))*2
    
    #Record sample size needed for signifcance at alpha
    if p > 0.05:
        p_values.append(p)

#Reorganize into data frame
Power = 1 - len(p_values)/number_interations
print(Power)
