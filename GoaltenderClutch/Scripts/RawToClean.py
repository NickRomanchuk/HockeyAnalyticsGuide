import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

#Set file path were game sheets are saved
HTMLReportDirectory = 'C:\\Users\\nickr\\OneDrive\\Desktop\\LLS_Blog\\GoaltenderClutch\\'

#Create loop to read in all the HTML game sheets saved on computer
Shots = {}
Goals = {}
for q in range(20001, 21084):
        data = []
        data = []
        score = []
        GameNumberString = str(q)
        print(GameNumberString)
        SeasonString = "2019-2020"

        #Read in HTML game sheet
        textlist = open(HTMLReportDirectory + SeasonString + "\\" + GameNumberString + ".txt", "r").read().splitlines()

        #Remove every instance in the list that is contained within "<" and ">"
        textlist = filter(None,[re.sub('<[^>]+>', '', i) for i in textlist])

        #Remove any instance in the list after '<!--', and also remove anything that contains only empty space 
        textlist = [x for x in textlist if not x.isspace()]

        #Identify location of play-by-play events in list
        size = len(textlist)
        event = ['GOAL','SHOT','FAC','MISS','STOP','DELPEN','PENL','GIVE','TAKE','HIT','BLOCK','PEND']
        idx_list = [idx + 1 for idx, val in enumerate(textlist) if val in event]

        #Based on the location of play-by-play events, convert to a list of list (each event is new list)
        res=[]
        for i in range(0, len(idx_list)):
                if i+1 == len(idx_list):
                        #-4 because there is information (ex. time, period) that relates to the event prior to the event location
                        res.append(textlist[idx_list[i]-4:])
                        break
                else:
                        res.append(textlist[idx_list[i]-4:idx_list[i+1]-4])
        
        #Convert list of play-by-play events into dataframe
        data=pd.DataFrame(res)
        
        #Identify the home and away Teams (unique three letter acronynm)
        idx_team = [i for i, s in enumerate(textlist) if 'On Ice' in s]
        Away_Team = textlist[idx_team[0]][:3]
        Home_Team = textlist[idx_team[1]][:3]

        #Identify the locations of goalie numbers playing when each of the play-by-play events occured
        Goalie_Index = []              
        for i in range(0, len(res)):
                Goalie_Index.append([idx + 1 for idx, val in enumerate(res[i]) if val == 'G'])

        #Extract the goalie number for each of the goalies when the play-by-play event occured
        Home_Goalie=[]
        Away_Goalie=[]
        for i in range(0, len(data.index)):
                #If the length is less than 2 that means only one goalie was playing
                if len(Goalie_Index[i])<2:
                        #If length is zero that means no goalies apply to the particular event
                        if len(Goalie_Index[i]) == 0:
                                Away_Goalie.append('None')
                                Home_Goalie.append('None')
                        #If length is 1 that means only one goalie was on the ice
                        #based on the location <>28 we can determine if it was the home or away goalie
                        elif Goalie_Index[i][0]<28:
                                Away_Goalie.append(data.iloc[i, Goalie_Index[i][0]-2])
                                Home_Goalie.append('None')
                        elif Goalie_Index[i][0]>28:
                                Away_Goalie.append('None')
                                Home_Goalie.append(data.iloc[i, Goalie_Index[i][0]-2])
                #If length is greater or equal to 2 than two goalies were on the ice
                elif len(Goalie_Index[i])>=2:
                        Away_Goalie.append(data.iloc[i, Goalie_Index[i][0]-2])
                        Home_Goalie.append(data.iloc[i, Goalie_Index[i][1]-2])

        #Now that we have the goalie numbers for the home/away teams for each event we can add that to the dataframe 
        data['Away_Goalie']=Away_Goalie
        data['Home_Goalie']=Home_Goalie

        #We will now filter the data so only periods 1-3 are included (i.e. no overtime or shootout)
        period = ['1','2','3']
        data=data[data[0].isin(period)]

        #Create new column with the team that the event occured for (i.e. unique three letter acronynm)
        data['Team']=data[4].str[:3]

        #Relabel event coloumn as 'Event'
        data['Event']=data[3]

        #Filter out columns we are no longer have interest in
        data=data[['Event','Team','Away_Goalie','Home_Goalie']]

        #Filter out events we are not interested in (i.e. leave only shots and goals)
        event = ['SHOT','GOAL']
        data = data[data['Event'].isin(event)]
        #data = data[~data.isin(['None'])].dropna()

        #reset the index now that the events have been removed
        data=data.reset_index()

        #Loop through all the events and tally the games score and record the shots/goals when the score differential is <=1
        score = [Home_Team, Away_Team]
        for i in range(0, len(data.index)):
                if abs(score.count(Home_Team)-score.count(Away_Team))<=1:
                        
                        if data['Event'][i]=='SHOT':
                                
                                if data['Team'][i] == Home_Team:
                                        if Away_Team + data['Away_Goalie'][i] in Shots.keys():
                                                Shots[Away_Team + data['Away_Goalie'][i]] += 1
                                        else:
                                                Shots[Away_Team + data['Away_Goalie'][i]] = 1                                             

                                elif data['Team'][i] == Away_Team:
                                        if Home_Team + data['Home_Goalie'][i] in Shots.keys():
                                                Shots[Home_Team + data['Home_Goalie'][i]] += 1
                                        else:
                                                Shots[Home_Team + data['Home_Goalie'][i]] = 1
        
                        elif data['Event'][i]=='GOAL':
                             
                                if data['Team'][i] == Home_Team:
                                        if Away_Team + data['Away_Goalie'][i] in Goals.keys():
                                                Goals[Away_Team + data['Away_Goalie'][i]] += 1
                                        else:
                                                Goals[Away_Team + data['Away_Goalie'][i]] = 1

                                elif data['Team'][i] == Away_Team:
                                        if Home_Team + data['Home_Goalie'][i] in Goals.keys():
                                                Goals[Home_Team + data['Home_Goalie'][i]] += 1
                                        else:
                                                Goals[Home_Team + data['Home_Goalie'][i]] = 1
                                             
                                score.append(data['Team'][i])
                                
                elif abs(score.count(Home_Team)-score.count(Away_Team))>1:
                        if data['Event'][i]=='GOAL':
                                score.append(data['Team'][i])

