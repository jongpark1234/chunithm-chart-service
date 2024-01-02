from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.options import *
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from config import *
from fetchURL import *

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

Select(driver.find_element(By.NAME, 'level')).select_by_visible_text('LEVEL 15')
Select(driver.find_element(By.NAME, 'friend')).select_by_index(1)
driver.find_element(By.CLASS_NAME, 'btn_battle').click()
musiclist = driver.find_element(By.XPATH, '/html/body/div/div/div/div[1]/div[3]/div[2]/div[5]')
for music in musiclist.find_elements(By.XPATH, './*')[1:]:
    print(f'{music.find_element(By.XPATH, './div[1]/div[1]').text}: {music.find_element(By.XPATH, './div[2]/div[3]').text}')
driver.quit()

