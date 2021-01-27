# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import hakuData.method
import logging
import requests, json

#requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMPLEMENTOFDEFAULT"

myLogger = logging.getLogger('hakuBot')
GLOTKEY = hakuData.method.search_keys_dict('glot_key')

def glotLang():
    langList = requests.get(url='https://run.glot.io/languages').json()
    langDict = {}
    for dct in langList:
        langDict[dct['name']] = dct['url'] + '/latest'
    langDict['python2'] = 'https://run.glot.io/languages/python/2'
    return langDict


def main(msgDict):
    if GLOTKEY:
        msgList = list(msgDict['raw_message'].split())
        ans = ''
        LANG = ''
        if len(msgList) == 1:
            ans = 'Haku is rather serious when it comes to codes.\nRun "run <lang>" to verity if <lang> is supported.'
        elif len(msgList) == 2:
            lang = msgList[1].strip()
            try:
                LANG = glotLang()
            except:
                myLogger.exception('RuntimeError')
                ans = 'It seems that glot is temporary not achievable.'
            else:
                if LANG.get(lang):
                    ans = 'Haku have the capability to run ' + lang + '~'
                else:
                    ans = lang + 'は何か　知らない。'
        else:
            lang = msgList[1]
            pos = 0
            flag = 1
            spcont = 0
            space = [' ', '\n', '\t']
            for s in msgDict['raw_message'].strip():
                pos += 1
                if space.count(s):
                    if flag:
                        flag = 0
                        spcont += 1
                else:
                    if not flag: flag = 1
                if spcont == 2: break
            content = msgDict['raw_message'].strip()[pos:]
            
            try :
                LANG = glotLang()
            except:
                LANG = {}
                ans = 'It seems that glot is temporary not achievable.'
                myLogger.exception('RuntimeError')
            else:
                if not LANG.get(lang):
                    ans = lang + 'は何か　知らない。'

            if LANG.get(lang):
                try:
                    url = LANG[lang]
                    headers = {
                        'Authorization': 'Token ' + GLOTKEY,
                        'Content-type': 'application/json',
                    }
                    data = {
                        "files": [{
                            "name": 'hakuScript.' + lang,
                            "content": content
                        }]
                    }
                    resp = requests.post(url=url, headers=headers, json=data).json()
                    if len(resp['stdout']):
                        ans += 'stdout:\n' + resp['stdout']
                    if len(resp['stderr']):
                        if len(ans): ans += '\n'
                        ans += 'stderr:\n' + resp['stderr']
                    if len(resp['error']):
                        if len(ans): ans += '\n'
                        ans += 'error:\n' + resp['error']
                except:
                    myLogger.exception('RuntimeError')
                    ans = 'Error occurred while sending codes.'
    else:
        ans = '好像不给查诶...'

    return ans

    
#print(main({'raw_message':input()})) 
