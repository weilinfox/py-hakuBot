# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import logging, time, threading
import hakuData.status
import hakuData.method
import hakuCore.cqhttpApi
import hakuCore.report
import hakuCore.plugin

myLogger = logging.getLogger('hakuBot')

configDict = hakuData.method.get_config_dict()
serverConfig = configDict.get('server_config', {})
hakuConfig = configDict.get('haku_config', {})
INDEX = hakuConfig.get('index', '.')
ADMINQQ = hakuConfig.get('admin_qq', -1)
ADMINGRP = hakuConfig.get('admin_group', -1)

meta_msg_event = {
    'message':'',
    'raw_message':'',
    'message_id':-1,
    'message_type':'',
    'post_type':'message',
    'user_id':-1,
    'group_id':-1
}

# 消息统计
heartBeatCache = list()
heartBeatCacheLen = 0
errorCount = 0
timeDelay = 0

# 注册自己
hakuData.status.regest_router('meta_event', {'event_frequency':0})

# 循环指令 {'command':{'message':'msg', 'interval':0, 'last_call':0}, ...}
regularComLock = threading.Lock()
regularComFile = 'meta_event.regular_commands.csv'
regularComDict = dict()

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
processTimeNow = ''

def load_regular_commands():
    global regularComDict
    myLogger.debug('Loading regular commands')
    with regularComLock:
        rawDict = hakuData.method.csv_read_dict(regularComFile, ['command', 'interval'])
    for i in range(0, len(rawDict)):
        try:
            rawDict[i]['interval'] = int(rawDict[i]['interval'])
        except ValueError:
            myLogger.warning(f'Inlegal interval in {regularComFile}: {rawDict[i]["interval"]}')
            rawDict[i]['interval'] = 60
        except:
            myLogger.exception('RuntimeError')
        else:
            if rawDict[i]['interval'] == 0: rawDict[i]['interval'] = 1
            if rawDict[i]['command'][0] == INDEX and len(rawDict[i]['command']) > 1:
                com = list(rawDict[i]['command'].split())[0]
                regularComDict[com] = {'message':rawDict[i]['command'], 'interval':rawDict[i]['interval']*60, 'last_call':0}
    myLogger.debug(f'Finish loading regular commands. {regularComDict}')

def load_group_time_csv():
    global groupTimeDict
    myLogger.debug('Loading group time table...')
    with groupTimeLock:
        rawData = hakuData.method.csv_read_dict(groupTimeFile, ['group_id', 'time', 'message'])
        for dct in rawData:
            if dct['group_id'] in groupTimeDict:
                if dct['time'] in groupTimeDict[dct['group_id']]['time']:
                    groupTimeDict[dct['group_id']][dct['time']].append(dct['message'])
                else:
                    groupTimeDict[dct['group_id']]['time'].add(dct['time'])
                    groupTimeDict[dct['group_id']][dct['time']] = [dct['message']]
            else:
                groupTimeDict[dct['group_id']] = {'time':{dct['time']}, dct['time']:[dct['message']]}
    myLogger.debug(f'Finish loading group time table. {groupTimeDict}')

def load_group_date_csv():
    global groupDateDict
    myLogger.debug('Loading group schedual...')
    with groupDateLock:
        rawData = hakuData.method.csv_read_dict(groupDateFile, ['group_id', 'date', 'message'])
        for dct in rawData:
            if dct['group_id'] in groupDateDict:
                if dct['date'] in groupDateDict[dct['group_id']]['date']:
                    groupDateDict[dct['group_id']][dct['date']].append(dct['message'])
                else:
                    groupDateDict[dct['group_id']]['date'].add(dct['date'])
                    groupDateDict[dct['group_id']][dct['date']] = [dct['message']]
            else:
                groupDateDict[dct['group_id']] = {'date':{dct['date']}, dct['date']:[dct['message']]}
    myLogger.debug(f'Finish loading group schedual. {groupDateDict}')

def load_user_time_csv():
    global userTimeDict
    myLogger.debug('Loading user time table...')
    with userTimeLock:
        rawData = hakuData.method.csv_read_dict(userTimeFile, ['user_id', 'time', 'message'])
        for dct in rawData:
            if dct['user_id'] in userTimeDict:
                if dct['time'] in userTimeDict[dct['user_id']]['time']:
                    userTimeDict[dct['user_id']][dct['time']].append(dct['message'])
                else:
                    userTimeDict[dct['user_id']]['time'].add(dct['time'])
                    userTimeDict[dct['user_id']][dct['time']] = [dct['message']]
            else:
                userTimeDict[dct['user_id']] = {'time':{dct['time']}, dct['time']:[dct['message']]}
    myLogger.debug(f'Finish loading user time table. {userTimeDict}')

