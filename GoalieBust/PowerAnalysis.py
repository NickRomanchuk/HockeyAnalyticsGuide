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

#Change setting so that all rows and columns of dataframe are displayed
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


#Perform Scraping from hockey reference, first need table of all goalies who played a game in 2019-2020 NHL season
page = requests.get("https://www.hockey-reference.com/leagues/NHL_2020_goalies.html")
soup = BeautifulSoup(page.content, 'html.parser')
all_goalies = soup.find(id="stats")
table_body_all_goalies = all_goalies.find('tbody')
goalies = table_body_all_goalies.find_all('tr')

allrows = []
for row in goalies:
    cols=row.find_all('td')
    cols=[x.text.strip() for x in cols]
    link=row.find('a')
    try:
        url=link['href']
        cols.append(url)
        allrows.append(cols)
    except:
        pass

#Data is a dataframe of all the goalies who played at least 1 game in 2019-2020 NHL season
data=pd.DataFrame(allrows)

#Remove duplicates so each goalie only appears once
data.drop_duplicates(subset=[0], keep='first', inplace=True)

#Create object containing the URLs for each goalies gamelogs
url_goalie = "https://www.hockey-reference.com" + data[25].astype(str).str[:-5] + '/gamelog/2020'

#Create empty varibles to be filled in subsequent loop
avg = []
sd = []
count = []
name = []
i = 0

#Set this to remove games below a certain # of minutes played
Minute_Threshold=40

#loop for each goalie identified above, scrape table with individual game peformances
for url in url_goalie:
    
    #record goalie name from current loop
    goalie_name=data.iloc[i,0]
    i+=1

    #Scrape table and organize
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    elements = soup.find(id="gamelog")
    table_body = elements.find('tbody')
    rows = table_body.find_all('tr')

    games = []
    games_clean = []
    all_games = []

    for row in rows:
        cols=row.find_all('td')
        cols=[x.text.strip() for x in cols]
        games.append(cols)

        #remove empty rows
        games_clean = [x for x in games if x != []]

        #all_games is a dataframe where each row is a game played by the goalie in 2019-2020 NHL Season
        all_games = pd.DataFrame(games_clean)

        #Label Columns
        all_games.columns = ['Date','G','Age','Tm','','Opp','','DEC','GA','SA','SV','SV%','SO','PIM','TOI']

        #Clean SV% column: set to str and add zero in front of decimal points, allows for future conversion to numeric
        all_games['SV%'].astype(str)
        for index, row in all_games.iterrows():
            if row['SV%'] != '1.000':
                row['SV%'] = '0' + row['SV%']

        #Remove games where the goalies did not play a previously specified minimum number of minutes
        all_games = all_games[pd.to_numeric(all_games['TOI'].astype("|S").map(lambda x: x[:-3]))>=Minute_Threshold]

        #Remove games where the goalie did not face any shots
        all_games['SA'] = all_games.SA.astype(int)
        all_games = all_games[all_games.SA != 0]

        #Set save percentage to be numeric value
        all_games['SV%'] = pd.to_numeric(all_games['SV%'],errors='coerce')

    #Now that dataframe has been correctly organized we can calculate desired stats
    #Record goalie name, will appear more than once if goalie played for >1 team
    name += [goalie_name] * all_games['Tm'].nunique()

    #Record number of games played for each team by the goalie
    count.append(all_games.groupby(['Tm'])['SV%'].count())

    #Record the average save perecetage for each team the goalie played
    avg.append(all_games.groupby(['Tm'])['SV%'].mean())

    #Record standard deviation of the save perecetage for each team the goalie played
    sd.append(all_games.groupby(['Tm'])['SV%'].std())

#Create new data frame with the extracted inforamtion above
SV = pd.concat([pd.concat(count),pd.concat(avg),pd.concat(sd)], axis=1)
SV.reset_index(level=0, inplace=True)

#Label the columns appropriately
SV.columns=['Team','GP','Mean','SD']
SV['Name']=name

#Drop duplicate rows (i.e. goalies that played for >1 team) only keep the team they played the most games for
SV.sort_values('GP', ascending=False).drop_duplicates('Name').sort_index()

#Record the median number of games played by the remaining goalies, and remove rows below median
Median_GP = SV['GP'].median()
SV = SV[SV['GP']>SV['GP'].median()]

#Calculate average save percentage of remaining goalies
SV_Average = SV['Mean'].mean() *100

#Caluclate average standard deviation of the save perectage
SV_Deviation =SV['SD'].mean() *100

#Calculate effect size over a range of hypothetical save percentages compared to average
Effect_Size = (np.arange(93, 100.25, 0.25) - SV_Average)/SV_Deviation

#Set alpha to be constant at 0.05
alpha = 0.05

#Calculate sample size required to achieve specified power over the range of effect sizes calculated above 
Sample_80 = []
Sample_85 = []
Sample_90 = []
Sample_95 = []
for effect in Effect_Size:
    Sample_80.append(tt_solve_power(effect_size=effect,nobs=None,alpha=alpha,power=0.8,alternative='two-sided'))
    Sample_85.append(tt_solve_power(effect_size=effect,nobs=None,alpha=alpha,power=0.85,alternative='two-sided'))
    Sample_90.append(tt_solve_power(effect_size=effect,nobs=None,alpha=alpha,power=0.9,alternative='two-sided'))
    Sample_95.append(tt_solve_power(effect_size=effect,nobs=None,alpha=alpha,power=0.95,alternative='two-sided'))

#Oragnze calculated sample sizes into data frame    
SampleSizes = pd.DataFrame({'SV%': np.arange(93, 100.25, 0.25), '80': Sample_80, '85': Sample_85, '90': Sample_90, '95': Sample_95})

#Plot the sample size needed as for each hypothetical save perecentage (effect size) at given power
ax = plt.gca()
SampleSizes.plot(kind='line',x='SV%',y='80', ax=ax)
SampleSizes.plot(kind='line',x='SV%',y='85', color='red', ax=ax)
SampleSizes.plot(kind='line',x='SV%',y='90', color='black', ax=ax)
SampleSizes.plot(kind='line',x='SV%',y='95', color='green', ax=ax)
plt.title('Sample Size for Evaluating Goalie Performance')
plt.ylabel('Games Needed')
plt.xlabel('Goalie Performance (SV%)')
plt.show()

#Export data dataframes to excel
SampleSizes.to_excel(r'C:\Users\nickr\OneDrive\Desktop\LLS_Blog\GoaliePowerSampleSize.xlsx', index = False)
