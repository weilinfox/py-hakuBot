# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import logging, time, threading, requests
import hakuCore.cqhttpApi
import hakuData.method
import hakuCore.report

configDict = hakuData.method.get_config_dict()
serverConfig = configDict.get('server_config', {})
hakuConfig = configDict.get('haku_config', {})

INDEX = hakuConfig.get('index', '.')

myLogger = logging.getLogger('hakuBot')

textFiles = {'txt':'text', 'log':'text', 'md':'md', 'csv':'text', 'tex':'tex',
             'sh':'sh', 'bash':'bash', 'zsh':'zsh', 'cmake':'cmake',
             'py':'py', 'java':'java', 'kt':'kotlin', 'go':'go', 'cs':'csharp',
             'c':'c', 'cpp':'cpp', 'cxx':'cpp', 'h':'c', 'hpp':'cpp', 'cu':'cuda',
             's':'asm', 'S':'asm', 'asm':'asm', 'v':'verilog', 'vhd':'vhdl', 'vhdl':'vhdl',
             'php':'php', 'html':'html', 'css':'css', 'jsp':'jsp', 'js':'js',
             'json':'json', 'hjson':'text', 'xml':'xml', 'yaml':'yaml',
             'lisp':'lisp', 'pas':'pascal', 'erl':'erlang', 'hrl':'erlang', 'rs':'rust',
             'hs':'haskell', 'lua':'lua', 'pl':'perl', 'rb':'ruby', 'swift':'swift'}
pastebinUrl = 'https://fars.ee/'
pastebinHeaders = {'Content-Type': 'application/json', 'Accept': 'application/json'}
pastebinJson = {'content': ''}
def check_upload_file(fileType, fileName, fileLink):
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
                pasteRet = requests.post(url = pastebinUrl,
                                         headers = pastebinHeaders,
                                         json = myJson,
                                         timeout = (1,10)
                                         )
            except:
                pass
            else:
                if pasteRet.status_code == 200:
                    return f"{pasteRet.json()['url']}/{textFiles[fileType]}"
    return ''

def block_group(groupId):
    if groupId in [776045778,614236428,865409903]:
        return True
    return False


def new_event(msgDict):
    myLogger.debug(f'Get notice: {msgDict}')
    if block_group(msgDict.get('group_id', -1)):
        myLogger.debug(f'Block group: {msgDict.get("group_id", -1)}')
        return
    if msgDict['notice_type'] == 'group_increase' and msgDict['user_id'] != msgDict['self_id']:
        greetMsg = f'欢迎欢迎，进了群就是一家人了~\n{INDEX}help 查看给小白的指示哦'
        hakuCore.cqhttpApi.send_group_msg(msgDict['group_id'], '[CQ:at,qq=' + str(msgDict['user_id']) + ']\n' + greetMsg)
    elif msgDict['notice_type'] == 'notify' and msgDict['sub_type'] == 'lucky_king':
        greetMsg = '运气王出现了'
        hakuCore.cqhttpApi.send_group_msg(msgDict['group_id'], '[CQ:at,qq=' + str(msgDict['target_id']) + ']\n' + greetMsg)
    elif msgDict['notice_type'] == 'friend_add':
        myLogger.info(f'收到新的好友添加请求，来自id: {msgDict["user_id"]}')
        hakuCore.report.report(f'收到新的好友添加请求，来自id: {msgDict["user_id"]}')
    elif msgDict['notice_type'] == 'group_upload':
        fileInfo = msgDict['file']
        fileSize = fileInfo['size']
        fileName = fileInfo['name']
        fileLink = fileInfo['url']
        fileType = fileName.split('.', fileName.count('.'))[-1]
        pasteLink = ''
        if fileSize < 1048576:
            # pastebin
            pasteLink = check_upload_file(fileType, fileName, fileLink)
            if fileSize < 1024:
                fileSize = f'{fileSize} B'
            else:
                fileSize = f'{fileSize/1024:.2f} KB'
        elif fileSize < 1073741824:
            fileSize = f'{fileSize/1048576:.2f} MB'
        else:
            fileSize = f'{fileSize/1073741824:.2f} GB'
        retMsg = f'↑文件上传信息~\n文件名: {fileName}\n文件类型: {fileType}\n文件大小: {fileSize}'
        if pasteLink:
            retMsg += f'\nPastebin: {pasteLink}'
        hakuCore.cqhttpApi.send_group_msg(msgDict['group_id'], retMsg)
    elif msgDict['notice_type'] == 'offline_file':
        fileInfo = msgDict['file']
        fileSize = fileInfo['size']
        fileName = fileInfo['name']
        fileLink = fileInfo['url']
        fileType = fileName.split('.', fileName.count('.'))[-1]
        pasteLink = ''
        if fileSize < 1048576:
            # pastebin
            pasteLink = check_upload_file(fileType, fileName, fileLink)
            if fileSize < 1024:
                fileSize = f'{fileSize} B'
            else:
                fileSize = f'{fileSize/1024:.2f} KB'
        elif fileSize < 1073741824:
            fileSize = f'{fileSize/1048576:.2f} MB'
        else:
            fileSize = f'{fileSize/1073741824:.2f} GB'
        retMsg = f'↑文件上传信息~\n文件名: {fileName}\n文件类型: {fileType}\n文件大小: {fileSize}'
        if pasteLink:
            retMsg += f'\nPastebin: {pasteLink}'
        hakuCore.cqhttpApi.send_private_msg(msgDict['user_id'], retMsg)
        

