# -*- coding: utf-8 -*-
"""
Created on Sun May  8 21:30:27 2022

@author: isam1
"""

from urllib.request import Request, urlopen
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from proxybroker import Broker
import asyncio
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

#Get info for specific app from Steam
def getAppInfo(appId):
    
    #Access game's webpage
    appUrl = 'https://store.steampowered.com/app/{}'.format(appId)
    html = urlopen(appUrl)
    bs = BeautifulSoup(html, 'html.parser')
    
    #Get app name
    try:
        name = bs.find('div', id='appHubAppName').get_text()
        # print(name)
    except:
        name = np.nan
        # print('No name/failed to load page.')
        
    #Get app developer name
    try:
        developerName = bs.find('div', {'class' : 'summary column', 'id' : 'developers_list'}).get_text(strip=True)
        # print(developerName)
    except:
        developerName = np.nan
        # print("Couldn't find developer name.")
    
    #Get app release date
    try:
        releaseDate = bs.find('div', class_='grid_content grid_date').get_text(strip=True)
        # print('Release Date:', releaseDate)
        
    except:
        releaseDate = np.nan
        # print('No release date.')
    
    #Get app price
    try:
        price = bs.find('meta', itemprop='price')['content']
        # print('Price: ${}'.format(price))
        
    except:
        price = np.nan
        # print('No price to report.')
    
    
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
        
        # print('Number of reviews:', numReviews)
        
    except:
        numReviews = np.nan
        # print('No reviews.')
    
    try:
        #Get string talking about the fraction of positive reviews
        positiveReviewPercentageString = bs.find('div', 
                                             class_='user_reviews_summary_row',
                                             onclick="window.location='#app_reviews_hash'"
                                             )['data-tooltip-html']
        #Clean string; get the percent of positive reviews
        positiveReviewPercentage = positiveReviewPercentageString[
            :positiveReviewPercentageString.index('%')+1]
        # print('{} of reviews are positive.'.format(positiveReviewPercentage))
        
    except:
        positiveReviewPercentage = np.nan
        # print('No review percentage to report.')
    
    #Get app genre
    try:
        appGenre = bs.find_all('span', {'data-panel' : True})[0].get_text(strip=True).split(",")
        # print('App genre(s): {}'.format(appGenre))
        
    except:
        appGenre = np.nan
        # print('Could not get app genre(s).')
    
    #Get list game-tag strings
    try:
        tagsList = [bs.find_all('a', class_='app_tag')[i].get_text(strip=True)
                for i in range(len(bs.find_all('a', class_='app_tag')))]
        # print(tagsList)
        
    except:
        tagsList = []
        # print('Could not obtain tags list.')
            
    
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
        # print('App type: {}'.format(appType))
        
    except:
        appType = np.nan
        # print('No app type found.')
    
    #Is it DLC?
    try:
        dlcString = bs.find('div',text='Downloadable Content').get_text()
        dlcBool = (type(dlcString) != '')
        # print('Is this DLC?',dlcBool)
        
    except:
        dlcBool = False
        # print('Not DLC.')
        
    #Get game description
    try:
        appDesc = bs.find('meta', {'name' : 'Description'})['content']
        # print(appDesc)
        
    except:
        appDesc = np.nan
        # print('No game description found.')
        
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
 
    return [appId, name, developerName, releaseDate, price, numReviews, positiveReviewPercentage,
            appGenre, tagsList, appType, dlcBool, appDesc]
    
#Get info for a random app on Steam
def getRandomAppInfo():
    random.seed(datetime.datetime.now())
    
    randomAppId = random.choice(AppList)['appid']
    
    return getAppInfo(randomAppId)

#Remove unencodable characters from strings
def removeUnencodableCharacters(string):
    output = ''
    
    for character in string:
        
        #Check if character is a normal keyboard character
        #(i.e., check that it is not a weird parenthesis or kanji or something)
        
        try:
            if ord(character) < 128:
                output += character
                
        except TypeError:
            pass
    
    return output

