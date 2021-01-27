# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import logging, time
import hakuData.status
import hakuData.method
import hakuCore.cqhttpApi
import hakuCore.report

myLogger = logging.getLogger('hakuBot')
pluginModules = dict()

# 消息统计
heartBeatCache = list()
heartBeatCacheLen = 0
errorCount = 0
timeDelay = 0

hakuData.status.regest_router('meta_event', {'event_frequency':0})

def new_event(msgDict):
    global myLogger, heartBeatCache, heartBeatCacheLen, errorCount
    # 获取go-cqhttp状态
    cqhttpStatus = msgDict.get('status', {})
    if cqhttpStatus:
        if not cqhttpStatus['app_enabled'] or not cqhttpStatus['app_good'] or \
            not cqhttpStatus['app_initialized'] or not cqhttpStatus['good'] or not cqhttpStatus['online']:
            myLogger.info(f'Catch error in meta event: {cqhttpStatus}')
            errorCount += 1
        else:
            errorCount = 0
        #    myLogger.debug(f'Call meta event: {msgDict}')
    if errorCount > 99:
        errorCount = 0
        myLogger.error('Error count exceeded.')
        hakuCore.cqhttpApi.set_restart()
        time.sleep(60)
        hakuCore.report.report('Error count exceeded, go-cqhttp restarted.')
    # 获取heartbeat速率
    if msgDict['meta_event_type'] == 'heartbeat':
        tm = msgDict['time']
        delList = []
        heartBeatCache.append(tm)
        heartBeatCacheLen += 1
        for t in heartBeatCache:
            if tm - t >= 60: delList.append(t)
        for t in delList:
            heartBeatCache.remove(t)
        heartBeatCacheLen -= len(delList)
        hakuData.status.refresh_status('meta_event', {'heartbeat_frequency':heartBeatCacheLen})

    # 事件逻辑
    

def link_modules(plgs):
    global pluginModules
    pluginModules = plgs
