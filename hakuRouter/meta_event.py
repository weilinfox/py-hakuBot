# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import logging
import hakuData.status

myLogger = logging.getLogger('hakuBot')
pluginModules = dict()

# 消息统计
metaTimeCache = list()
metaTimeCacheLen = 0

hakuData.status.regest_router('meta_event', {'event_frequency':0})

def new_event(msgDict):
    global myLogger, metaTimeCache, metaTimeCacheLen
    myLogger.debug(f'Call meta event: {msgDict}')
    tm = msgDict['time']
    delList = []
    metaTimeCache.append(tm)
    metaTimeCacheLen += 1
    for t in metaTimeCache:
        if tm - t >= 60: delList.append(t)
    for t in delList:
        metaTimeCache.remove(t)
    metaTimeCacheLen -= len(delList)
    hakuData.status.refresh_status('meta_event', {'message_frequency':metaTimeCacheLen})

def link_modules(plgs):
    global pluginModules
    pluginModules = plgs
