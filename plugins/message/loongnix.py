# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

"""
Loongnix 包查询
"""

import gnupg
import requests
import time
import hashlib
import gzip
import lzma
import sqlite3
import threading
import re
import logging
import hakuData.method as method

myLogger = logging.getLogger('hakuBot')
dbpath = method.sqlite_get_path('message', 'loongnix')


def fetch_files(url, md5):
    res = requests.get(url, timeout=60)
    if res.status_code == 200:
        content = res.content
        h = hashlib.md5()
        h.update(content)
        if h.hexdigest() != md5:
            return {}

        profix = url[-3:]
        if profix == '.gz':
            content = gzip.decompress(content).decode('utf-8')
        elif profix == '.xz':
            content = lzma.decompress(content, lzma.FORMAT_XZ).decode('utf-8')

        content = content.split('\n\n')
        result = {}
        for con in content:
            con = con.split('\n')
            if len(con) < 2:
                continue
            for conp in range(len(con)-1, -1, -1):
                if con[conp][0] == ' ':
                    con[conp-1] = f"{con[conp-1]}\n{con[conp]}"
                    con.pop(conp)
            pkg = ''
            inf = {}
            for pcon in con:
                pcon = pcon.split(':')
                if len(pcon) < 2:
                    continue
                key = pcon[0].strip()
                value = pcon[1].strip()
                if key == 'Package':
                    pkg = value
                else:
                    inf.update({key: value})
            if pkg and inf:
                result.update({pkg: inf})

        return result
    return {}


def fetch_lists(baseurl, pkgtree):
    subpaths = pkgtree['subdirs']
    if subpaths:
        tfiles = {}
        for s in subpaths.keys():
            url = f"{baseurl}/{s}"
            tfiles.update(fetch_lists(url, subpaths[s]))
        return tfiles
    else:
        url = f"{baseurl}/{pkgtree['package']}"
        md5 = pkgtree['md5']
        trys = 0
        tfiles = {}
        while not tfiles:
            tfiles = fetch_files(url, md5)
            trys += 1
            if trys > 5:
                break
        return tfiles


def fetch_pkgs(baseurl, distri):
    res = requests.get(url=f'{baseurl}dists/{distri}/InRelease', timeout=60)
    if res.status_code == 200:
        releasetext = res.text
    else:
        myLogger.warning(f'Fetch InRelease failed: {res.status_code}')
        return
    res = requests.get(url=f'{baseurl}dists/{distri}/Release.gpg', timeout=60)
    if res.status_code == 200:
        gpgtext = res.text
    else:
        myLogger.warning(f'Fetch Release.gpg failed: {res.status_code}')
        return

    gpgtext = gpgtext.replace('\n', '')
    gpgtext = gpgtext.replace('\r', '')
    gpg = gnupg.GPG()
    status = gpg.decrypt(releasetext, passphrase=gpgtext)

    outmsg = status.data.decode('utf-8')
    if len(outmsg) == 0:
        myLogger.warning('No Release file.')

    dictmsg = outmsg.split()
    ansdict = {}
    anskey = ''
    ansmsg = ''
    for s in dictmsg:
        if s[-1] == ':':
            if anskey != '':
                ansdict.update({anskey: ansmsg.lstrip()})
            anskey = s[:-1]
            ansmsg = ''
        else:
            ansmsg = f'{ansmsg} {s}'
    if anskey != '':
        ansdict.update({anskey: ansmsg.lstrip()})

    #print(ansdict)
    ansdict['Date'] = time.strptime(ansdict['Date'], '%a, %d %b %Y %H:%M:%S %Z')
    ansdict['Architectures'] = ansdict['Architectures'].split()
    ansdict['Components'] = ansdict['Components'].split()

    files = ansdict.get('MD5Sum').split()
    comp = ansdict.get('Components')
    if (not files) or (not comp):
        myLogger.warning('Unsupported mirror.')
    if len(files) % 3 != 0:
        myLogger.warning('Corrupt Release file.')

    pkgtree = {
            'subdirs': {},
            'package': '',
        }
    for dir in ansdict['Components']:
        pkgtree['subdirs'].update({dir: {'subdirs': {}, 'package': '', 'md5': '', 'size': '', }})
    pat = 'Package.*'
    for i in range(2, len(files), 3):
        fpath = files[i].split('/')
        if fpath[0] not in comp:
            continue
        if not re.match(pat, fpath[-1]):
            continue
        lenth = len(fpath)-1
        subtree = pkgtree['subdirs'][fpath[0]]
        for j in range(1, lenth):
            if fpath[j] not in subtree['subdirs'].keys():
                subtree['subdirs'].update({fpath[j]: {'subdirs': {}, 'package': '', 'md5': '', 'size': '', }})
            subtree = subtree['subdirs'][fpath[j]]
        if subtree['package'] == '' or subtree['size'] > int(files[i - 1]):
            subtree['package'] = fpath[-1]
            subtree['size'] = int(files[i - 1])
            subtree['md5'] = files[i - 2]

    pkglist = fetch_lists(f'{baseurl}dists/{distribution}', pkgtree)

    with sqlite3.connect(dbpath) as conn:
        cur = conn.cursor()
        try:
            cur.execute('CREATE TABLE IF NOT EXISTS packages'
                        '(Package VARCHAR(2048), Version VARCHAR(2048), '
                        'Architecture VARCHAR(2048), Description VARCHAR(4096), '
                        'PRIMARY KEY(Package, Version));')
            cur.execute('CREATE TABLE IF NOT EXISTS lastupdate(date DOUBLE);')
            cur.execute('DELETE FROM packages;')
            for key in pkglist.keys():
                pkg = pkglist[key]
                cur.execute('INSERT INTO packages VALUES(?, ?, ?, ?);', (key, pkg['Version'], pkg['Architecture'], pkg['Description']))
            cur.execute('DELETE FROM lastupdate;')
            cur.execute('INSERT INTO lastupdate VALUES(?)', (time.time(),))
        except Exception as e:
            pass
        else:
            conn.commit()


