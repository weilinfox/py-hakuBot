# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE
"""
notice 事件处理
支持入群欢迎
支持运气王提示
支持加好友提示
支持文件上传提示
支持自动判断上传的文本/代码转 pastebin

支持自定义入群欢迎信息
支持屏蔽入群欢迎
支持自定义群屏蔽整个功能
支持自定义群屏蔽 pastebin 上传

数据库使用 sqlite3
对上传的文本转 base64 后存储
"""

import logging
import sqlite3
import base64
import requests
import hakuCore.cqhttpApi
import hakuData.method
import hakuCore.report

configDict = hakuData.method.get_config_dict()
serverConfig = configDict.get('server_config', {})
hakuConfig = configDict.get('haku_config', {})

INDEX = hakuConfig.get('index', '.')

myLogger = logging.getLogger('hakuBot')


greetMsgDict = dict()
blockGidDict = {'greet': set(), 'notice': set(), 'pastebin': set()}


def base64_decode(b64msg):
    """
    base64 解码 默认 UTF-8
    :param b64msg: base64 密文
    :return: 解码后的 str
    """
    try:
        msg = base64.b64decode(b64msg.encode()).decode()
    except:
        return ''
    return msg


def notice_init_data():
    """
    初始化入群欢迎消息和功能屏蔽 只在载入时调用一次
    :return: 无返回值
    """
    global greetMsgDict, blockGidDict

    conn = hakuData.method.sqlite_default_db_open('notice', 'notice')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS greetmsg(gid BIGINT, greetmsg VARCHAR(2048));')
    cur.execute('CREATE TABLE IF NOT EXISTS blockgid(gid BIGINT, greet BYTE, notice BYTE, pastebin BYTE);')
    cur.execute('DELETE FROM greetmsg WHERE greetmsg IS NULL OR greetmsg=""')
    rawdata = cur.execute('SELECT * FROM greetmsg;').fetchall()
    for d in rawdata:
        greetMsgDict[d[0]] = base64_decode(d[1])
    rawdata = cur.execute('SELECT * FROM blockgid;').fetchall()
    blockGidDict = {'greet': set(), 'notice': set(), 'pastebin': set()}
    for d in rawdata:
        if d[1]:
            blockGidDict['greet'].add(d[0])
        if d[2]:
            blockGidDict['notice'].add(d[0])
        if d[3]:
            blockGidDict['pastebin'].add(d[0])
    hakuData.method.sqlite_db_close(conn)


notice_init_data()


def notice_get_greet(gid):
    """
    获取 id 对应的自定义消息
    :param gid: 群 id
    :return: 自定义消息 不存在返回 ''
    """
    return greetMsgDict.get(gid, f'欢迎欢迎，进了群就是一家人了~\n{INDEX}help 查看给小白的指示哦')


def notice_check_block(gid, ukey):
    """
    是否在屏蔽列表中
    :param gid: 群 id
    :param ukey: 屏蔽位名
    :return: 是/否 屏蔽 bool
    """
    if gid < 1:
        return False
    if ukey not in ['greet', 'notice', 'pastebin']:
        return False
    return gid in blockGidDict[ukey]


def notice_update_block(gid, ukey, uflag):
    """
    更新屏蔽位
    :param gid: 群 id
    :param ukey: 屏蔽位名
    :param uflag: 打开/关闭 bool
    :return: 成功/失败 bool
    """
    global blockGidDict

    if ukey not in ['greet', 'notice', 'pastebin']:
        return False
    datanow = gid in blockGidDict[ukey]
    if uflag == datanow:
        return True
    if uflag:
        flagdata = 1
    else:
        flagdata = 0
    try:
        conn = hakuData.method.sqlite_default_db_open('notice', 'notice')
        cur = conn.cursor()
        if cur.execute(f'SELECT * FROM blockgid WHERE gid={gid}').fetchall():
            cur.execute(f'UPDATE blockgid SET {ukey}={flagdata} WHERE gid={gid}')
        else:
            cur.execute(f'INSERT INTO blockgid (gid, {ukey}) VALUES(?,?)', (gid, flagdata))
        if uflag:
            blockGidDict[ukey].add(gid)
        else:
            if gid in blockGidDict[ukey]:
                blockGidDict[ukey].remove(gid)
        hakuData.method.sqlite_db_close(conn)
    except Exception as e:
        myLogger.exception(e)
        return False

    return True


def notice_update_greetmsg(gid, msg):
    """
    更新入群欢迎消息
    :param gid: 群 id
    :param msg: 消息
    :return: 更新 成功/失败 bool
    """
    global greetMsgDict

    try:
        b64msg = base64.b64encode(msg.encode()).decode()
    except Exception as e:
        return False
    if len(b64msg) > 2047:
        return False

    try:
        conn = hakuData.method.sqlite_default_db_open('notice', 'notice')
        cur = conn.cursor()
        if gid in greetMsgDict:
            cur.execute(f'UPDATE greetmsg SET greetmsg={b64msg} WHERE id={gid}')
        else:
            cur.execute(f'INSERT INTO greetmsg (gid, greetmsg) VALUES (?,?)', (gid, b64msg))
        greetMsgDict[gid] = msg
        hakuData.method.sqlite_db_close(conn)
    except Exception as e:
        myLogger.exception(e)
        return False

    return True


