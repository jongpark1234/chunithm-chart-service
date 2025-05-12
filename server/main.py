import os
import json
import numpy as np
import requests
from selenium import webdriver

import imgkit

from bs4 import BeautifulSoup
from bs4.element import Tag

from decimal import Decimal
from typing import List

from enums import Rank
from config import *
from fetchURL import *
import sourcetypes


CURRENT_VERSION = 'VERSE'


def urlParse(filename: str) -> str:
    return os.path.dirname(os.path.realpath(__file__)) + '\\' + filename

def parseWebelement(diff: int, namelist: list[str], scorelist: list[str], comboStatuslist: list[Tag]):
    for song in chart['songs']:
        if song['category'] == "WORLD'S END": # skip WORLD'S END
            continue
        if song['title'] in namelist:
            curidx = namelist.index(song['title'])
            
            name = str(namelist[curidx]) # 이름 ( str )
            score = str(scorelist[curidx]) # 점수 ( str )
            scoreValue = int(score.replace(',', '')) # 점수 ( int )
            diffValue = ['basic', 'advanced', 'expert', 'master', 'ultima'][diff] # 난이도 ( str )
            level = song['sheets'][diff]['internalLevel'] # 레벨 ( str )
            levelValue = song['sheets'][diff]['internalLevelValue'] # 레벨 ( float )
            ratingValue = calc_rating(scoreValue, levelValue) # 레이팅 ( Decimal )
            rating = f'{int(ratingValue * 100) / 100:.2f}' # 레이팅 ( str )
            image = IMAGE_DATA_FETCH_URL + song['imageName'] # 커버 이미지 ( str )

            comboStatusElement = comboStatuslist[curidx].find('img')
            comboStatus = (1 if comboStatusElement.attrs['src'].split('/')[-1] == 'icon_fullcombo.png' else 2) if comboStatusElement else 0

            # 현재 곡의 버전이 최신 버전인 경우 신곡 차트로 반영
            if song['version'] == CURRENT_VERSION:
                new_result.append({
                    'name': name,
                    'score': score,
                    'scoreValue': scoreValue,
                    'diff': diff,
                    'diffValue': diffValue,
                    'level': level,
                    'levelValue': levelValue,
                    'rating': rating,
                    'ratingValue': ratingValue,
                    'comboStatus': comboStatus,
                    'image': image
                })
            
            # 아닐 경우 구곡 차트로 반영
            else:
                old_result.append({
                    'name': name,
                    'score': score,
                    'scoreValue': scoreValue,
                    'diff': diff,
                    'diffValue': diffValue,
                    'level': level,
                    'levelValue': levelValue,
                    'rating': rating,
                    'ratingValue': ratingValue,
                    'comboStatus': comboStatus,
                    'image': image
                })


def calc_rating(score: int, internal_level: float) -> Decimal:
    baselvl = Decimal(str(internal_level or 0)) * 10_000
    rating = Decimal(0)

    if score >= Rank.border(Rank.SSSp):
        rating = baselvl + 21_500

    elif score >= Rank.border(Rank.SSS):
        rating = baselvl + 20_000 + (score - Rank.border(Rank.SSS))

    elif score >= Rank.border(Rank.SSp):
        rating = baselvl + 15_000 + (score - Rank.border(Rank.SSp)) * 2

    elif score >= Rank.border(Rank.SS):
        rating = baselvl + 10_000 + (score - Rank.border(Rank.SS))

    elif score >= Rank.border(Rank.S):
        rating = baselvl + Decimal(score - Rank.border(Rank.S)) * 2 / 5

    elif score >= Rank.border(Rank.A):
        rating = baselvl - 50_000 + Decimal(score - Rank.border(Rank.A)) * 2 / 3

    elif score >= Rank.border(Rank.BBB):
        rating = (baselvl - 50_000) / 2 + ((score - Rank.border(Rank.BBB)) * ((baselvl - 50_000) / 2)) / 100_000

    elif score >= Rank.border(Rank.C):
        rating = (((baselvl - 50_000) / 2) * (score - Rank.border(Rank.C))) / 300_000

    if rating < 0 and internal_level is not None and internal_level > 0:
        rating = Decimal(0)

    return rating / 10_000


