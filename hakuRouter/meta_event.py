# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import logging, time, threading
import hakuData.status
import hakuData.method
import hakuCore.cqhttpApi
import hakuCore.report

myLogger = logging.getLogger('hakuBot')
pluginModules = dict()

configDict = hakuData.method.get_config_dict()
serverConfig = configDict.get('server_config', {})
hakuConfig = configDict.get('haku_config', {})
INDEX = hakuConfig.get('index', '.')

# 消息统计
heartBeatCache = list()
heartBeatCacheLen = 0
errorCount = 0
timeDelay = 0

# 注册自己
hakuData.status.regest_router('meta_event', {'event_frequency':0})

# 用户数据 {group_id:{'time':{time1, time2, ...}, time1:['msg1', ...], time2:['msg2', ...], ...}, ...}
userTimeLock = threading.Lock()
userTimeFile = 'meta_event.user_time_table.csv'
userTimeDict = dict()
userDateLock = threading.Lock()
userDateFile = 'meta_event.user_schedual.csv'
userDateDict = dict()
groupTimeLock = threading.Lock()
groupTimeFile = 'meta_event.group_time_table.csv'
groupTimeDict = dict()
groupDateLock = threading.Lock()
groupDateFile = 'meta_event.group_schedual.csv'
groupDateDict = dict()
updateTime = int(time.time())
processTimeSet = set()

def load_group_time_csv():
    global groupTimeDict
    myLogger.debug('Loading group time table...')
    with groupTimeLock:
        rawData = hakuData.method.read_dict_csv_file(groupTimeFile, ['group_id', 'time', 'message'])
        for dct in rawData:
            if dct['group_id'] in groupTimeDict:
                if dct['time'] in groupTimeDict[dct['group_id']]['time']:
                    groupTimeDict[dct['group_id']][dct['time']].append(dct['message'])
                else:
                    groupTimeDict[dct['group_id']]['time'].add(dct['time'])
                    groupTimeDict[dct['group_id']][dct['time']] = [dct['message']]
            else:
                groupTimeDict[dct['group_id']] = {'time':{dct['time']}, dct['time']:[dct['message']]}
    myLogger.debug('Finish loading group time table.')
    print(groupTimeDict)

def load_group_date_csv():
    global groupDateDict
    myLogger.debug('Loading group schedual...')
    with groupDateLock:
        rawData = hakuData.method.read_dict_csv_file(groupDateFile, ['group_id', 'date', 'message'])
        for dct in rawData:
            if dct['group_id'] in groupDateDict:
                if dct['date'] in groupDateDict[dct['group_id']]['date']:
                    groupDateDict[dct['group_id']][dct['date']].append(dct['message'])
                else:
                    groupDateDict[dct['group_id']]['date'].add(dct['date'])
                    groupDateDict[dct['group_id']][dct['date']] = [dct['message']]
            else:
                groupDateDict[dct['group_id']] = {'date':{dct['date']}, dct['date']:[dct['message']]}
    myLogger.debug('Finish loading group schedual.')
    print(groupDateDict)

def load_user_time_csv():
    global userTimeDict
    myLogger.debug('Loading user time table...')
    with userTimeLock:
        rawData = hakuData.method.read_dict_csv_file(userTimeFile, ['user_id', 'time', 'message'])
        for dct in rawData:
            if dct['user_id'] in userTimeDict:
                if dct['time'] in userTimeDict[dct['user_id']]['time']:
                    userTimeDict[dct['user_id']][dct['time']].append(dct['message'])
                else:
                    userTimeDict[dct['user_id']]['time'].add(dct['time'])
                    userTimeDict[dct['user_id']][dct['time']] = [dct['message']]
            else:
                userTimeDict[dct['user_id']] = {'time':{dct['time']}, dct['time']:[dct['message']]}
    myLogger.debug('Finish loading user time table.')
    print(userTimeDict)

def load_user_date_csv():
    global userDateDict
    myLogger.debug('Loading user schedual...')
    with userDateLock:
        rawData = hakuData.method.read_dict_csv_file(userDateFile, ['user_id', 'date', 'message'])
        for dct in rawData:
            if dct['user_id'] in userDateDict:
                if dct['date'] in userDateDict[dct['user_id']]['date']:
                    userDateDict[dct['user_id']][dct['date']].append(dct['message'])
                else:
                    userDateDict[dct['user_id']]['date'].add(dct['date'])
                    userDateDict[dct['user_id']][dct['date']] = [dct['message']]
            else:
                userDateDict[dct['user_id']] = {'date':{dct['date']}, dct['date']:[dct['message']]}
    myLogger.debug('Finish loading user schedual.')
    print(userDateDict)