#Aggregate data for goalies that played for multipl teams                            
Shots['JCamp']=Shots['L.A36']+Shots['TOR36']
Goals['JCamp']=Goals['L.A36']+Goals['TOR36']

Shots['LDomi']=Shots['N.J70']+Shots['VAN30']
Goals['LDOmi']=Goals['N.J70']+Goals['VAN30']

Shots['Hutch']=Shots['TOR30']+Shots['COL35']
Goals['Hutch']=Goals['TOR30']+Goals['COL35']

Shots['RLehner']=Shots['CHI40']+Shots['VGK90']
Goals['RLehner']=Goals['CHI40']+Goals['VGK90']

#Remove the individual teams from the aggregated goalies
keys_to_remove = ('L.A36','TOR36','N.J70','VAN30','TOR30','COL35','CHI40','VGK90')
for k in keys_to_remove:
    Shots.pop(k, None)
    Goals.pop(k, None)

#Find the median number of shots faced by all goalies
median_values = []
for key in Shots.keys():
        median_values.append(Shots[key])

#Use 500 based on the median value being 540.5 and inspection of histogram
#np.median(median_values)
plt.hist(median_values, 20)
plt.show()
median = 500

#Remove the goalies that faced a below median number of shots
Saves = {}
for key in Shots.keys():
  if Shots[key] > median:
          Saves[key]=Shots[key]

#For remaining goalies calculate sv%
SavePercent = {}
for key in Saves:
        SavePercent[key] = (1 - (Goals[key]/(Saves[key]+Goals[key]))) * 100

SV = pd.DataFrame(data=SavePercent, index=[0])
SV.to_excel(r'C:\Users\nickr\OneDrive\Desktop\LLS_Blog\GoaltenderClutch\SituationalSV.xlsx', index = False)