textFiles = {'txt': 'text', 'log': 'text', 'md': 'md', 'csv': 'text', 'tex': 'tex',
             'sh': 'sh', 'bash': 'bash', 'zsh': 'zsh', 'cmake': 'cmake',
             'py': 'py', 'java': 'java', 'kt': 'kotlin', 'go': 'go', 'cs': 'csharp',
             'c': 'c', 'cpp': 'cpp', 'cxx': 'cpp', 'h': 'c', 'hpp': 'cpp', 'cu': 'cuda',
             's': 'asm', 'S': 'asm', 'asm': 'asm', 'v': 'verilog', 'vhd': 'vhdl', 'vhdl': 'vhdl',
             'php': 'php', 'html': 'html', 'css': 'css', 'jsp': 'jsp', 'js': 'js',
             'json': 'json', 'hjson': 'text', 'xml': 'xml', 'yaml': 'yaml',
             'lisp': 'lisp', 'pas': 'pascal', 'erl': 'erlang', 'hrl': 'erlang', 'rs': 'rust',
             'hs': 'haskell', 'lua': 'lua', 'pl': 'perl', 'rb': 'ruby', 'swift': 'swift'}
pastebinUrl = 'https://fars.ee/'
pastebinHeaders = {'Content-Type': 'application/json', 'Accept': 'application/json'}
pastebinJson = {'content': ''}


def handle_group_upload_pastebin(fileType, fileName, fileLink, gid):
    """
    判断是否需要添加 pastebin 链接
    :param fileType: 文件类型
    :param fileName: 文件名
    :param fileLink: 文件链接
    :return: 返回 pastebin 链接
    """
    if notice_check_block(gid, 'pastebin'):
        return ''
    if not fileType in textFiles.keys():
        return ''
    try:
        myFile = requests.get(fileLink, timeout=(1, 10))
    except:
        pass
    else:
        if myFile.status_code == 200:
            myJson = pastebinJson.copy()
            myJson['content'] = myFile.text
            try:
                pasteRet = requests.post(url=pastebinUrl,
                                         headers=pastebinHeaders,
                                         json=myJson,
                                         timeout=(1, 10)
                                         )
            except:
                pass
            else:
                if pasteRet.status_code == 200:
                    return f"{pasteRet.json()['url']}/{textFiles[fileType]}"
    return ''


def handle_group_upload(msgDict):
    """
    group_upload 事件处理
    :param msgDict: 事件 dict
    :return: 返回发送的提示信息
    """
    fileInfo = msgDict['file']
    fileSize = fileInfo['size']
    fileName = fileInfo['name']
    fileLink = fileInfo['url']
    fileType = fileName.split('.', fileName.count('.'))[-1]
    pasteLink = ''
    if msgDict['message_type'] == 'group':
        gid = msgDict['group_id']
    else:
        gid = -1
    if fileSize < 1048576:
        # pastebin
        pasteLink = handle_group_upload_pastebin(fileType, fileName, fileLink, gid)
        if fileSize < 1024:
            fileSize = f'{fileSize} B'
        else:
            fileSize = f'{fileSize / 1024:.2f} KB'
    elif fileSize < 1073741824:
        fileSize = f'{fileSize / 1048576:.2f} MB'
    else:
        fileSize = f'{fileSize / 1073741824:.2f} GB'
    retMsg = f'↑文件上传信息~\n文件名: {fileName}\n文件类型: {fileType}\n文件大小: {fileSize}'
    if pasteLink:
        retMsg += f'\nPastebin: {pasteLink}'
    return retMsg


def handle_offline_file(msgDict):
    """
    offline_file 事件处理
    :param msgDict: 事件 dict
    :return: 返回发送的提示信息
    """
    return handle_group_upload(msgDict)


def handle_group_increase(msgDict):
    """
    group_incease 事件处理
    :param msgDict: 事件 dict
    :return: 返回发送的提示信息
    """
    msg = notice_get_greet(msgDict['group_id'])
    return '[CQ:at,qq=' + str(msgDict['user_id']) + ']\n' + msg


def handle_lucky_king(msgDict):
    """
    lucky_king 事件处理
    :param msgDict: 事件 dict
    :return: 返回发送的提示信息
    """
    msg = '运气王出现了'
    return '[CQ:at,qq=' + str(msgDict['target_id']) + ']\n' + msg


def new_event(msgDict):
    """
    notice 事件处理
    :param msgDict: 事件 dict
    :return: 无返回值
    """
    myLogger.debug(f'Get notice: {msgDict}')
    gid = msgDict.get('group_id', -1)

    if notice_check_block(gid, 'notice'):
        myLogger.debug(f'Block group: {gid}')
        return

    if msgDict['notice_type'] == 'group_increase' and msgDict['user_id'] != msgDict['self_id']:
        if gid == -1: return
        if not notice_check_block(gid, 'greet'):
            msg = handle_group_increase(msgDict)
            hakuCore.cqhttpApi.send_group_msg(gid, msg)
    elif msgDict['notice_type'] == 'notify' and msgDict['sub_type'] == 'lucky_king':
        if gid == -1: return
        msg = handle_lucky_king(msgDict)
        hakuCore.cqhttpApi.send_group_msg(gid, msg)
    elif msgDict['notice_type'] == 'friend_add':
        myLogger.info(f'收到新的好友添加请求，来自id: {msgDict["user_id"]}')
        hakuCore.report.report(f'收到新的好友添加请求，来自id: {msgDict["user_id"]}')
    elif msgDict['notice_type'] == 'group_upload':
        if gid == -1: return
        msg = handle_group_upload(msgDict)
        hakuCore.cqhttpApi.send_group_msg(gid, msg)
    elif msgDict['notice_type'] == 'offline_file':
        msg = handle_offline_file(msgDict)
        hakuCore.cqhttpApi.send_private_msg(msgDict['user_id'], msg)
