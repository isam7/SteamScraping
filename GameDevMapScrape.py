# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 23:02:33 2022

@author: phyis
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
from SteamScrape import removeUnencodableCharacters

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

startTime = time.time()
    
numLoops = 0

csvFile = open('GameDevLocations.csv', 'w+')

writer = csv.writer(csvFile)
writer.writerow(('company', 'city', 'state/province', 'country','alteredTextBool'))

#Loop over all different webpages at gamedevmap
for startNumber in range(40+1):
    
    response = requests.get(url='https://www.gamedevmap.com/index.php?location=&country=&state=&city=&query=&type=Developer&start={}&count=100'.format(startNumber*100+1))
    bs = BeautifulSoup(response.text, 'html.parser')
    
    #Table on current page
    table = bs.find('table',cellpadding='6').find_all('tr')
    
    #Last index in table
    lastIndex = len(table) - 1
    
    #Iterate over all rows below header row, i.e., starting with row 4
    for row in table[4:lastIndex]:
        
        columns = row.find_all('td')
        
        print(columns[0].text.strip(),columns[3].text.strip(),columns[4].text.strip(),columns[5].text.strip())
        
        try:
            writer.writerow((columns[0].text.strip(),\
                             columns[3].text.strip(),\
                             columns[4].text.strip(),\
                             columns[5].text.strip(),\
                             False))
            
        except UnicodeEncodeError:
            writer.writerow((removeUnencodableCharacters(columns[0].text.strip()),\
                             removeUnencodableCharacters(columns[3].text.strip()),\
                             removeUnencodableCharacters(columns[4].text.strip()),\
                             removeUnencodableCharacters(columns[5].text.strip()),\
                             True))
        
    # print(bs.find('table',cellpadding='6').find_all('tr')[17].find_all('td')[0].text)
    # print(bs.find('table',cellpadding='6').find_all('tr')[17].find_all('td')[3].text.strip())
    # print(bs.find('table',cellpadding='6').find_all('tr')[17].find_all('td')[4].text.strip())
    # print(bs.find('table',cellpadding='6').find_all('tr')[17].find_all('td')[5].text.strip())
    # print(len(bs.find('table',cellpadding='6').find_all('tr')))
    
    time.sleep(5)

csvFile.close()

print('Time elapsed: {} seconds'.format(time.time() - startTime))

# #Get info for specific app from Steam
# def getDeveloperLocations():
    
#     #Access game's webpage
#     appUrl = 'https://www.gamedevmap.com/index.php?location=&country=&state=&city=&query=&type=Developer&start=1&count=100'
#     html = urlopen(appUrl)
#     bs = BeautifulSoup(html, 'html.parser')
    
#     #Get app developer name
#     try:
#         developerName = bs.find('div', {'class' : 'summary column', 'id' : 'developers_list'}).get_text(strip=True)
#         # print(developerName)
#     except:
#         developerName = np.nan
#         # print("Couldn't find developer name.")
    
#     #Get developer city
#     try:
#         releaseDate = bs.find('div', class_='grid_content grid_date').get_text(strip=True)
#         # print('Release Date:', releaseDate)
        
#     except:
#         releaseDate = np.nan
#         # print('No release date.')
    
#     #Get developer state/province
#     try:
#         price = bs.find('meta', itemprop='price')['content']
#         # print('Price: ${}'.format(price))
        
#     except:
#         price = np.nan
#         # print('No price to report.')
    
    
#     #Get developer country
#     try:
#         #Get strings of total and recent reviews
#         reviewTotalStrings = [bs.find_all('span',
#                                text=re.compile('\(.*?reviews\)'))[i].get_text(strip=True)
#                         for i in range(len(bs.find_all('span',
#                                                text=re.compile('\(.*?reviews\)'))))]
        
#         #Get number of total and recent reviews;
#         #trim of parentheses and 'reviews' string;
#         #remove commas and convert review number strings to integers
#         reviewNumbers = [int(reviewTotalStrings[i][1:reviewTotalStrings[i].index('r')-1].replace(',',''))
#                          for i in range(len(reviewTotalStrings))]
        
#         #Get total number of reviews
#         numReviews = max(reviewNumbers)
        
#         # print('Number of reviews:', numReviews)
        
#     except:
#         numReviews = np.nan
#         # print('No reviews.')
    
    
#     return [appId, name, developerName, releaseDate, price, numReviews, positiveReviewPercentage,
#             appGenre, tagsList, appType, dlcBool, appDesc]
    