from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.options import *
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import re
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

def parseChartData(obj) -> list:
    return list(map(lambda x: re.split(r'([^.*]+\\n[^\\n]*?){4}', x), obj))



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
    diffRadio = driver.find_elements(By.XPATH, '/html/body/div/div/div/div[1]/div[3]/div[2]/div[3]/form/div[2]/input')
    diff = diffRadio[i]

    driver.execute_script("arguments[0].setAttribute('checked', 'checked');", diff)

    diffValue = diff.get_attribute('id') # 'basic' | 'advanced' | 'expert' | 'master' | 'ultima'
    driver.find_element(By.CLASS_NAME, 'btn_battle').click()

    genrelist = driver.find_elements(By.XPATH, '/html/body/div/div/div/div[1]/div[3]/div[2]/div[5]/*')[1:]
    print(parseChartData(map(lambda x: x.text, genrelist)))
    # for genre in genrelist:

    #     musiclist = genre.find_elements(By.XPATH, './*')[1:]
    #     for music in musiclist:
    #         name = music.find_element(By.XPATH, './div[1]/div[1]').text
    #         score = music.find_element(By.XPATH, './div[2]/div[3]/div[1]').text
    #         if score != '0':
    #             result.append({
    #                 'name': name,
    #                 'diff': diffValue,
    #                 'score': score
    #             })
with open('userplaydata.out', 'w', encoding='utf-8') as f:
    f.write(str(result))
driver.quit()

