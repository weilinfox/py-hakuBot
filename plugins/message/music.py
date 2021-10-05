# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import requests
import json, logging
import hakuCore.cqhttpApi as hakuApi

#HOST = 'inuyasha.love'
#PORT = 8001
URL = 'http://inuyasha.love:8001/search'
BACKURL = 'http://musicapi.leanapp.cn/search'

myLogger = logging.getLogger('hakuBot')

def main (msgDict):
    helpMsg = '小白会试着从网易云搜索~'
    req = list(msgDict['raw_message'].split(' ', 1))
    ans = ''
    if len(req) > 1:
        req[1] = req[1].strip()
    if len(req) > 1 and len(req[1]) > 0:
        try:
            resp = requests.get(url=URL, params={'keywords':req[1]}, timeout=5)
        except ConnectionError:
            try: 
                resp = requests.get(url=BACKURL, params={'keywords':req[1]}, timeout=5)
            except ConnectionError:
                ans = '啊嘞嘞好像出错了'
            except:
                myLogger.exception('RuntimeError')
                return '啊嘞嘞好像出错了'
        except:
            myLogger.exception('RuntimeError')
            return '啊嘞嘞好像出错了'
        if resp.status_code == 200:
            rejson = json.loads(resp.text)
            # print(resp.text)
            if rejson['result'].get('songs'):
                mscid = rejson['result']['songs'][0]['id']
                mscname = rejson['result']['songs'][0]['name']
                #ans = '[CQ:share,url=https://music.163.com/song/' + str(mscid) + '/,title=' + str(mscname) + ']'
                if msgDict['message_type'] == 'group':
                    hakuApi.send_group_share_music(msgDict['group_id'], '163', mscid)
                else:
                    hakuApi.send_private_share_music(msgDict['user_id'], '163', mscid)
            else:
                ans = '网易云里没有诶~'
        else:
            ans = '好像返回了奇怪的东西: ' + str(resp.status_code)
    else:
        ans = helpMsg

    return ans
