from urllib.request import HTTPError
from urllib.request import urlopen
from datetime import date
from directoryref import HTMLReportDirectory
import re
import os

HTMLReportDirectory = 'C:\\Users\\nickr\\OneDrive\\Desktop\\LLS_Blog\\GoaltenderClutch\\'

#Number of games in NHL Season: 1230
#First year that NHL.com released HTML Reports: 2003-2004
year = str(20192020)
gamenumber = str(20001)

def numberofcycles(year):
	return int(date.today().year) - int(year[:4])

def incyear(year):
	year = int(year)
	year = year + 10001
	return str(year)

def incgamenum(gamenumber):
	gamenumber = int(gamenumber)
	if gamenumber<21230:
		gamenumber += 1
	else:
		20001

	return str(gamenumber)


def nhlhtmlsheeturl(year, gamenumber):
	url = "http://www.nhl.com/scores/htmlreports/" + year + "/PL0" + gamenumber + ".HTM"
	return url

def createfile(yeardirectory):
	
	if not os.path.exists(yeardirectory):
    		os.makedirs(yeardirectory)

def yearwithhyphen(year):
	year = year[:4] + "-" + year[-4:]
	return year

def sourcecodetotext(url, gamenumber, year):

	try:
		webPage=urlopen(url)
		rawSrc = makestringpath(yearwithhyphen(year)) + "\\" + gamenumber + ".txt"
		wRawSrc = open(rawSrc, mode="wb")
		wPageSrc=webPage.read()
		webPage.close()
		wRawSrc.write(wPageSrc)

	except HTTPError:
		print("Game %s in year %s does not exist in HTML Report database" %(gamenumber, year))

def makestringpath(year):
	directory = HTMLReportDirectory + year
	return directory


for _ in range(1230*numberofcycles(year)):

	url = nhlhtmlsheeturl(year, gamenumber)
	sourcecodetotext(url, gamenumber, year)
	print(gamenumber)
	gamenumber = incgamenum(gamenumber)

	if int(gamenumber) == 20001:
		year = incyear(year)
		createfile(makestringpath(yearwithhyphen(year)))
		print(yearwithhyphen(year))
