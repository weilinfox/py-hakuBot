# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import requests
import re
import haku_core.api_cqhttp

url = 'https://www.baidu.com/s'
params = {
        'tn': 'baidurt',
        'wd': '关键路径',
        'ie': 'utf-8',
        'rn': 2,
        'cl': 3,
        'pn': 1
    }
headers = {'User-Agent':'Mozilla/5.0 (X11; Linux mips64; rv:68.0) Gecko/20100101 Firefox/68.0'}


def main(msgdict):
    wd = list(msgdict['message'].split())
    if len(wd) == 1:
        return '小白会试着从百度搜索~'
    wd = list(msgdict['message'].split(' ', 1))[1].strip()
    # print(wd)
    params['wd'] = wd
    try:
        resp = requests.get(url=url, params=params, headers=headers, timeout=5)
    except:
        return '啊嘞嘞？一定是百度炸了不可能是小白！'
    if resp.status_code == 200:
        page_text = resp.text
        page_list = list(page_text.split('table', page_text.count('table')))
        get_result = False
        for s in page_list:
            if 'class="result"' in s:
                res = re.findall(r'href="(.*?)"', s)[0]
                title = re.findall(r'>\s+(.*?)\s+</a>', s)[0].replace('<em>','').replace('</em>','')
                if res and title:
                    haku_core.api_cqhttp.reply_msg(msgdict, f'[CQ:share,url={res},title={title}]')
                    get_result = True
        if not get_result:
            return '啊嘞嘞？好像啥也没有找到欸。'
    else:
        return '啊嘞嘞？一定是百度炸了不可能是小白！'