def load_user_date_csv():
    global userDateDict
    myLogger.debug('Loading user schedual...')
    with userDateLock:
        rawData = hakuData.method.csv_read_dict(userDateFile, ['user_id', 'date', 'message'])
        for dct in rawData:
            if dct['user_id'] in userDateDict:
                if dct['date'] in userDateDict[dct['user_id']]['date']:
                    userDateDict[dct['user_id']][dct['date']].append(dct['message'])
                else:
                    userDateDict[dct['user_id']]['date'].add(dct['date'])
                    userDateDict[dct['user_id']][dct['date']] = [dct['message']]
            else:
                userDateDict[dct['user_id']] = {'date':{dct['date']}, dct['date']:[dct['message']]}
    myLogger.debug(f'Finish loading user schedual. {userDateDict}')

def new_event(msgDict):
    global myLogger, heartBeatCache, heartBeatCacheLen, errorCount
    global userTimeDict, groupTimeDict, updateTime, processTimeNow
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
        if hakuData.method.csv_check_update(regularComFile):
            load_regular_commands()
        if hakuData.method.csv_check_update(userTimeFile):
            load_user_time_csv()
        if hakuData.method.csv_check_update(groupTimeFile):
            load_group_time_csv()
        if hakuData.method.csv_check_update(userDateFile):
            load_user_date_csv()
        if hakuData.method.csv_check_update(groupDateFile):
            load_group_date_csv()

    # 小时+8
    time_struct = time.gmtime(timeNow + 8 * 3600 + 60) # 下一分钟
    timeFlag = str(time_struct.tm_hour * 100 + time_struct.tm_min)
    dateFlag = str(time_struct.tm_mon * 100 + time_struct.tm_mday)
    groupTimes = dict()
    groupComs = dict()
    userTimes = dict()
    userComs = dict()
    if  timeFlag != processTimeNow:
        processTimeNow = timeFlag
        needSend = False
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
        if timeFlag == '0':
            for grpDctK in groupDateDict.keys():
                if dateFlag in groupDateDict[grpDctK]['date']:
                    if not grpDctK in groupTimes:
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
        if timeFlag == '0':
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
        if groupTimes:
            needSend = True
            myLogger.debug(f'group time: {groupTimes}')
        if groupComs:
            needSend = True
            myLogger.debug(f'group command: {groupComs}')
        if userTimes:
            needSend = True
            myLogger.debug(f'user time: {userTimes}')
        if userComs:
            needSend = True
            myLogger.debug(f'user command: {userComs}')
        if needSend:
            # 等待时机
            newTime_struct = time.gmtime(time.time() + 8 * 3600 + 60) # 下一分钟
            newTimeFlag = str(time_struct.tm_hour * 100 + time_struct.tm_min)
            if newTimeFlag == timeFlag:
                waitSec = 60 - (int(time.time()) % 60) - 1
                if waitSec > 0:
                    myLogger.debug(f'Wait for {waitSec}s')
                    time.sleep(waitSec)
            myLogger.debug('About to send.')
            while int(time.time()) % 60 != 0: pass
            # 发送
            for grp in groupTimes.keys():
                for msg in groupTimes[grp]:
                    hakuCore.cqhttpApi.send_group_msg(grp, msg)
            for usr in userTimes.keys():
                for msg in userTimes[usr]:
                    hakuCore.cqhttpApi.send_private_msg(usr, msg)
            msgEvent = meta_msg_event.copy()
            msgEvent['message_type'] = 'group'
            for grp in groupComs.keys():
                msgEvent['group_id'] = int(grp)
                for msg in groupComs[grp]:
                    msgEvent['message'] = msgEvent['raw_message'] = msg
                    modName = list(msg[1:].split())[0]
                    hakuCore.plugin.run_module(msgEvent, 'message', modName)
            msgEvent['message_type'] = 'private'
            msgEvent['group_id'] = -1
            for usr in userComs.keys():
                msgEvent['user_id'] = int(usr)
                for msg in userComs[usr]:
                    msgEvent['message'] = msgEvent['raw_message'] = msg
                    modName = list(msg[1:].split())[0]
                    hakuCore.plugin.run_module(msgEvent, 'message', modName)

    # 重复指令
    timeNow = time.time()
    msgEvent = meta_msg_event.copy()
    if ADMINQQ > 99999:
        msgEvent['user_id'] = ADMINQQ
        msgEvent['message_type'] = 'private'
    if ADMINGRP > 99999:
        msgEvent['group_id'] = ADMINGRP
        msgEvent['message_type'] = 'group'
    for com in regularComDict.keys():
        if timeNow - regularComDict[com]['last_call'] >= regularComDict[com]['interval']:
            msgEvent['message'] = msgEvent['raw_message'] = regularComDict[com]['message']
            regularComDict[com]['last_call'] = timeNow
            hakuCore.plugin.run_module(msgEvent, 'message', com[1:])

# 数据初始化
load_regular_commands()

load_group_time_csv()
load_group_date_csv()
load_user_time_csv()
load_user_date_csv()
