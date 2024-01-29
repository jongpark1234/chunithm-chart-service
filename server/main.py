import json
import numpy as np
import requests

from bs4 import BeautifulSoup
from decimal import Decimal
from typing import List

from enums import Rank
from config import *
from fetchURL import *

    
def parseWebelement(diff: int, namelist: list[str], scorelist: list[str]):
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
            ratingValue = calc_rating(scoreValue, level) # 레이팅 ( Decimal )
            rating = f'{int(ratingValue * 100) / 100:.2f}' # 레이팅 ( str )
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

    elif Rank.from_score(score) == Rank.SSS:
        bright = 0.3
        color = 'darkgoldenrod'

    elif Rank.from_score(score) == Rank.SSp:
        bright = 0.2
        color = 'goldenrod'
        
    elif Rank.from_score(score) == Rank.SS:
        bright = 0.2
        color = 'goldenrod'

    elif Rank.from_score(score) == Rank.Sp:
        bright = 0.1
        color = 'gold'

    elif Rank.from_score(score) == Rank.S:
        bright = 0.1
        color = 'gold'

    elif Rank.from_score(score) in [Rank.AAA, Rank.AA, Rank.A]:
        bright = 0.1
        color = 'orange'

    elif Rank.from_score(score) in [Rank.BBB, Rank.BB, Rank.B]:
        bright = 0.1
        color = 'turquoise'
        
    else:
        bright = 0.1
        color = 'darkgrey'
        
    return ', '.join(f'0 0 {bright}em {color}' for _ in range(3))



result = []
chart = json.load(open('chart.json', 'r', encoding='utf-8'))

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
    'Referer': CHUNITHM_VS_BATTLESTART_URL,
}

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
    
    friend = session.get('https://chunithm-net-eng.com/mobile/friend/')
    friend_soup = BeautifulSoup(friend.text, 'html.parser')
    friend_block = friend_soup.find('input', { 'value': '8038648670957' }).find_parent('div', { 'class': 'friend_block' })

    for diff in range(5):
        print(f'Fetching {chart["difficulties"][diff]["name"]} Data...')
        vs_result = session.post(
            url=CHUNITHM_VS_FETCH_URL,
            headers=VS_HEADERS,
            data={
                'genre': 99,
                'friend': 8038648670957,
                'radio_diff': diff,
                'loseOnly': 'on',
                'token': AUTH_TOKEN
            }
        )

        soup = BeautifulSoup(vs_result.text, 'html.parser')
        namelist = list(map(lambda x: x.text, soup.find_all(attrs={ 'class': 'block_underline text_b text_c' })))
        scorelist = list(map(lambda x: x.text, soup.find_all(attrs={ 'class': 'play_musicdata_highscore' })))[1::2]

        parseWebelement(diff, namelist, scorelist)

result.sort(key=lambda x: -x['ratingValue'])

bn = '\n'
html_content = open('styleHead.html', encoding='utf-8').read() + f"""<body>
    <div class="background">
        <div class="titleContainer">
            <div class="infoContainer"></div>
            <div class="infoContainer"></div>
        </div>
        <div class="ratingContainer">
            {bn.join(map(lambda song: f'''<div class="element">
        <div class="elementOrder"># {song[0] + 1}</div>
        <img class="songImage" src="{song[1]['image']}" style="box-shadow: 0 0 3px 1px {chart['difficulties'][song[1]['diff']]['color']};"/>
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
''', enumerate(result[:30])))}
        </div>
    </div>
</body>"""

open('output.html', 'w', encoding='utf-8').write(html_content)