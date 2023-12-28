from requests import get

with open('chart.json', 'w', encoding='utf-8') as f:
    f.write(get('https://dp4p6x0xfi5o9.cloudfront.net/chunithm/data.json').text)