def getRankTextShadow(score: int) -> str:
    if Rank.from_score(score) == Rank.SSSp:
        bright = 0.4
        color = 'green'
        times = 3

    elif Rank.from_score(score) == Rank.SSS:
        bright = 0.3
        color = 'darkgoldenrod'
        times = 3

    elif Rank.from_score(score) == Rank.SSp:
        bright = 0.3
        color = 'rgb(255, 123, 0)'
        times = 3
        
    elif Rank.from_score(score) == Rank.SS:
        bright = 0.3
        color = 'rgb(255, 123, 0)'
        times = 3

    elif Rank.from_score(score) == Rank.Sp:
        bright = 0.2
        color = 'rgb(255, 123, 0)'
        times = 2

    elif Rank.from_score(score) == Rank.S:
        bright = 0.2
        color = 'rgb(255, 123, 0)'
        times = 2

    elif Rank.from_score(score) in [Rank.AAA, Rank.AA, Rank.A]:
        bright = 0.1
        color = 'firebrick'
        times = 2

    elif Rank.from_score(score) in [Rank.BBB, Rank.BB, Rank.B]:
        bright = 0.1
        color = 'turquoise'
        times = 2
        
    else:
        bright = 0.1
        color = 'darkgrey'
        times = 1
        
    return ', '.join(f'0 0 {bright}em {color}' for _ in range(times))

def songNameStyle(comboStatus: int) -> str:
    if comboStatus == 1: # Full Combo
        return 'style="background: linear-gradient(to top, #FCF6D1 0%, #BD9457 5%, #FFF2DB 80%, #EAC885 90%, #FBF5D1 97%, #ECD8A3 100%); background-clip: text; -webkit-background-clip: text; color: transparent; text-shadow: #FC0 0 0 0.4rem;"'
    elif comboStatus == 2: # All Justice
        return 'style="background: linear-gradient(to top, #d1fcf8 0%, #57bdb8 5%, #ffdbfd 80%, #e285ea 90%, #f7d1fb 97%, #e3a3ec 100%); background-clip: text; -webkit-background-clip: text; color: transparent; text-shadow: 0 0 0.7rem rgb(240, 166, 255);"'
    else:
        return ''

def playerProfileStyle(possession: str) -> str:
    if possession == 'profile_silver': # silver
        return 'style="background: linear-gradient(45deg, #509CD3 20%, #92C7EE 36%, #509CD3 52%, #6BBBF4 68%, #469EDD 84%, #6BBBF4 100%)"'
    
    elif possession == 'profile_gold': # gold
        return 'style="background: linear-gradient(45deg, #CACD2A 20%, #FEFFC0 36%, #CACD2A 52%, #E4E582 68%, #CACD2A 84%, #E4E759 100%)"'
    
    elif possession == 'profile_platina': # platina
        return 'style="background: linear-gradient(45deg, #EAD66F 20%, #FFF9C5 36%, #ECDF69 52%, #F2EBAC 68%, #F2DF77 84%, #F4DC85 100%)"'
    
    elif possession == 'profile_rainbow': # rainbow
        return 'style="background: linear-gradient(45deg, #F4DCFF 20%, #FFF9C5 36%, #EECAFF 52%, #C96DF4 68%, #77F2EB 84%, #41FF3E 100%)"'
    
    else: # normal
        return 'style="background: #d9d9d9"'


def replaceAlphabet(string: str) -> str:
    for i in 'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ０１２３４５６７８９':
        string = string.replace(i, chr(ord(i) - 65248))
    return string

