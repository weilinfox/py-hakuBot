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
        helpMsg = '小白会试着搜索指定地区天气~\nforecast 城市 地区 n日后\n0>=n>=2'
        req = list(msgDict['raw_message'].split())
        for i in range(0, len(req)):
            req[i] = req[i].strip()
        url1 = 'https://geoapi.heweather.net/v2/city/lookup'
        url2 = 'https://devapi.heweather.net/v7/weather/3d'
        ans = ''
        params = {'key':KEY}
        days = 0
        try:
            days = int(req[3])
        except:
            days = 100

        if days >= 0 and days <= 2 and len(req) == 4:
            params.update({'location':req[2],'adm':req[1]})
            try:
                resp = requests.get(url=url1,params=params)
                if resp.status_code == 200:
                    rejson = json.loads(resp.text)
                    print(rejson)
                    cityId = rejson['location'][0]['id']
                    province = rejson['location'][0]['adm1']
                    city = rejson['location'][0]['adm2']
                    resp = requests.get(url=url2,params={'key':KEY,'location':cityId})
                    if resp.status_code == 200:
                        rejson = json.loads(resp.text)
                        print(rejson)
                        ans = province + '-' + city + ' ' + rejson['daily'][days]['textDay'] \
                                + '\n' + rejson['daily'][days]['fxDate'] \
                                + '\n气温:' + rejson['daily'][days]['tempMin'] + '-' + rejson['daily'][days]['tempMax'] + '℃' \
                                + '\n风向:' + rejson['daily'][days]['windDirDay'] + ' 风力:' + rejson['daily'][days]['windScaleDay'] + '级' \
                                + '\n风速:' + rejson['daily'][days]['windSpeedDay'] + 'km/h 气压:' + rejson['daily'][days]['pressure'] + 'hPa'
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
 
