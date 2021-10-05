# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import hakuData.method
import logging
import requests
import json

myLogger = logging.getLogger('hakuBot')
HEKEY = hakuData.method.search_keys_dict('heweather')

def main (msgDict):
    KEY = HEKEY #和风天气key
    if KEY:
        helpMsg = '小白会试着搜索指定地区天气~\nweather 城市/地区\nweather 城市 地区'
        req = list(msgDict['raw_message'].split())
        for i in range(0, len(req)):
            req[i] = req[i].strip()
        url1 = 'https://geoapi.heweather.net/v2/city/lookup'
        url2 = 'https://devapi.heweather.net/v7/weather/now'
        ans = ''
        params = {'key':KEY}

        if len(req) == 2:
            params.update({'location':req[1]})
        elif len(req) > 2:
            params.update({'location':req[2],'adm':req[1]})

        if len(req) > 1:
            try:
                resp = requests.get(url=url1,params=params, timeout=5)
                if resp.status_code == 200:
                    rejson = json.loads(resp.text)
                    #print(rejson)
                    cityId = rejson['location'][0]['id']
                    province = rejson['location'][0]['adm1']
                    city = rejson['location'][0]['adm2']
                    resp = requests.get(url=url2,params={'key':KEY,'location':cityId}, timeout=5)
                    if resp.status_code == 200:
                        rejson = json.loads(resp.text)
                        #print(rejson)
                        ans = province + '-' + city + ' ' + rejson['now']['text'] \
                                + '\n气温:' + rejson['now']['temp'] + '℃ 体感:' + rejson['now']['feelsLike'] + '℃' \
                                + '\n风向:' + rejson['now']['windDir'] + ' 风力:' + rejson['now']['windScale'] + '级' \
                                + '\n风速:' + rejson['now']['windSpeed'] + 'km/h 气压:' + rejson['now']['pressure'] + 'hPa'
                    else:
                        ans = '好像返回了奇怪的东西: ' + str(resp.status_code)
                elif resp.status_code == 404:
                    ans = '真的有这个地方咩，别骗小白！'
                else:
                    ans = '好像返回了奇怪的东西: ' + str(resp.status_code)
            except:
                myLogger.exception('RuntimeError')
                ans = '啊嘞嘞好像出错了，一定是和风炸了不关小白！'
        else:
            ans = helpMsg
    else:
        ans = '好像和风不让查诶...'

    return ans
 
