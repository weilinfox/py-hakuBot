# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

"""
Debian 包查询
"""

import requests
import re


def search_debian(keywords):
    baseurl = 'https://packages.debian.org'
    searchurl = '/search'
    params = {
        'suite': 'all',
        'section': 'all',
        'arch': 'any',
        'searchon': 'names',
        'keywords': keywords,
    }

    try:
        res = requests.get(url=baseurl+searchurl, params=params, timeout=20)
    except requests.exceptions.ReadTimeout:
        return 'Search timeout.'

    if res.status_code == 200:
        restexts = res.text.split()
        restext = ''
        for s in restexts:
            restext += ' ' + s

        searchRes = {
            'package': '',
            'links': [],
        }

        hits = re.findall(r'<h3>.*?</ul>', restext, flags=0)
        if len(hits) > 0:
            hits = hits[0]
            name = re.findall(r'<h3>(.*?)</h3>', hits, flags=0)
            if len(name) > 0:
                searchRes['package'] = name[0]
            links = re.findall(r'<li.*?</li>', hits, flags=0)
            for ln in links:
                href = re.findall(r'href="(.*?)</a>', ln, flags=0)
                if len(href) > 0:
                    href = href[0]
                    ln = ln.split(href, 1)[1][4:-5]
                    ln = ln.split('<br>', 1)
                    des = ln[0].strip()
                    ver = ln[1].strip()
                    dis = href.split('">', 1)
                    href = dis[0].strip()
                    dis = dis[1].strip()
                    searchRes['links'].append({
                        'distribution': dis,
                        'link': baseurl + href,
                        'description': des,
                        'version': ver,
                    })
            result = searchRes['package']
            for ln in searchRes['links']:
                result += f"\n{ln['distribution']}:\n{ln['description']}\n{ln['version']}\n{ln['link']}"
            return result
        else:
            return 'No search result.'


def main(msgdict):
    req = list(msgdict['raw_message'].strip().split(' ', 1))
    helpmsg = 'Debian 包查询'
    if len(req) > 1:
        keywords = req[1].strip()
        return search_debian(keywords)

    return helpmsg


if __name__ == '__main__':
    print(search_debian('linux'))
