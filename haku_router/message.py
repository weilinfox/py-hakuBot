# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import json, logging, threading, importlib
import haku_data.method
import haku_data.status
import haku_core.api_cqhttp as hakuApi
import haku_core.plugin as hakuPlg

configDict = haku_data.method.get_config_dict()
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
haku_data.status.regest_router('message', {'message_frequency':0})


def check_msg_cache(msgdict):
    """
    消息缓存
    :param msgdict: 消息字典
    """
    global groupMsgCache, groupMsgCacheLock, msgTimeCache, msgTimeCacheLen
    with msgTimeCacheLock:
        tm = msgdict['time']
        delList = []
        msgTimeCache.append(tm)
        msgTimeCacheLen += 1
        for t in msgTimeCache:
            if tm - t >= 60: delList.append(t)
        for t in delList:
            msgTimeCache.remove(t)
        msgTimeCacheLen -= len(delList)
        haku_data.status.refresh_status('message', {'message_frequency':msgTimeCacheLen})
    if msgdict['message_type'] != 'group': return
    gid = msgdict['group_id']
    myLogger.debug('Insert message to group message cache.')
    canRepeat = True
    with groupMsgCacheLock:
        # 新消息插入和复读
        repeatMsg, repeatQid, repeatNow = msgdict['message'], msgdict['user_id'], msgdict['time']
        if not (gid in groupMsgCache):
            groupMsgCache[gid] = {'pos':-1, 'msgCount':0, 'msgDicts':[{'msgDict':{}, 'repeated':False} for i in range(16)]}
            canRepeat = False
        posNow = (groupMsgCache[gid]['pos'] + 1) % 16
        posPast = (posNow + 15) % 16
        groupMsgCache[gid]['msgDicts'][posNow]['msgDict'] = msgdict
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
        hakuApi.reply_msg(msgdict, repeatMsg)


def new_event(msgdict):
    """
    新事件
    :param msgdict: 消息字典
    """
    check_msg_cache(msgdict)
    myLogger.info(f'Current message frequency: {msgTimeCacheLen}/min\nGet message: {msgdict}')
    modname = ''
    if msgdict['message'][0] == INDEX:
        # modname = list(msgDict['message'][1:].split())[0]
        modname = list(msgdict['message'].split())[0][1:]
    if modname:
        myLogger.debug(f'Cache plugin: {msgdict["message"][1:]}')
        hakuPlg.run_module(msgdict, 'message', modname)
