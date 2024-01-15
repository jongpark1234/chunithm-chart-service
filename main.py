from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.options import *
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import json
import threading
import numpy as np

from enums import Rank

from html2image import Html2Image
from decimal import Decimal
from typing import List

from config import *
from fetchURL import *

    
def parseWebelement(diff: int, obj: List[WebElement]):
    namelist = flatten(getChartName(obj)) # song name list
    scorelist = flatten(getChartScore(obj)) # song score list
    
    # Mask only indexes with non-zero ( played at least once ) scores
    mask = scorelist != '0'
    namelist = namelist[mask]
    scorelist = scorelist[mask]
    for song in chart['songs']:
        if song['category'] == "WORLD'S END": # skip WORLD'S END
            continue
        if song['title'] in namelist:
            curidx = int(np.where(namelist == song['title'])[0]) # 현재 chart로 조회중인 노래가 WebElement 노래 리스트에서 몇 번째 인덱스에 있는지
            
            name = str(namelist[curidx]) # 이름 ( str )
            score = str(scorelist[curidx]) # 점수 ( str )
            scoreValue = int(score.replace(',', '')) # 점수 ( int )
            diffValue = ['basic', 'advanced', 'expert', 'master', 'ultima'][diff] # 난이도 ( str )
            level = song['sheets'][diff]['internalLevel'] # 레벨 ( str )
            levelValue = song['sheets'][diff]['internalLevelValue'] # 레벨 ( float )
            ratingValue = calc_rating(scoreValue, level) # 레이팅 ( Decimal )
            rating = f'{ratingValue:.2f}' # 레이팅 ( str )
            image = IMAGE_DATA_FETCH_URL + song['imageName'] # 커버 이미지 ( str )
            
            # save at ret array
            result.append({
                'name': name,
                'score': score,
                'scoreValue': scoreValue,
                'diff': diff,
                'diffValue': diffValue,
                'level': level,
                'levelValue': levelValue,
                'rating': rating,
                'ratingValue': ratingValue,
                'image': image
            })


def calc_rating(score: int, internal_level: float) -> Decimal:
    baselvl = Decimal(str(internal_level or 0)) * 10_000
    rating = Decimal(0)

    if score >= 1_009_000:
        rating = baselvl + 21_500
    elif score >= 1_007_500:
        rating = baselvl + 20_000 + (score - 1_007_500)
    elif score >= 1_005_000:
        rating = baselvl + 15_000 + (score - 1_005_000) * 2
    elif score >= 1_000_000:
        rating = baselvl + 10_000 + (score - 1_000_000)
    elif score >= 975_000:
        rating = baselvl + Decimal(score - 975_000) * 2 / 5
    elif score >= 900_000:
        rating = baselvl - 50_000 + Decimal(score - 900_000) * 2 / 3
    elif score >= 800_000:
        rating = (baselvl - 50_000) / 2 + ((score - 800_000) * ((baselvl - 50_000) / 2)) / 100_000
    elif score >= 500_000:
        rating = (((baselvl - 50_000) / 2) * (score - 500_000)) / 300_000

    if rating < 0 and internal_level is not None and internal_level > 0:
        rating = Decimal(0)

    return rating / 10_000
def getChartName(obj: List[WebElement]) -> list:
    return list(map(lambda x: x.split('\n')[1::4], map(lambda y: y.text, obj)))

def getChartScore(obj: List[WebElement]) -> list:
    return list(map(lambda x: x.split('\n')[2::4], map(lambda y: y.text, obj)))

def flatten(obj: list) -> np.ndarray[str]:
    return np.array([item for sublist in obj for item in sublist])


result = []
chart = json.load(open('chart.json', 'r', encoding='utf-8'))

