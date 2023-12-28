from selenium import common, types, webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.options import *
from selenium.webdriver.support.ui import Select

from config import *

driver = webdriver.Chrome()
options = webdriver.ChromeOptions()
options.add_argument('headless')


driver.get(LOGIN_URL)
driver.find_element(By.CLASS_NAME, 'c-button--openid--twitter').click()
driver.find_element(By.ID, 'username_or_email').send_keys(TWITTER_ID)
driver.find_element(By.ID, 'password').send_keys(TWITTER_PW)
driver.find_element(By.ID, 'allow').click()
driver.get('https://chunithm-net-eng.com/mobile/friend/levelVs')
Select(driver.find_element(By.NAME, 'level')).select_by_visible_text('LEVEL 15')
Select(driver.find_element(By.NAME, 'friend')).select_by_index(1)
driver.find_element(By.CLASS_NAME, 'btn_battle').click()
musiclist = driver.find_element(By.XPATH, '/html/body/div/div/div/div[1]/div[3]/div[2]/div[5]')
for music in musiclist.find_elements(By.XPATH, './*')[1:]:
    print(f'{music.find_element(By.XPATH, './div[1]/div[1]').text}: {music.find_element(By.XPATH, './div[2]/div[3]').text}')
driver.quit()

