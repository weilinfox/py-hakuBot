# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import requests
import time
import re
import logging
import hakuData.method as method
import hakuCore.cqhttpApi as api

"""
龙芯开源社区新闻订阅
"""

mylogger = logging.getLogger('hakuBot')

starttime = time.gmtime(time.time() + 8 * 3600)
lastday = [starttime.tm_year, starttime.tm_mon, starttime.tm_mday]

subset = set()
database = method.sqlite_get_name('message', 'loongnews')

mydb = method.sqlite_db_open(database)
cursor = mydb.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS ids(id Long);')
cursor.execute('CREATE TABLE IF NOT EXISTS news(content Text);')
ids = cursor.execute('SELECT id FROM ids;')
ids = ids.fetchall()
for id in ids:
    subset.add(id[0])
cursor.close()
method.sqlite_db_close(mydb)


def get_page(url):
    try:
        res = requests.get(url=url, timeout=5)
    except Exception as e:
        pass
    else:
        if res.status_code == 200:
            return res.text
    return ''


def loongnix_cn_news():
    """
    获取 loongnix.cn 产品新闻和社区新闻
    """
    baseurl = 'http://www.loongnix.cn'
    indexurl = '/index.php/%E9%A6%96%E9%A1%B5'
    suburls = {
        #'product': '/index.php/%E4%BA%A7%E5%93%81%E6%96%B0%E9%97%BB',
        #'community': '/index.php/%E7%A4%BE%E5%8C%BA%E6%96%B0%E9%97%BB',
        'loongnix': '/index.php/Loongnix',
        'java': '/index.php/Java',
    }

    news = []
    context = get_page(baseurl+indexurl)
    hits = list(re.findall(r'<li>.*?</li>', context, flags=re.DOTALL))
    for url in suburls.values():
        context = get_page(baseurl+url)
        for h in re.findall(r'<li>.*?</li>', context, flags=re.DOTALL):
            hits.append(h)
    for s in hits:
        msgs = re.findall(r'\[(\d+)[/|-](\d+)[/|-](\d+)\](.*?)</li>', s, flags=re.DOTALL)
        for h in msgs:
            if len(h) == 4:
                yy = int(h[0])
                mm = int(h[1])
                dd = int(h[2])
                if yy != lastday[0] or mm != lastday[1] or dd != lastday[2]:
                    continue
                msg = f'[{h[0]}/{h[1]}/{h[2]}] ' + re.sub(r'<(.*?)>', '', h[3]).strip()
                links = re.findall(r'href="(.*?)"', h[3], flags=0)
                # print(h)
                for l in links:
                    if len(l) > 1 and l[0] == '/':
                        msg += f'\n{baseurl}{l}'
                    else:
                        msg += f'\n{l}'
                news.append(msg)
    return news


def main(msgdict):
    global subset, lastday

    comm = msgdict['raw_message'].split()
    if msgdict['message_type'] == 'private':
        uid = msgdict['user_id']
    elif msgdict['message_type'] == 'group':
        uid = -msgdict['group_id']
    else:
        timenow = time.gmtime(time.time() + 8 * 3600)
        if timenow.tm_year != lastday[0] or timenow.tm_mon != lastday[1] or timenow.tm_mday != lastday[2]:
            db = method.sqlite_db_open(database)
            cursor = db.cursor()
            cursor.execute('DELETE FROM news;')
            cursor.close()
            method.sqlite_db_close(db)
            lastday = [timenow.tm_year, timenow.tm_mon, timenow.tm_mday]
        newss = loongnix_cn_news()
        ans = '龙芯开源社区新闻：'
        postnews = []
        db = method.sqlite_db_open(database)
        cursor = db.cursor()
        for s in newss:
            cursor.execute('SELECT content FROM news WHERE content=?;', (s, ))
            if len(cursor.fetchall()) == 0:
                postnews.append(s)
                cursor.execute('INSERT INTO news(content) values(?)', (s, ))
        cursor.close()
        method.sqlite_db_close(db)
        # print(postnews)
        if len(postnews) > 0:
            for i in range(len(postnews)):
                ans += f'\n{i}. {postnews[i]}'
            # print(ans)
            for id in subset:
                if id > 0:
                    api.send_private_msg(id, ans)
                else:
                    api.send_group_msg(-id, ans)
        return
    status = uid in subset
    ans = """龙芯开源社区新闻：
sub 订阅
unsub 取消订阅"""
    if status:
        ans += '\n汝已订阅'
    else:
        ans += '\n汝未订阅'
    if len(comm) > 1 and comm[1] in ['sub', 'unsub']:
        db = method.sqlite_db_open(database)
        cursor = db.cursor()
        if comm[1] == 'sub' and not status:
            subset.add(uid)
            cursor.execute('INSERT INTO ids(id) values(?)', (uid, ))
        elif comm[1] == 'unsub' and status:
            subset.remove(uid)
            cursor.execute('DELETE FROM ids WHERE id=?', (uid, ))
        cursor.close()
        method.sqlite_db_close(db)
        ans = '汝的操作成功执行'
    return ans


if __name__ == '__main__':
    print(loongnix_cn_news())
    print(main({'raw_message': 'news sub', 'message_type': 'group', 'group_id': 12}))
    print(main({'raw_message': 'news ', 'message_type': 'group', 'group_id': 12}))
    print(main({'raw_message': '', 'message_type': ''}))
    print(main({'raw_message': 'news unsub', 'message_type': 'group', 'group_id': 12}))

