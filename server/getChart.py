from requests import get

from fetchURL import *

with open('server/chart.json', 'w', encoding='utf-8') as f:
    f.write(get(CHART_DATA_FETCH_URL).text)