#Scrapes all apps from Steam; stores data in csv file
#
#Logs scraping in txt file
def getAllAppsInfo():
    startTime = time.time()
        
    numLoops = 0
    
    csvFile = open('SteamAppsInfo.csv', 'w+')
    scrapingLogsTxt = open('SteamScrapingLogs.txt', 'w')
    
    writer = csv.writer(csvFile)
    writer.writerow(('appId','name', 'developerName', 'releaseDate','price',
                     'numReviews', 'positiveReviewPercentage', 'appGenre','tagsList','appType','dlcBool',
                     'appDesc','alteredTextBool'))
    
    failureCount = 0
    
    for app in AppList:
        
        try:
            appInfo = getAppInfo(app['appid'])
            
            appType = appInfo[9];
            
            print('Trying to get info from {} (App ID: {})...'.format(appInfo[1],appInfo[0]))
            try:
                scrapingLogsTxt.write('Trying to get info from {} (App ID: {})...\n'.format(appInfo[1],appInfo[0]))
                
            except UnicodeError:
                try:
                    appInfo[1] = removeUnencodableCharacters(appInfo[1])
                    
                    scrapingLogsTxt.write('Trying to get info from {} (App ID: {})...\n'.format(appInfo[1],appInfo[0]))
                except:
                    print('Failed to write name of App {} into data logs.'.format(appInfo[0]))
                    scrapingLogsTxt.write('Failed to write name of App {} into data logs.\n')
            
                
            
            #Check there is an app type, i.e., that appType =/= np.nan
            if appType != np.nan:
                
                #Check it's a game
                if appType == 'All Games':
                    
                    # writer = csv.writer(csvFile)
                    # writer.writerow(tuple(appInfo))
                    
                    try:
                        writer = csv.writer(csvFile)
                        writer.writerow(tuple(appInfo + [False]))
                        print('Wrote data to CSV successfully!')
                        scrapingLogsTxt.write('Wrote data to CSV successfully!\n')
                    
                    except UnicodeEncodeError:
                        #Rewrite unencodable game name and/or description
                        try:
                            appInfo[1] = removeUnencodableCharacters(appInfo[1])
                            appInfo[2] = removeUnencodableCharacters(appInfo[2])
                            appInfo[11] = removeUnencodableCharacters(appInfo[11])
                            
                            writer = csv.writer(csvFile)
                            writer.writerow(tuple(appInfo + [True]))
                            
                            print('Wrote data to CSV successfully!')
                            scrapingLogsTxt.write('Wrote data to CSV successfully!\n')
                        except:
                            print('Failed to rewrite unencodable game description.')
                            scrapingLogsTxt.write('Failed to rewrite unencodable game description.\n')
                    
                    except:
                        print('Failed to write to CSV.')
                        scrapingLogsTxt.write('Failed to write to CSV.\n')
                
                else:
                    print('Not a game. No data saved.')
                    scrapingLogsTxt.write('Not a game. No data saved.\n')
                
        except HTTPError:
            print('HTTP Error!')
            scrapingLogsTxt.write('HTTP Error!\n')
            pass
        
        except:
            print('Failed to get app info!')
            scrapingLogsTxt.write('Failed to get app info!\n')
            failureCount += 1
        
        print('--------------------------------------------------------------------')
        scrapingLogsTxt.write('--------------------------------------------------------------------\n')
        
        time.sleep(0.6) #Delay scraping a little bit to be nice
            
        numLoops += 1
        
        
        
        print("{} seconds elapsed.".format(time.time() - startTime))
        scrapingLogsTxt.write("{} seconds elapsed.\n".format(time.time() - startTime))
        
        
    print('Failed to get info on {} out of {} apps.'.format(failureCount,len(AppList)))
    scrapingLogsTxt.write('Failed to get info on {} out of {} apps.\n'.format(failureCount,len(AppList)))
    csvFile.close()
    scrapingLogsTxt.close()
    
#Get Steam reviews data
def getSteamReviewData(appId):
    
    #Access game's webpage
    appUrl = 'https://store.steampowered.com/appreviews/{}?json=1'.format(appId)
    response = requests.get(appUrl)
    
    return response

