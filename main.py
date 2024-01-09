from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.options import *
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import re
import json
import math
import numpy as np

from enums import Rank

from html2image import Html2Image
from decimal import Decimal
from typing import Iterable

from config import *
from fetchURL import *

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

def getChartName(obj: list[WebElement]) -> list:
    return list(map(lambda x: x.split('\n')[1::4], map(lambda y: y.text, obj)))

def getChartScore(obj: list[WebElement]) -> list:
    return list(map(lambda x: x.split('\n')[2::4], map(lambda y: y.text, obj)))

def flatten(obj) -> np.ndarray:
    return np.array([item for sublist in obj for item in sublist])

chart = json.load(open('chart.json', 'r', encoding='utf-8'))


result = []

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument("window-size=1920x1080")
options.add_argument("disable-gpu") 
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_experimental_option('prefs', { 'profile.default_content_setting_values': { 'cookies' : 2, 'images': 2, 'plugins' : 2, 'popups': 2, 'geolocation': 2, 'notifications' : 2, 'auto_select_certificate': 2, 'fullscreen' : 2, 'mouselock' : 2, 'mixed_script': 2, 'media_stream' : 2, 'media_stream_mic' : 2, 'media_stream_camera': 2, 'protocol_handlers' : 2, 'ppapi_broker' : 2, 'automatic_downloads': 2, 'midi_sysex' : 2, 'push_messaging' : 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop' : 2, 'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement' : 2, 'durable_storage' : 2 } })
caps = DesiredCapabilities.CHROME
caps['pageLoadStrategy'] = 'none'

driver = webdriver.Chrome(options=options)
driver.maximize_window()

driver.get(LOGIN_URL)
driver.implicitly_wait(10)

driver.find_element(By.CLASS_NAME, 'c-button--openid--twitter').click()
driver.find_element(By.ID, 'username_or_email').send_keys(TWITTER_ID)
driver.find_element(By.ID, 'password').send_keys(TWITTER_PW)
driver.find_element(By.ID, 'allow').click()

driver.get(VS_URL)
driver.implicitly_wait(10)

for i in range(5):
    diffRadio = driver.find_elements(By.XPATH, '/html/body/div/div/div/div[1]/div[3]/div[2]/div[3]/form/div[2]/input') # difficulty radio button htmlElements
    diff = diffRadio[i] # radio button ( i_0 -> basic, i_1 -> advanced, i_2 -> expert, i_3 -> master, i_4 -> ultima )

    driver.execute_script("arguments[0].setAttribute('checked', 'checked');", diff) # difficulty button click

    diffValue = diff.get_attribute('id') # 'basic' | 'advanced' | 'expert' | 'master' | 'ultima'
    driver.find_element(By.CLASS_NAME, 'btn_battle').click() # battle button click

    genrelist = driver.find_elements(By.XPATH, '/html/body/div/div/div/div[1]/div[3]/div[2]/div[5]/*')[1:] # All song list with genre title
    
    namelist = flatten(getChartName(genrelist))
    scorelist = flatten(getChartScore(genrelist))
    mask = scorelist != '0'
    namelist = namelist[mask]
    scorelist = scorelist[mask]
    for songidx in range(len(chart['songs'])):
        cursong = chart['songs'][songidx]
        if cursong['category'] == "WORLD'S END":
            continue
        if cursong['title'] in namelist:
            curidx = int(np.where(namelist == cursong['title'])[0])
            name = str(namelist[curidx])
            score = str(scorelist[curidx])
            level = cursong['sheets'][i]['internalLevelValue']
            rating = calc_rating(int(score.replace(',', '')), cursong['sheets'][i]['internalLevelValue'])
            result.append({ 
                'name': name,
                'score': score,
                'diff': i,
                'diffValue': diffValue,
                'level': cursong['sheets'][i]['internalLevel'],
                'ratingVal': rating,
                'rating': f'{rating:.2f}',
                'image': IMAGE_DATA_FETCH_URL + cursong['imageName']
            })
result.sort(key=lambda x: -x['ratingVal'])
html_content = f'''
<head>
</head>
<body style="margin: 0;">
    <div class="background">
        <div class="titleContainer">TEST</div>
        <div class="ratingContainer">
            {'\n'.join(map(lambda x: f'''
            <div class="element">
                <img class="songImage" src="{x['image']}" style="box-shadow: 0 0 3px 2px {chart['difficulties'][x['diff']]['color']};"/>
                <div class="songInfoContainer">
                    <span class="songTitle">{x['name']}</span>
                    <span class="songTitle">{x['level']}</span>
                    <span class="songTitle">{x['score']} {Rank.from_score(int(x['score'].replace(',', '')))}</span>
                    <span class="songTitle">{x['rating']}</span>
                </div>
            </div>''', result[:30]))}
        </div>
    </div>
</body>'''

css_content = f'''
    * {{
        box-sizing: border-box;
    }}
    .background {{
        height: 100vh;
        aspect-ratio: 0.586;
        display: flex;
        align-items: center;
        flex-direction: column;
        flex-wrap: wrap;
        background-color: lightgreen;
    }}
    .titleContainer {{
        width: 100%;
        height: 10%;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 2.5rem;
    }}
    .ratingContainer {{
        width: 90%;
        height: 80%;
        background-color: yellow;
        display: flex;
        justify-content: space-evenly;
        align-items: center;
        flex-wrap: wrap;
    }}
    .element {{
        width: 30%;
        height: 8%;
        border: 1px solid black;
        padding: 10px;
        gap: 10px;
        display: flex;
        align-items: center;
    }}
    .songImage {{
        height: 90%;
        aspect-ratio: 1;
        left: 0;
    }}
    .songInfoContainer {{
        display: flex;
        flex-direction: column;;
    }}
    .songTitle {{
        font-size: 0.7rem;
    }}'''

hti = Html2Image()
hti.screenshot(html_str=html_content, css_str=css_content, save_as='output.png')
driver.quit()
