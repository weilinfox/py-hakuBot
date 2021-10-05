# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import logging
import requests
import json

myLogger = logging.getLogger('hakuBot')

def main (msgDict):
    helpMsg = '今天小白不高兴[CQ:face,id=107]'
    req = list(msgDict['raw_message'].split(' ', 1))
    ans = ''
    if len(req) > 1:
        ans = helpMsg
    else:
        try:
            #resp = requests.get(url='https://v1.hitokoto.cn/',params={'c':'j'})
            resp = requests.get(url='http://api.heerdev.top:4995/nemusic/random', timeout=5)
            if resp.status_code == 200:
                rejson = json.loads(resp.text)
                # print(rejson)
                #ans = rejson['hitokoto']
                ans = rejson['text']
            else:
                ans = '好像返回了奇怪的东西: ' + str(resp.status_code)
        except:
            myLogger.exception('RuntimeError')
            ans = '啊嘞嘞好像出错了，一定是wyy炸了不关小白！'

    return ans
 
