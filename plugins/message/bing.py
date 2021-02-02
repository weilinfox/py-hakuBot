# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import requests, re
import hakuCore.cqhttpApi

#url = 'https://www.bing.com/search'
url = 'https://cn.bing.com/search'
params = {
        'q':'',
        #'mkt':'zh-CN',
        'qs':'n',
        'form':'QBRE',
        'sp':-1,
        'pq':'',
        'sc':'',
        'sk':'',
        'scope':'web'
    }
headers = {'User-Agent':'Mozilla/5.0 (X11; Linux mips64; rv:68.0) Gecko/20100101 Firefox/68.0'}

def main(msgDict):
    wd = list(msgDict['message'].split())
    if len(wd) == 1:
        return '小白会试着从bing搜索~'
    wd = list(msgDict['message'].split(' ', 1))[1].strip()
    #print(wd)
    params['q'] = wd.replace(' ', '+')
    try:
        resp = requests.get(url=url, params=params, headers=headers)
    except:
        return '啊嘞嘞？一定是bing炸了不可能是小白！'
    if resp.status_code == 200:
        try:
            resultPage = re.findall(r'<ol\s+id="b_results">(.*?)</ol>', resp.text)[0]
            resultList = re.findall(r'<li\s+class="b_algo">(.*?)</li>', resultPage)
        except:
            return '啊嘞嘞？好像啥也没有找到欸。'
        count = 0
        for s in resultList:
            try:
                res = re.findall(r'href="(.*?)"', s)[0]
                title = re.findall(r'<a target="_blank"(.*?)</a>', s)[0]
                title = re.findall(r'">(.*?)kk', title+'kk')[0].replace('<strong>','').replace('</strong>','')
            except:
                continue
            if res and title:
                count += 1
                #print(f'[CQ:share,url={res},title={title}]')
                hakuCore.cqhttpApi.reply_msg(msgDict, f'[CQ:share,url={res},title={title}]')
            if count == 2:
                break
        if count == 0:
            return '啊嘞嘞？好像啥也没有找到欸。'
    else:
        return '啊嘞嘞？一定是bing炸了不可能是小白！'

if __name__ == "__main__":
    msg = input('input msg: ')
    print(main({'message':msg}))
