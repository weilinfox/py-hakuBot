# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import json, logging, threading, importlib
import hakuData.method
import hakuData.status
import hakuCore.cqhttpApi as hakuApi
import hakuCore.plugin as hakuPlg

configDict = hakuData.method.get_config_dict()
serverConfig = configDict.get('server_config', {})
hakuConfig = configDict.get('haku_config', {})

INDEX = hakuConfig.get('index', '.')

myLogger = logging.getLogger('hakuBot')

# 群消息缓存 {<groupId>:{'pos':0, 'msgCount':0, 'msgDicts':[{'msgDict':{}, 'repeated':False}, ...]}
groupMsgCacheLock = threading.Lock()
groupMsgCache = dict()

# 消息统计
msgTimeCache = list()
msgTimeCacheLen = 0
msgTimeCacheLock = threading.Lock()

# 注册status
hakuData.status.regest_router('message', {'message_frequency':0})

def check_msg_cache(msgDict):
    global groupMsgCache, groupMsgCacheLock, msgTimeCache, msgTimeCacheLen
    with msgTimeCacheLock:
        tm = msgDict['time']
        delList = []
        msgTimeCache.append(tm)
        msgTimeCacheLen += 1
        for t in msgTimeCache:
            if tm - t >= 60: delList.append(t)
        for t in delList:
            msgTimeCache.remove(t)
        msgTimeCacheLen -= len(delList)
        hakuData.status.refresh_status('message', {'message_frequency':msgTimeCacheLen})
    if msgDict['message_type'] != 'group': return
    gid = msgDict['group_id']
    myLogger.debug('Insert message to group message cache.')
    canRepeat = True
    with groupMsgCacheLock:
        # 新消息插入和复读
        repeatMsg, repeatQid, repeatNow = msgDict['message'], msgDict['user_id'], msgDict['time']
        if not (gid in groupMsgCache):
            groupMsgCache[gid] = {'pos':-1, 'msgCount':0, 'msgDicts':[{'msgDict':{}, 'repeated':False} for i in range(16)]}
            canRepeat = False
        posNow = (groupMsgCache[gid]['pos'] + 1) % 16
        posPast = (posNow + 15) % 16
        groupMsgCache[gid]['msgDicts'][posNow]['msgDict'] = msgDict
        groupMsgCache[gid]['msgDicts'][posNow]['repeated'] = False
        groupMsgCache[gid]['pos'] = posNow
        groupMsgCache[gid]['msgCount'] += 1
        if canRepeat and repeatMsg == groupMsgCache[gid]['msgDicts'][posPast]['msgDict']['message']:
            groupMsgCache[gid]['msgDicts'][posNow]['repeated'] = groupMsgCache[gid]['msgDicts'][posPast]['repeated']
        else:
            canRepeat = False
        canRepeat = canRepeat and (not groupMsgCache[gid]['msgDicts'][posNow]['repeated'])
        # 同一个人
        if canRepeat and repeatQid == groupMsgCache[gid]['msgDicts'][posPast]['msgDict']['user_id']: canRepeat = False
        # 超时
        if canRepeat and repeatNow - groupMsgCache[gid]['msgDicts'][posPast]['msgDict']['time'] >= 60: canRepeat = False
        # blocklist
        if repeatMsg in ['[视频]你的QQ暂不支持查看视频短片，请升级到最新版本后查看。']: canRepeat = False
        if canRepeat: groupMsgCache[gid]['msgDicts'][posNow]['repeated'] = True
    if canRepeat and (len(repeatMsg) == 1 or repeatMsg[0] != INDEX):
        hakuApi.reply_msg(msgDict, repeatMsg)

def new_event(msgDict):
    check_msg_cache(msgDict)
    myLogger.info(f'Current message frequency: {msgTimeCacheLen}/min\nGet message: {msgDict}')
    modName = ''
    if msgDict['message'][0] == INDEX:
        modName = list(msgDict['message'][1:].split())[0]
    if modName:
        myLogger.debug(f'Cache plugin: {msgDict["message"][1:]}')
        hakuPlg.run_module(msgDict, 'message', modName)
