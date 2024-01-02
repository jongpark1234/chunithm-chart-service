from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.options import *
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from config import *
from fetchURL import *

def calc_rating():
    constant = 13.5
    score = 975000
    C = max((constant - 5) * 0.1 * ((min(score, 800000) - 500000) / 60000), 0)
    BBB = max((constant - 5) * 0.1 * ((min(score, 900000) - 800000) / 20000), 0)
    A = max(0.01 * (min(score, 925000) - 900000) / 125, 0)
    AA = max(0.03 * (min(score, 950000) - 925000) / 500, 0)
    AAA = max(0.03 * (min(score, 975000) - 950000) / 500, 0)
    S = max(0.01 * (min(score, 990000) - 975000) / 250, 0)
    SP = max(0.01 * (min(score, 1000000) - 990000) / 250, 0)
    SS = max(0.01 * (min(score, 1005000) - 1000000) / 100, 0)
    SSP = max(0.01 * (min(score, 1007500) - 1005000) / 50, 0)
    SSS = max(0.01 * (min(score, 1009000) - 1007500) / 100, 0)
    return sum(C, BBB, A, AA, AAA, S, SP, SS, SSP, SSS)

result = []

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument("window-size=1920x1080")
options.add_argument("disable-gpu") 
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_experimental_option('prefs', {'profile.default_content_setting_values': {'cookies' : 2, 'images': 2, 'plugins' : 2, 'popups': 2, 'geolocation': 2, 'notifications' : 2, 'auto_select_certificate': 2, 'fullscreen' : 2, 'mouselock' : 2, 'mixed_script': 2, 'media_stream' : 2, 'media_stream_mic' : 2, 'media_stream_camera': 2, 'protocol_handlers' : 2, 'ppapi_broker' : 2, 'automatic_downloads': 2, 'midi_sysex' : 2, 'push_messaging' : 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop' : 2, 'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement' : 2, 'durable_storage' : 2}})
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
    diffValue = diff.get_attribute('id')
    driver.find_element(By.CLASS_NAME, 'btn_battle').click()
    genrelist = driver.find_elements(By.XPATH, '/html/body/div/div/div/div[1]/div[3]/div[2]/div[5]/*')[1:]
    for genre in genrelist:
        musiclist = genre.find_elements(By.XPATH, './*')[1:]
        for music in musiclist:
            name = music.find_element(By.XPATH, './div[1]/div[1]').text
            score = music.find_element(By.XPATH, './div[2]/div[3]/div[1]').text
            if score != '0':
                result.append({
                    'name': name,
                    'diff': diffValue,
                    'score': score
                })
with open('userplaydata.out', 'w', encoding='utf-8') as f:
    f.write(str(result))
driver.quit()