def isExistFriend(serial_code: str) -> bool:
    with requests.Session() as session:
        session.get(LOGIN_URL)
        login_response = session.post(url=LOGIN_FETCH_URL, headers=LOGIN_HEADERS, params=LOGIN_PARAMS, allow_redirects=False)
        session.get(login_response.headers['Location'])

        friend = session.get('https://chunithm-net-eng.com/mobile/friend/')
        friend_soup = BeautifulSoup(friend.text, 'html.parser')
        friend_block = friend_soup.find('input', { 'value': serial_code })
        
        return bool(friend_block)
    
def sendFriendInvite(friend_code: str) -> int:
    with requests.Session() as session:
        session.get(LOGIN_URL)
        login_response = session.post(url=LOGIN_FETCH_URL, headers=LOGIN_HEADERS, params=LOGIN_PARAMS, allow_redirects=False)
        AUTH_TOKEN = session.get(login_response.headers['Location']).cookies['_t']
        send_invite = session.post('https://chunithm-net-eng.com/mobile/friend/search/sendInvite/', data={
            'idx': friend_code,
            'token': AUTH_TOKEN
        })
        return send_invite.status_code


old_result = []
new_result = []
chart = json.load(open(urlParse('chart.json'), 'r', encoding='utf-8'))

LOGIN_PARAMS = {
    'retention': 1,
    'sid': SEGA_ID,
    'password': SEGA_PW
}

LOGIN_HEADERS = {
    'Host': AIME_URL.replace('https://', ''),
    'Origin': AIME_URL,
    'Referer': LOGIN_URL
}

