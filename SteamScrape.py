# -*- coding: utf-8 -*-
"""
Created on Sun May  8 21:30:27 2022

@author: isam1
"""

from urllib.request import Request, urlopen
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import datetime
import random
import re
import requests
import json
import numpy as np
import pandas as pd
import time
from urllib.error import HTTPError
import csv

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

#Get list of Steam apps with Steam API
steamAppUrl = 'http://api.steampowered.com/ISteamApps/GetAppList/v0002/?format=json'
response = requests.get(steamAppUrl)
AppList = response.json()['applist']['apps']

def getAppInfo(appId):
    
    #Access game's webpage
    appUrl = 'https://store.steampowered.com/app/{}'.format(appId)
    html = urlopen(appUrl)
    bs = BeautifulSoup(html, 'html.parser')
    
    #Get app name
    try:
        name = bs.find('div', id='appHubAppName').get_text()
        print(name)
    except AttributeError:
        name = np.nan
        print('No name/failed to load page.')
    
    #Get app release date
    try:
        releaseDate = bs.find('div', class_='grid_content grid_date').get_text(strip=True)
        print('Release Date:', releaseDate)
        
    except (AttributeError, ValueError, TypeError):
        releaseDate = np.nan
        print('No release date.')
    
    #Get app price
    try:
        price = bs.find('meta', itemprop='price')['content']
        print('Price: ${}'.format(price))
        
    except TypeError:
        price = np.nan
        print('No price to report.')
    
    
    #Get total number of reviews
    try:
        #Get strings of total and recent reviews
        reviewTotalStrings = [bs.find_all('span',
                               text=re.compile('\(.*?reviews\)'))[i].get_text(strip=True)
                        for i in range(len(bs.find_all('span',
                                               text=re.compile('\(.*?reviews\)'))))]
        
        #Get number of total and recent reviews;
        #trim of parentheses and 'reviews' string;
        #remove commas and convert review number strings to integers
        reviewNumbers = [int(reviewTotalStrings[i][1:reviewTotalStrings[i].index('r')-1].replace(',',''))
                         for i in range(len(reviewTotalStrings))]
        
        #Get total number of reviews
        numReviews = max(reviewNumbers)
        
        print('Number of reviews:', numReviews)
        
    except (AttributeError, ValueError, TypeError):
        numReviews = np.nan
        print('No reviews.')
    
    try:
        #Get string talking about the fraction of positive reviews
        positiveReviewPercentageString = bs.find('div', 
                                             class_='user_reviews_summary_row',
                                             onclick="window.location='#app_reviews_hash'"
                                             )['data-tooltip-html']
        #Clean string; get the percent of positive reviews
        positiveReviewPercentage = positiveReviewPercentageString[
            :positiveReviewPercentageString.index('%')+1]
        print('{} of reviews are positive.'.format(positiveReviewPercentage))
        
    except (ValueError, TypeError):
        positiveReviewPercentage = np.nan
        print('No review percentage to report.')
    
    #Get list game-tag strings
    try:
        tagsList = [bs.find_all('a', class_='app_tag')[i].get_text(strip=True)
                for i in range(len(bs.find_all('a', class_='app_tag')))]
        print(tagsList)
        
    except:
        tagsList = []
        print('Could not obtain tags list.')
            
    
    # #Get other app info from SteamDB
    # appUrlDb = 'https://steamdb.info/app/{}/graphs/'.format(appId)
    # headers = {'User-Agent': 'Mozilla/5.0'}
    # req = Request(appUrlDb,headers=headers)
    # htmlDb = urlopen(req)
    # bsDb = BeautifulSoup(htmlDb, 'html.parser')
    
    # #Get app type
    # try:
    #     appType = bsDb.find('td', itempro='applicationCategory').get_text()
    #     print(appType)
    
    # except (AttributeError, ValueError, TypeError):
    #     print('Could not find app type.')
    
    #Get app type header
    try:
        appType = bs.find('div', class_='blockbg').a.get_text()
        print('App type: {}'.format(appType))
        
    except (AttributeError, ValueError, TypeError):
        appType = np.nan
        print('No app type found.')
    
    #Is it DLC?
    try:
        dlcString = bs.find('div',text='Downloadable Content').get_text()
        dlcBool = (type(dlcString) != '')
        print('Is this DLC?',dlcBool)
        
    except (AttributeError, ValueError, TypeError):
        dlcBool = False
        print('Not DLC.')
        
    #Get game description
    try:
        appDesc = bs.find('meta', {'name' : 'Description'})['content']
        print(appDesc)
        
    except (AttributeError, ValueError, TypeError):
        appDesc = np.nan
        print('No game description found.')
        
    # #Is it a downloadable soundtrack?
    # try:
    #     dlsString = bs.find('div',text='Downloadable Soundtrack').get_text()
    #     dlsBool = (type(dlsString) != '')
    #     print('Is this a downloadable soundtrack?',dlsBool)
        
    # except (AttributeError, ValueError, TypeError):
    #     dlsBool = False
    #     print('Not a downloadable soundtrack.')
        
    # #Is it a video?
    # try:
    #     videoString = bs.find('h2',text='Steam Video').get_text()
    #     videoBool = (type(videoString) != '')
    #     print('Is this a video?',videoBool)
         
    # except (AttributeError, ValueError, TypeError):
    #     videoBool = False
    #     print('Not a video.')
 
    print('--------------------------------------------------------------------')
    
    return [appId, name, releaseDate, price, numReviews, positiveReviewPercentage,
            tagsList, appType, dlcBool, appDesc]
    
