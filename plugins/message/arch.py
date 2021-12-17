# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

"""
Archlinux 包查询
"""

import requests
import re


def search_arch(keywords):
    baseurl = 'https://archlinux.org'
    searchurl = '/packages/'
    params = {
        'sort': '',
        'maintainer': '',
        'flagged': '',
        'q': keywords,
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

        searchRes = []

        hits = re.findall(r'<table class="results">(.*?)</table>', restext, flags=0)
        if len(hits) == 0:
            return 'No search result.'
        hits = re.findall(r'<tr>(.*?)</tr>', hits[0], flags=0)
        result = 'Search Result(s):'
        for i in range(min(5, len(hits))):
            if i == 0:
                continue
            p = re.findall(r'<td.*?</td>', hits[i], flags=0)
            try:
                pkg = {
                    'arch': re.findall(r'<td>(.*?)</td>', p[0], flags=0)[0],
                    'repo': re.findall(r'<td>(.*?)</td>', p[1], flags=0)[0],
                    'name': re.findall(r'">(.*?)</a></td>', p[2], flags=0)[0],
                    'link': baseurl+re.findall(r'href="(.*?)"', p[2], flags=0)[0],
                    'version': re.findall(r'<td>(.*?)</td>', p[3], flags=0)[0],
                    'description': re.findall(r'">(.*?)</td>', p[4], flags=0)[0],
                    'lastupdate': re.findall(r'<td>(.*?)</td>', p[5], flags=0)[0],
                    'flagdate': re.findall(r'<td>(.*?)</td>', p[6], flags=0)[0],
                }
            except Exception:
                pass
            else:
                for k in pkg.keys():
                    inhtmls = re.findall(r'<.*?>', pkg[k], flags=0)
                    for s in inhtmls:
                        pkg[k] = pkg[k].replace(s, '')
                searchRes.append(pkg)
        if len(searchRes) == 0:
            return 'No search result.'
        for rs in searchRes:
            result += f"\nPackage {rs['name']} {rs['version']}\n{rs['arch']} {rs['repo']}\n"\
                      f"{rs['description']}\n{rs['link']}"
        return result
    else:
        return 'Archlinux server error.'


def main(msgdict):
    req = list(msgdict['raw_message'].strip().split(' ', 1))
    helpmsg = 'Archlinux 包查询'
    if len(req) > 1:
        keywords = req[1].strip()
        return search_arch(keywords)

    return helpmsg


if __name__ == '__main__':
    print(search_arch('linux'))
