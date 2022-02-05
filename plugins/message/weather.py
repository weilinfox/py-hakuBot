# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE
"""
和风天气查询 需要 key

语法：
weather 城市/地区
weather 城市 地区
"""

import haku_data.method
import requests
import json


HEKEY = haku_data.method.search_keys_dict('heweather')
params = {'key': HEKEY}
url1 = 'https://geoapi.heweather.net/v2/city/lookup'
url2 = 'https://devapi.heweather.net/v7/weather/now'


def send_request():
    ans = cityId = province = city = None
    trytime = 5
    while not cityId and trytime > 0:
        try:
            resp = requests.get(url=url1, params=params, timeout=5)
            if resp.status_code == 200:
                rejson = json.loads(resp.text)
                # print(rejson)
                if rejson['code'] == '200':
                    cityId = rejson['location'][0]['id']
                    province = rejson['location'][0]['adm1']
                    city = rejson['location'][0]['adm2']
                else:
                    ans = '真的有这个地方咩，别骗小白！'
            else:
                ans = '好像返回了奇怪的东西: ' + str(resp.status_code)
            break
        except Exception as e:
            trytime -= 1
    if trytime == 0:
        ans = '啊嘞嘞好像出错了，一定是和风炸了不关小白！'
    if cityId:
        trytime = 5
        while trytime > 0:
            try:
                resp = requests.get(url=url2, params={'key': HEKEY, 'location': cityId}, timeout=5)
                if resp.status_code == 200:
                    rejson = json.loads(resp.text)
                    # print(rejson)
                    ans = province + '-' + city + ' ' + rejson['now']['text'] \
                          + '\n气温:' + rejson['now']['temp'] + '℃ 体感:' + rejson['now']['feelsLike'] + '℃' \
                          + '\n风向:' + rejson['now']['windDir'] + ' 风力:' + rejson['now']['windScale'] + '级' \
                          + '\n风速:' + rejson['now']['windSpeed'] + 'km/h 气压:' + rejson['now']['pressure'] + 'hPa'
                else:
                    ans = '好像返回了奇怪的东西: ' + str(resp.status_code)
                break
            except Exception as e:
                trytime -= 1
        if trytime == 0:
            ans = '啊嘞嘞好像出错了，一定是和风炸了不关小白！'
    return ans


def main(msgDict):
    if HEKEY:
        ans = '小白会试着搜索指定地区天气~\nweather 城市/地区\nweather 城市 地区'
        req = list(msgDict['raw_message'].split())
        for i in range(0, len(req)):
            req[i] = req[i].strip()

        if len(req) == 2:
            params.update({'location': req[1]})
        elif len(req) > 2:
            params.update({'location': req[2], 'adm': req[1]})
        if len(req) > 1:
            ans = send_request()
    else:
        ans = '好像和风不让查诶...'

    return ans