VS_HEADERS = {
    'Host': CHUNITHM_MAIN_URL.replace('https://', ''),
    'Origin': CHUNITHM_MAIN_URL,
    'Referer': CHUNITHM_FRIEND_VS_BATTLESTART_URL,
}
if __name__ == '__main__':

    with requests.Session() as session:

        print('Accessing To CNBot Account...')
        session.get(LOGIN_URL)

        login_response = session.post(
            url=LOGIN_FETCH_URL,
            headers=LOGIN_HEADERS,
            params=LOGIN_PARAMS,
            allow_redirects=False
        )

        AUTH_TOKEN = session.get(login_response.headers['Location']).cookies['_t']


        TARGET_FRIENDCODE = 8038648670957
        
        friend = session.get('https://chunithm-net-eng.com/mobile/friend/')
        friend_soup = BeautifulSoup(friend.text, 'html.parser')
        friend_block = friend_soup.find('input', { 'value': f'{TARGET_FRIENDCODE}' }).find_parent('div', 'friend_block')

        friend_player_chara = friend_block.find('div', 'player_chara')

        friend_style_charaFrame = friend_player_chara.attrs['style']
        friend_src_character = friend_player_chara.find('img').attrs['src']
        friend_style_honor = friend_block.find('div', 'player_honor_short').attrs['style']

        friend_src_classemblem_base = friend_block.find('div', 'player_classemblem_base')
        if friend_src_classemblem_base:
            friend_src_classemblem_base = friend_src_classemblem_base.find('img').attrs['src']
        else:
            friend_src_classemblem_base = ''

        friend_src_classemblem_medal = friend_block.find('div', 'player_classemblem_top')
        if friend_src_classemblem_medal:
            friend_src_classemblem_medal = friend_src_classemblem_medal.find('img').attrs['src']
        else:
            friend_src_classemblem_medal = ''

        friend_src_player_reborn = friend_block.find('div', 'player_reborn')
        if friend_src_player_reborn:
            friend_src_player_reborn = int(friend_src_player_reborn.text.strip())
        else:
            friend_src_player_reborn = 0

        friend_team = friend_block.find('div', 'player_team_name')
        if friend_team:
            friend_team = friend_team.text.strip()
        else:
            friend_team = ''

        friend_honor_text = friend_block.find('div', 'player_honor_text')
        if friend_honor_text:
            friend_honor_text = friend_honor_text.text
        else:
            friend_honor_text = ''

        friend_name = friend_block.find('div', 'player_name_in').text.strip()
        friend_lv = friend_src_player_reborn * 100 + int(friend_block.find("div", 'player_lv').text.strip())
        friend_rating = Decimal(''.join(map(lambda x: x.attrs['src'][-5], friend_block.find('div', 'player_rating_num_block').find_all('img'))).replace('a', '.'))
        friend_overpower = friend_block.find('div', 'player_overpower').text.strip()
        friend_overpower_const = Decimal(friend_overpower.split()[0])
        friend_overpower_percent = Decimal(friend_overpower.split()[1][1:-2])
        friend_possession = friend_block.find('div', 'box_playerprofile .clearfix').attrs['style'].split('/')[-1].split('.')[0]
        
        for diff in range(5):
            print(f'Fetching {chart["difficulties"][diff]["name"]} Data...')
            vs_result = session.post(
                url=CHUNITHM_FRIEND_VS_FETCH_URL,
                headers=VS_HEADERS,
                data={
                    'genre': 99,
                    'friend': TARGET_FRIENDCODE,
                    'radio_diff': diff,
                    'loseOnly': 'on',
                    'token': AUTH_TOKEN
                }
            )

            soup = BeautifulSoup(vs_result.text, 'html.parser')
            namelist = list(map(lambda x: x.text, soup.find_all(attrs={ 'class': 'block_underline text_b text_c' })))
            scorelist = list(map(lambda x: x.text, soup.find_all(attrs={ 'class': 'play_musicdata_highscore' })))[1::2]
            comboStatuslist = list(soup.find_all(attrs={ 'class': 'vs_list_friendbatch clearfix' }))
            parseWebelement(diff, namelist, scorelist, comboStatuslist)

    old_result.sort(key=lambda x: (-x['ratingValue'], -x['scoreValue']))
    old_result = old_result[:30]
    
    new_result.sort(key=lambda x: (-x['ratingValue'], -x['scoreValue']))
    new_result = new_result[:20]
    bn = '\n'

    old_rating = round(sum(map(lambda x: x['ratingValue'], old_result)) / len(old_result), 2)
    new_rating = round(sum(map(lambda x: x['ratingValue'], new_result)) / len(new_result), 2)

    style_head = open(urlParse('styleHead.html'), encoding='utf-8').read()
    html_content: sourcetypes.xml = f"""<body>
        <div class="background">

            <div class="titleContainer">

                <div class="leftInfoContainer" {playerProfileStyle(friend_possession)}>
                    <div class="charaContainer">
                        <div class="charaFrame" style="{friend_style_charaFrame}">
                            <img class="charaImage" src="{friend_src_character}"/>
                        </div>
                    </div>
                    <div class="profileContainer">
                        <div class="teamBg" style="background-image: url(https://chunithm-net-eng.com/mobile/images/team_bg_rainbow.png);">
                            <span class="teamText">{replaceAlphabet(friend_team)}</span>
                        </div>
                        <div class="honor" style="{friend_style_honor}">
                            <span class="honorText">{friend_honor_text}</span>
                        </div>
                        <div class="rowContainer" style="justify-content: space-around;">
                            <span class="profileBoldText">LV. {friend_lv}</span>
                            <span class="profileBoldText">{replaceAlphabet(friend_name)}</span>
                        </div>
                        <div class="rowContainer" style="position: relative; height: 200px;">
                            {f'<img class="profileClassEmblem" style="position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%);" src="{friend_src_classemblem_base}">' if friend_src_classemblem_base else ''}
                            {f'<img class="profileClassEmblem" style="position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%);" src="{friend_src_classemblem_medal}">' if friend_src_classemblem_medal else ''}
                        </div>
                    </div>
                </div>

                <div class="rightInfoContainer" {playerProfileStyle(friend_possession)}>
                    <div class="infoTitleContainer">
                        <span class="infoTitleText">RATING</span>
                        <span class="infoTitleText">OLD RATING</span>
                        <span class="infoTitleText">NEW RATING</span>
                        <span class="infoTitleText">OVERPOWER</span>
                    </div>
                    <div class="infoDataContainer">
                        <span class="infoDataText">{friend_rating}</span>
                        <span class="infoDataText">{old_rating}</span>
                        <span class="infoDataText">{new_rating}</span>
                        <div class="overpowerGauge">
                            <div class="overpowerGaugeBlock" style="width: {100 - friend_overpower_percent}%"></div>
                        </div>
                    </div>
                </div>

            </div>

            <div class="ratingContainer">

                {bn.join(map(lambda song: f'''
                    <div class="element">
                        <div class="elementOrder"># {song[0] + 1}</div>
                        <div class="elementWrapper">
                            <img class="songImage" src="{song[1]['image']}" style="box-shadow: 0 0 3px 3px {chart['difficulties'][song[1]['diff']]['color']};"/>
                            <div class="songInfoContainer">
                                <span class="songTitle" {songNameStyle(song[1]['comboStatus'])}>{song[1]['name']}</span>
                                <div class="columnContainer">
                                    <div class="textRowContainer">
                                        <span class="songDetailKey">CONST -</span>
                                        <div class="textRowContainer">    
                                            <span class="songText">&nbsp;{song[1]['level'].split('.')[0]}.</span>
                                            <span class="songRatingDetail">{song[1]['level'].split('.')[1]}</span>
                                        </div>
                                    </div>
                                    <div class="textRowContainer">
                                        <span class="songDetailKey" style="letter-spacing: 0.018rem;">SCORE -</span>
                                        <span class="songText">&nbsp;{song[1]['score']}</span>
                                    </div>
                                </div>
                                <div class="rowContainer">
                                    <div class="textRowContainer">
                                        <span class="songRating">↪ {song[1]['rating'].split('.')[0]}.</span>
                                        <span class="songRatingDetail">{song[1]['rating'].split('.')[1]}</span>
                                    </div>
                                    <span class="songRank" style="text-shadow: {getRankTextShadow(song[1]['scoreValue'])};">{Rank.from_score(song[1]['scoreValue'])}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                ''', enumerate(old_result)))}

            </div>

            <div class="ratingContainer">

                {bn.join(map(lambda song: f'''
                    <div class="element">
                        <div class="newElementOrder"># {song[0] + 1}</div>
                        <div class="elementWrapper">
                            <img class="songImage" src="{song[1]['image']}" style="box-shadow: 0 0 3px 3px {chart['difficulties'][song[1]['diff']]['color']};"/>
                            <div class="songInfoContainer">
                                <span class="songTitle" {songNameStyle(song[1]['comboStatus'])}>{song[1]['name']}</span>
                                <div class="columnContainer">
                                    <div class="textRowContainer">
                                        <span class="songDetailKey">CONST -</span>
                                        <div class="textRowContainer">    
                                            <span class="songText">&nbsp;{song[1]['level'].split('.')[0]}.</span>
                                            <span class="songRatingDetail">{song[1]['level'].split('.')[1]}</span>
                                        </div>
                                    </div>
                                    <div class="textRowContainer">
                                        <span class="songDetailKey" style="letter-spacing: 0.018rem;">SCORE -</span>
                                        <span class="songText">&nbsp;{song[1]['score']}</span>
                                    </div>
                                </div>
                                <div class="rowContainer">
                                    <div class="textRowContainer">
                                        <span class="songRating">↪ {song[1]['rating'].split('.')[0]}.</span>
                                        <span class="songRatingDetail">{song[1]['rating'].split('.')[1]}</span>
                                    </div>
                                    <span class="songRank" style="text-shadow: {getRankTextShadow(song[1]['scoreValue'])};">{Rank.from_score(song[1]['scoreValue'])}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                ''', enumerate(new_result)))}

            </div>

        </div>
    </body>"""

    
    open(urlParse('output.html'), 'w', encoding='utf-8').write(style_head + html_content)
    options = webdriver.ChromeOptions()
    options.add_argument('window-size=2400x2400')
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)
    driver.get(urlParse('output.html'))
    element = driver.find_element('class name', 'background')
    with open('output.png', 'wb') as file:
        file.write(element.screenshot_as_png)
