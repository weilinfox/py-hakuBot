# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import requests, re
import hakuCore.cqhttpApi

url = 'https://www.baidu.com/s'
params = {
        'tn':'baidurt',
        'wd':'关键路径',
        'ie':'utf-8',
        'rn':2,
        'cl':3,
        'pn':1
    }
headers = {'User-Agent':'Mozilla/5.0 (X11; Linux mips64; rv:68.0) Gecko/20100101 Firefox/68.0'}

def main(msgDict):
    wd = list(msgDict['message'].split())
    if len(wd) == 1:
        return '小白会试着从百度搜索~'
    wd = list(msgDict['message'].split(' ', 1))[1].strip()
    # print(wd)
    params['wd'] = wd
    try:
        resp = requests.get(url=url, params=params, headers=headers)
    except:
        return '啊嘞嘞？一定是百度炸了不可能是小白！'
    if resp.status_code == 200:
        pageText = resp.text
        pageList = list(pageText.split('table', pageText.count('table')))
        for s in pageList:
            if 'class="result"' in s:
                res = re.findall(r'href="(.*?)"', s)[0].replace('<em>','').replace('</em>','')
                title = re.findall(r'>\s+(.*?)\s+</a>', s)[0].replace('<em>','').replace('</em>','')
                if res and title:
                    hakuCore.cqhttpApi.reply_msg(msgDict, f'[CQ:share,url={res},title={title}]')
    else:
        return '啊嘞嘞？一定是百度炸了不可能是小白！'
