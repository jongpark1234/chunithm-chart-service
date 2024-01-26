import * as config from './config'

export const AIME_URL = 'https://lng-tgk-aime-gw.am-all.net'
export const LOGIN_URL = 'https://lng-tgk-aime-gw.am-all.net/common_auth/login?site_id=chuniex&redirect_url=https://chunithm-net-eng.com/mobile/&back_url=https://chunithm.sega.com/'
    
export const CHUNITHM_MAIN_URL = 'https://chunithm-net-eng.com'
export const CHUNITHM_VS_URL = CHUNITHM_MAIN_URL + '/mobile/friend/genreVs'
export const CHUNITHM_VS_BATTLESTART_URL = CHUNITHM_VS_URL + '/battleStart'
    
export const LOGIN_FETCH_URL = 'https://lng-tgk-aime-gw.am-all.net/common_auth/login/sid/'
export const CHUNITHM_VS_FETCH_URL = 'https://chunithm-net-eng.com/mobile/friend/genreVs/sendBattleStart/'
    
export const CHART_DATA_FETCH_URL = 'https://dp4p6x0xfi5o9.cloudfront.net/chunithm/data.json'
export const IMAGE_DATA_FETCH_URL = 'https://dp4p6x0xfi5o9.cloudfront.net/chunithm/img/cover/'

export const LOGIN_PARAMS = {
    'retention': 1,
    'sid': config.SEGA_ID,
    'password': config.SEGA_PW
}
    
export const LOGIN_HEADERS = {
    'Host': AIME_URL.replace('https://', ''),
    'Origin': AIME_URL,
    'Referer': LOGIN_URL
}

export const VS_HEADERS = {
    'Host': CHUNITHM_MAIN_URL.replace('https://', ''),
    'Origin': CHUNITHM_MAIN_URL,
    'Referer': CHUNITHM_VS_BATTLESTART_URL,
}