def getAllSteamReviews():
    startTime = time.time()
    
    numLoops = 1
    
    rawGames = pd.read_csv('SteamAppsInfo.csv', encoding = "ISO-8859-1")
    
    reviewJson = list()
    
    reviewScrapingLogsTxt = open('SteamScrapingLogs.txt', 'w')
    
    for appId in rawGames['appId'].to_list():
        
        try:
            reviewData = getSteamReviewData(appId).json()
            
            print('Scraping App #{}, iteration {}...'.format(appId,numLoops))
            reviewScrapingLogsTxt.write('Scraping App #{}, iteration {}...\n'.format(appId,numLoops))
            if reviewData['success'] == 1:
                print('Success!!')
                reviewScrapingLogsTxt.write('Success!!\n')
                
            else:
                print('Failure...')
                reviewScrapingLogsTxt.write('Failure...\n')
                
            print('Summary of App #{} reviews:'.format(appId))
            print(reviewData['query_summary'],'\n')
            print("{} seconds elapsed.".format(time.time() - startTime))
            reviewScrapingLogsTxt.write("{} seconds elapsed.\n".format(time.time() - startTime))
            print('--------------------------------------------------------------------')
            reviewScrapingLogsTxt.write('--------------------------------------------------------------------\n')
            
            reviewData['appId'] = appId
            
            reviewJson.append(reviewData)
        
        except:
            print('Failed to get data!')
            reviewScrapingLogsTxt.write('Failed to get data!')
        
        numLoops += 1
        
        time.sleep(0.3) #Delay scraping a little bit to be nice
        
    with open('SteamReviewsData2.json', 'w') as f:
        json.dump(reviewJson, f, indent=2)
    
    return

def getAllUsersInfo():
    #Get games owned by Steam user with a certain ID
    from requests.exceptions import HTTPError
    startTime = time.time()
        
    successCount = 0
    interactionsCount = 0
    
    csvFile = open('SteamUsersInfo.csv', 'w+')
    scrapingLogsTxt = open('SteamUserScrapingLogs.txt', 'w')
    
    writer = csv.writer(csvFile)
    writer.writerow(('userID','ownedAppIDs','userCountry','userState'))
    
    userIDs = pd.read_csv('SteamUsersIDs.csv', encoding = "ISO-8859-1")['userID'].values
    
    for chunk in range(0,len(userIDs),100):
    
        userList = userIDs[chunk:chunk + 100]
        
        #Create empty string to fill with comma-delimited list of user IDs (in bins of 100) to pass to Steam API in URL
        userListString = ''
        
        #Add users from current userList to string of users
        for user in userList:
            userListString += str(user) + ','
            
        #Remove last character from list, since it is an unecessary comma
        userListString = userListString[:-1]
        try:
            steamUserAPIUrl = 'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key=DB6B9F4DA3B3C4BD75840820BBFE4EB9&steamids={}&format=json'.format(userListString)
            userResponse = requests.get(steamUserAPIUrl)
            userResponseList = userResponse.json()['response']['players']
            
        except AttributeError as e:
            print('Attribute Error!')
        
        for user in userResponseList:
            
            print(user['steamid'])
            #Country and state of user, if known
            try:
                userCountry = user['loccountrycode']
            except:
                userCountry = np.nan
                print('Failed to get user country.')
            
            try:
                userState = user['locstatecode']
            except:
                userState = np.nan
                print('Failed to get user state.')
            
            
            try:
                steamUserUrl = 'https://steamcommunity.com/profiles/{}/games/?tab=all'.format(user['steamid'])
                html = urlopen(steamUserUrl)
                bs = BeautifulSoup(html, 'html.parser')
            except HTTPError as e:
                print(e.response.text)
            
            #BeautifulSoup finds the (hideous) javascript variable containing all the games owned by user
            appIds = bs.find('script', language='javascript').string
            
            #Regular expression makes the soup beautiful (finds all app IDs in the list)
            appIdsClean = re.findall('"appid":(.*?),"',appIds)
            
            if appIdsClean == []:
                print('No games publicly shown for this user.')
            else:
                print('Successfully collected app list for user {}!'.format(user['steamid']))
                interactionsCount += len(appIdsClean)
                successCount += 1
            appIdsClean = []
            print('Failed to get owned apps!')
            
            # print(userCountry)
            # print(userState)
            # print(appIdsClean)
            
            writer.writerow((user['steamid'],appIdsClean,userCountry,userState))
            print(user['steamid'],userCountry,userState)
            
            
            time.sleep(1)
       
        print('Success count:', successCount)
        print('Total user-item interactions:', interactionsCount)
        break
    csvFile.close()
    scrapingLogsTxt.close()
    
    return

