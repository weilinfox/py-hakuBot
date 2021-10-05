# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import requests
import xml.dom.minidom
import hakuCore.cqhttpApi

#url = 'https://www.bing.com/search'
url = 'https://cn.bing.com/search'
params = {
        'format':'rss',
        'q':'',
    }
headers = {
    'User-Agent':'Mozilla/5.0 (X11; Linux mips64; rv:68.0) Gecko/20100101 Firefox/68.0',
    'Cookie': '_EDGE_V=1; MUID=; MUID=; SNRHOP=I=&TS=; SRCHD=AF=MOZLBR; _SS=PC=MOZI; SRCHS=PC=MOZI'
               }

def main(msgDict):
    wd = list(msgDict['message'].split())
    if len(wd) == 1:
        return '小白会试着从bing搜索~'
    wd = list(msgDict['message'].split(' ', 1))[1].strip()
    #print(wd)
    params['q'] = wd
    try:
        resp = requests.get(url=url, params=params, headers=headers, timeout=5)
    except:
        return '啊嘞嘞？一定是bing炸了不可能是小白！'
    if resp.status_code == 200:
        resultDoc = xml.dom.minidom.parseString(resp.text)
        itemCount = 0
        for item in resultDoc.getElementsByTagName('item'):
            titleEle = item.getElementsByTagName('title')[0]
            title = titleEle.childNodes[0].data
            linkEle = item.getElementsByTagName('link')[0]
            link = linkEle.childNodes[0].data
            descEle = item.getElementsByTagName('description')[0]
            desc = descEle.childNodes[0].data
            # print(title, link, desc)
            hakuCore.cqhttpApi.reply_msg(msgDict, f"[CQ:reply,id={msgDict['message_id']}][CQ:at,qq={msgDict['user_id']}]\n{desc}")
            hakuCore.cqhttpApi.reply_msg(msgDict, f"[CQ:share,url={link},title={title}]")
            itemCount += 1
            if itemCount == 2: break;
        if itemCount == 0:
            return '啊嘞嘞？好像啥也没有找到欸。'
    else:
        return '啊嘞嘞？一定是bing炸了不可能是小白！'

if __name__ == "__main__":
    msg = input('input msg: ')
    print(main({'message':'.bing '+msg}))
