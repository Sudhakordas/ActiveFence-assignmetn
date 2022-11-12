import os
import re
import numpy as np
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import csv
import urllib.request
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


options = webdriver.ChromeOptions() 
options.add_experimental_option("excludeSwitches", ["enable-logging"])

options.add_argument('--headless')
options.add_argument('--disable-gpu')

#THIS INITIALIZES THE DRIVER (AKA THE WEB BROWSER)
path = Service(r'C:\Users\Sudhakor\Scrapy\chromedriver.exe')
driver = webdriver.Chrome(options=options, service = path)

driver.get("https://www.tiktok.com/")
source_code = driver.page_source

def url_body(source_code):
    soup = BeautifulSoup(source_code, 'html.parser')
    url_body = soup.find_all('div', class_ = 'tiktok-1mo2fkg-DivUserLinkContainer e797se20')
    return url_body
    
body = url_body(source_code)

url_list = []
def url_generator(body):
    for i in body:
        url = 'https://www.tiktok.com' + i.find('a')['href']
        url_list.append(url)
url_generator(body)

def finding_content(url):
    driver.get(url)
    source_code = driver.page_source
    soup = BeautifulSoup(source_code, 'html.parser')
    name = soup.find('h2', class_ = "ekmpd5l5").text.strip()
    about = soup.find('h2', class_ = 'e1457k4r3').text
    about = re.sub('[^a-zA-Z0-9]', ' ', about)
    about = re.sub(' +', ' ', about).strip()
    img_link = soup.find('img', class_ = 'e1e9er4e1')['src']
    following = soup.find('strong', title = 'Following').text
    followers = soup.find('strong', title = 'Followers').text
    likes = soup.find('strong', title = 'Likes').text

    all_posts = []
    engagement = 0
    posts_main = []  
    try:
        posts_main = soup.find_all('div', class_ = 'e19c29qe7')
        if len(posts_main)> 50:
            posts_main = posts_main[:50]
        else:
            pass

        for post in posts_main:
            post_link = post.find('a')['href']
            views = post.find('strong', class_ = 'video-count tiktok-1nb981f-StrongVideoCount e148ts222').text
            if views.endswith('M'):
                views = views.split('M')[0]
                try:   
                    fract = views.split('.')[1]
                    le =(3-len(fract))
                    zero = ''
                    for i in np.zeros(le):
                        zero += '0' 
                    views = (views + zero).replace('.', '')
                except:
                    views = str(views) + ('000')
            elif views.endswith('B'):
                try:
                    fract = views.split('.')[1]
                    le =(6-len(fract))
                    zero = ''
                    for i in np.zeros(le):
                        zero += '0' 
                    views = (views + zero).replace('.', '')
                except:
                    views = str(views) + ('000000')            
            elif views.endswith('K'):
                views = views.split('K')[0]
                try:    
                    views = views.replace('.', '')
                except:
                    pass
            else: 
                views = int(views)/1000     
            engagement+=int(views)
            all_posts.append(post_link)
    except:
        all_posts = []

    average_engagement = str(np.round(engagement/len(posts_main),2))+'K'

    # print('Profile name: ', name)
    # print('About Section: ', about)
    # print('img link: ',img_link)
    # urllib.request.urlretrieve(img_link,'image'+'.jpeg')
    # print('Number of following: ', following)
    # print('Number of followers: ', followers)
    # print('Number of Likes: ', likes)
    # print('All the posts are: ', all_posts)
    # print('Average engagement is: ', average_engagement, engagement, len(posts_main))
    return name, img_link, about, likes, followers, following, all_posts, average_engagement

profile_list = []
for url in url_list:
    name, img_link, about, likes, followers, following, all_posts, average_engagement = finding_content(url)
    profile = {'Username': name,
    'Image':img_link,
    'About':about,
    'Likes': likes,
    'Followers' : followers,
    'Following' : following,
    'Posts' : all_posts,
    'Average engagement' : average_engagement
    }
    print(profile)
    profile_list.append(profile)
    print('Saving profile: ',name)

df = pd.DataFrame(profile_list)
df.to_csv('TIKTOK_DATA.csv', index = False)

driver.quit()