def new_event(msgDict):
    global myLogger, heartBeatCache, heartBeatCacheLen, errorCount
    global userTimeDict, groupTimeDict, updateTime, processTimeSet
    timeNow = int(time.time())
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
    # 每十五分钟查询一次数据更新
    if timeNow - updateTime >= 60*15:
        updateTime = timeNow
        myLogger.debug('Ask whether need to update time table.')
        if hakuData.method.get_csv_update_flag(userTimeFile):
            load_user_time_csv()
        if hakuData.method.get_csv_update_flag(groupTimeFile):
            load_group_time_csv()
        if hakuData.method.get_csv_update_flag(userDateFile):
            load_user_date_csv()
        if hakuData.method.get_csv_update_flag(groupDateFile):
            load_group_date_csv()

    # 小时+8
    time_struct = time.gmtime(timeNow + 8 * 3600 + 60) # 下一分钟
    timeFlag = str(time_struct.tm_hour * 100 + time_struct.tm_min)
    dateFlag = str(time_struct.tm_mon * 100 + time_struct.tm_mday)
    groupTimes = dict()
    groupComs = dict()
    userTimes = dict()
    userComs = dict()
    if not timeFlag in processTimeSet:
        processTimeSet.add(timeFlag)
        # 群时间表
        for grpDctK in groupTimeDict.keys():
            if timeFlag in groupTimeDict[grpDctK]['time']:
                groupTimes[grpDctK] = []
                groupComs[grpDctK] = []
                for msg in groupTimeDict[grpDctK][timeFlag]:
                    if msg[0] == INDEX and len(msg) > 1:
                        groupComs[grpDctK].append(msg)
                    else:
                        groupTimes[grpDctK].append(msg)
        # 群日志
        if timeFlag == 0:
            for grpDctK in groupDateDict.keys():
                if dateFlag in groupDateDict[grpDctK]['date']:
                    if not groupDctK in groupTimes:
                        groupTimes[grpDctK] = []
                        groupComs[grpDctK] = []
                    for msg in groupDateDict[grpDctK][dateFlag]:
                        if msg[0] == INDEX and len(msg) > 1:
                            groupComs[grpDctK].append(msg)
                        else:
                            groupTimes[grpDctK].append(msg)
        # 个人时间表
        for usrDctK in userTimeDict.keys():
            if timeFlag in userTimeDict[usrDctK]['time']:
                userTimes[usrDctK] = []
                userComs[usrDctK] = []
                for msg in userTimeDict[usrDctK][timeFlag]:
                    if msg[0] == INDEX and len(msg) > 1:
                        userComs[usrDctK].append(msg)
                    else:
                        userTimes[usrDctK].append(msg)
        # 个人日志
        if timeFlag == 0:
            for usrDctK in userDateDict.keys():
                if dateFlag in userDateDict[usrDctK]['date']:
                    if not usrDctK in userTimes:
                        userTimes[usrDctK] = []
                        userComs[usrDctK] = []
                    for msg in userDateDict[usrDctK][dateFlag]:
                        if msg[0] == INDEX and len(msg) > 1:
                            userComs[usrDctK].append(msg)
                        else:
                            userTimes[usrDctK].append(msg)
        print(dateFlag, timeFlag)
        print(groupTimes)
        print(groupComs)
        print(userTimes)
        print(userComs)
        # 等待时机
        newTime_struct = time.gmtime(time.time() + 8 * 3600 + 60) # 下一分钟
        newTimeFlag = str(time_struct.tm_hour * 100 + time_struct.tm_min)
        if newTimeFlag == timeFlag:
            waitSec = 60 - (int(time.time()) % 60) - 1
            if waitSec > 0:
                myLogger.debug(f'Wait for {waitSec}s')
                time.sleep(waitSec)
        myLogger.debug('Waiting...')
        while int(time.time()) % 60 != 0: pass
        # 发送
        myLogger.debug('Send!')
        for grp in groupTimes.keys():
            print(grp, groupTimes[grp])
            for msg in groupTimes[grp]:
                print(msg)
                hakuCore.cqhttpApi.send_group_msg(grp, msg)
        for usr in userTimes.keys():
            print(usr, userTimes[usr])
            for msg in userTimes[usr]:
                print(msg)
                hakuCore.cqhttpApi.send_private_msg(usr, msg)
        processTimeSet.remove(timeFlag)

def link_modules(plgs):
    global pluginModules
    pluginModules = plgs


# 数据初始化
load_group_time_csv()
load_group_date_csv()
load_user_time_csv()
load_user_date_csv()