# get n proxies from proxybroker
def getProxies(n):
    async def show(proxies):
        p = []
        while True:
                proxy = await proxies.get()
                if proxy is None: break
                p.append("{}://{}:{}".format(proxy.schemes[0].lower(), proxy.host, proxy.port))
        return p
    
    proxies = asyncio.Queue()
    broker = Broker(proxies)
    tasks = asyncio.gather(broker.find(types=['HTTP', 'HTTPS'], limit=n), show(proxies))
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(tasks)[1]

def getAllUsersInfoNoAPI():
    #Get games owned by Steam user with a certain ID
    from fake_useragent import UserAgent
    
    startTime = time.time()
    
    ua = UserAgent()
    
    successCount = 0
    interactionsCount = 0
    userCount = 1
    
    csvFile = open('SteamUsersInfoLongDelay.csv', 'w+')
    scrapingLogsTxt = open('SteamUserScrapingLogs.txt', 'w')
    
    writer = csv.writer(csvFile, lineterminator = '\n')
    writer.writerow(('userID','ownedAppIDs'))
    
    userIDs = pd.read_csv('SteamUsersIDs.csv', encoding = "ISO-8859-1")['userID'].values
    
    #Create proxy list
    # proxyTxt = open("proxies.txt", "r")

    # proxyIPs = []
    # for line in proxyTxt:
    #   rawProxies = line.strip()
    #   proxyIPs.append(rawProxies)
    
    # proxyTxt.close()
    
    for user in userIDs:
            
        print('Trying to get info from user #{} (User ID: {})...'.format(userCount,user))
        scrapingLogsTxt.write('Trying to get info from user {} (User ID: {})...\n'.format(userCount,user))
        
        try:
            steamUserUrl = 'https://steamcommunity.com/profiles/{}/games/?tab=all'.format(user)
            
            #Get random user agent
            header = {'User-Agent':str(ua.random)}
            # print(header)
            
            html = requests.get(steamUserUrl, headers=header).text
            bs = BeautifulSoup(html, 'html.parser')
            if bs.find('div', class_='profile_fatalerror') is not None:
                print('HTTPError: Too many requests!')
            
            try:
                #BeautifulSoup finds the (hideous) javascript variable containing all the games owned by user
                appIds = bs.find('script', language='javascript').string
                
                #Regular expression makes the soup beautiful (finds all app IDs in the list)
                appIdsClean = re.findall('"appid":(.*?),"',appIds)
                    
                if appIdsClean == []:
                    print('No games publicly shown for user ID {}.'.format(user))
                    scrapingLogsTxt.write('No games publicly shown for user ID {}.\n'.format(user))
                else:
                    print('Successfully collected app list for user ID {}!'.format(user))
                    scrapingLogsTxt.write('Successfully collected app list for user ID {}!\n'.format(user))
                    interactionsCount += len(appIdsClean)
                    successCount += 1
                
            except AttributeError:
                appIdsClean = []
                print('Failed to get owned apps for user ID {}!'.format(user))
                scrapingLogsTxt.write('Failed to get owned apps for user ID {}!\n'.format(user))
            
        except requests.exceptions.RequestException as e:
            appIdsClean = []
            print(e)
            print('HTTPError: Failed to connect.')
            scrapingLogsTxt.write('HTTPError: Failed to connect.\n')
        
        
            
        
        # print(userCountry)
        # print(userState)
        # print(appIdsClean)
        
        writer.writerow((user,appIdsClean))
        print(user)
        
        time.sleep(60)
       
        print('Time since start: {} min.'.format((time.time() - startTime)/60))
        print('Success count:', successCount)
        print('Total user-item interactions:', interactionsCount)
        print('Total users scraped: {}\n'.format(userCount))
        
        scrapingLogsTxt.write('Time since start:  {} min.\n'.format((time.time() - startTime)/60))
        scrapingLogsTxt.write('Success count: {}\n'.format(successCount))
        scrapingLogsTxt.write('Total user-item interactions: {}\n'.format(interactionsCount))
        scrapingLogsTxt.write('Total users scraped: {}\n'.format(userCount))
        
        userCount += 1
        
    csvFile.close()
    scrapingLogsTxt.close()
    
    return 

def getMyGames():
    
    myGames = open('myGamesData.txt','w')
    
    myGamesList = open('myGames.txt','r').read()
    
    myGames.write(str(re.findall('"appid":(.*?),"',myGamesList)))
    
    print(str(re.findall('"appid":(.*?),"',myGamesList)))
    
    myGames.close()
    
    return