baseUrl = 'http://pkg.loongnix.cn/loongnix/'
distribution = 'DaoXiangHu-testing'
updateThread = threading.Thread()
updateLock = threading.Lock()


def search_pkgs(pkg):
    global updateThread, updateLock

    with sqlite3.connect(dbpath) as conn:
        cur = conn.cursor()
        try:
            ans = cur.execute('SELECT * FROM lastupdate')
            ans = ans.fetchall()
        except:
            ans = ()
    if len(ans) > 0:
        delta = time.time() - ans[0][0]
    else:
        delta = -1
    if delta > 60*3600 or delta < 0:
        if updateLock.acquire(1):
            try:
                if not updateThread.is_alive():
                    updateThread = threading.Thread(target=fetch_pkgs, args=(baseUrl, distribution))
                    updateThread.start()
            except:
                pass
            updateLock.release()
        if updateThread.is_alive():
            return 'Updating database.'

    with sqlite3.connect(dbpath) as conn:
        cur = conn.cursor()
        try:
            ans = cur.execute('SELECT * FROM packages WHERE Package LIKE ?', (f'%{pkg}%',))
            pkgs = ans.fetchall()
        except:
            return 'Search ERROR.'
    cnt = 0
    if pkgs:
        ans = 'Search result(s):'
    else:
        ans = 'No result.'
    for pk in pkgs:
        cnt += 1
        slen = min(128, len(pk[3]))
        ans += f"\n\nPackage: {pk[0]} {pk[1]}\nArchitecture: {pk[2]}"
        if len(pk[3]) > 256:
            ans += f"\n{pk[3][0:256]}..."
        else:
            ans += f"\n{pk[3]}"
        if cnt >= 5:
            break
    return ans


def main(msgdict):
    req = list(msgdict['raw_message'].strip().split(' ', 1))
    helpmsg = 'Loongnix 包查询'
    if len(req) > 1:
        keywords = req[1].strip()
        return search_pkgs(keywords)

    time.sleep(10)
    return helpmsg


def quit_plugin():
    global updateThread, updateLock
    if updateLock.acquire(1):
        cnt = 6
        while updateThread.is_alive():
            cnt -= 1
            time.sleep(10)
            if cnt <= 0:
                break


if __name__ == '__main__':
    print(search_pkgs('driver'))