### =================== options =================== ###
options = webdriver.ChromeOptions()                   #
options.add_argument('headless')                      #
options.add_argument("window-size=1920x1080")         #
options.add_argument("disable-gpu")                   #
options.add_argument("disable-infobars")              #
options.add_argument("--disable-extensions")          #
options.add_experimental_option('prefs', {            #
    'profile.default_content_setting_values': {       #
        'cookies': 2,                                 #
        'images': 2,                                  #
        'plugins': 2,                                 #
        'popups': 2,                                  #
        'geolocation': 2,                             #
        'notifications': 2,                           #
        'auto_select_certificate': 2,                 #
        'fullscreen': 2,                              #
        'mouselock': 2,                               #
        'mixed_script': 2,                            #
        'media_stream': 2,                            #
        'media_stream_mic': 2,                        #
        'media_stream_camera': 2,                     #
        'protocol_handlers': 2,                       #
        'ppapi_broker': 2,                            #
        'automatic_downloads': 2,                     #
        'midi_sysex': 2,                              #
        'push_messaging': 2,                          #
        'ssl_cert_decisions': 2,                      #
        'metro_switch_to_desktop': 2,                 #
        'protected_media_identifier': 2,              #
        'app_banner': 2,                              #
        'site_engagement': 2,                         #
        'durable_storage': 2                          #
    }                                                 #
})                                                    #
caps = DesiredCapabilities.CHROME                     #
caps['pageLoadStrategy'] = 'none'                     #
### =============================================== ###

playDataByDiff = [] # return array

driver = webdriver.Chrome(options=options) # apply option
driver.maximize_window()

driver.get(LOGIN_URL) # open login page
driver.implicitly_wait(10)

driver.find_element(By.CLASS_NAME, 'c-button--openid--twitter').click() # click the button of 'login with twitter'
driver.find_element(By.ID, 'username_or_email').send_keys(TWITTER_ID) # put username
driver.find_element(By.ID, 'password').send_keys(TWITTER_PW) # put password
driver.find_element(By.ID, 'allow').click() # click allow button

driver.get(VS_URL) # open vs page
driver.implicitly_wait(10)

for diff in range(5):
    
    diffRadiolist = driver.find_elements(By.XPATH, '/html/body/div/div/div/div[1]/div[3]/div[2]/div[3]/form/div[2]/input') # difficulty radio button WebElements
    diffRadio = diffRadiolist[diff] # radio button ( i_0 -> basic, i_1 -> advanced, i_2 -> expert, i_3 -> master, i_4 -> ultima )

    driver.execute_script("arguments[0].setAttribute('checked', 'checked');", diffRadio) # difficulty button click
    driver.find_element(By.CLASS_NAME, 'btn_battle').click() # battle button click

    genrelist = driver.find_elements(By.XPATH, '/html/body/div/div/div/div[1]/div[3]/div[2]/div[5]/*')[1:]
    parseWebelement(diff, genrelist)

result.sort(key=lambda x: -x['ratingValue'])

html_content = open('styleHead.html', encoding='utf-8').read() + f'''<body>
    <div class="background">
        <div class="titleContainer">
            <div class="infoContainer">여기디자인은또언제함</div>
            <div class="infoContainer">하....</div>
        </div>
        <div class="ratingContainer">
            {'\n'.join(map(lambda song: f'''<div class="element">
        <div class="elementOrder"># {song[0] + 1}</div>
        <img class="songImage" src="{song[1]['image']}" style="box-shadow: 0 0 3px 1px darkorchid;"/>
        <div class="songInfoContainer">
            <span class="songTitle">{song[1]['name']}</span>
            <div class="columnContainer">
                <div class="textRowContainer">
                    <span class="songDetailKey">CONST -</span>
                    <div class="textRowContainer">    
                        <span class="songText">&nbsp;{song[1]['level'].split('.')[0]}.</span>
                        <span class="songRatingDetail">{song[1]['level'].split('.')[1]}</span>
                    </div>
                </div>
                <div class="textRowContainer">
                    <span class="songDetailKey">SCORE -</span>
                    <span class="songText">&nbsp;{song[1]['score']}</span>
                </div>
            </div>
            <div class="rowContainer">
                <div class="textRowContainer">
                    <span class="songRating">↪ {song[1]['rating'].split('.')[0]}.</span>
                    <span class="songRatingDetail">{song[1]['rating'].split('.')[1]}</span>
                </div>
                <span class="songRank" style="text-shadow: 0 0 0.3em darkgrey, 0 0 0.3em darkgrey, 0 0 0.3em darkgrey;">{Rank.from_score(song[1]['scoreValue'])}</span>
            </div>
        </div>
    </div>
''', enumerate(result[:30])))}
        </div>
    </div>
</body>'''

hti = Html2Image()
hti.screenshot(html_str=html_content, save_as='output.png')