def getRandomAppInfo():
    random.seed(datetime.datetime.now())
    
    randomAppId = random.choice(AppList)['appid']
    print(randomAppId)
    
    return getAppInfo(randomAppId)

def removeUnencodableCharacters(string):
    
    #Remove unencodable characters from strings
    output = ''
    
    for character in string:
        
        #Check if character is a normal keyboard character
        #(like note a weird parenthesis or kanji)
        if ord(character) < 128:
            output += character
    
    return output

#Scrapes all apps from Steam
def getSomeRandomAppsInfo():
    startTime = time.time()
        
    numLoops = 0
    
    csvFile = open('SteamAppsInfo.csv', 'w+')
    
    writer = csv.writer(csvFile)
    writer.writerow(('appId','name','releaseDate','price','numReviews',
                     'positiveReviewPercentage','tagsList','appType','dlcBool',
                     'appDesc','alteredNameOrDescBool'))
    while numLoops < 100:
        
        try:
            appInfo = getRandomAppInfo()
            
            appType = appInfo[7];
            
            #Check there is an app type, i.e., that appType =/= np.nan
            if appType != np.nan:
                
                #Check it's a game
                if appType == 'All Games':
                    
                    # writer = csv.writer(csvFile)
                    # writer.writerow(tuple(appInfo))
                    
                    try:
                        writer = csv.writer(csvFile)
                        writer.writerow(tuple(appInfo + [False]))
                    
                    except UnicodeEncodeError:
                        #Rewrite unencodable game name and/or description
                        try:
                            appInfo[1] = removeUnencodableCharacters(appInfo[1])
                            appInfo[9] = removeUnencodableCharacters(appInfo[9])
                            
                            writer = csv.writer(csvFile)
                            writer.writerow(tuple(appInfo + [True]))
                        except:
                            print('Failed to rewrite unencodable game description.')
                    
                    except:
                        print('Failed to write to CSV.')
                        return
                
        except HTTPError:
            print('HTTP Error!')
            pass
            
        time.sleep(0.6) #Delay scraping a little bit to be nice
            
        numLoops += 1
        
        
        
        print("{} seconds elapsed.".format(time.time() - startTime))
        
        
    csvFile.close()
    

    
    