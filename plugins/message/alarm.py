

import threading
import hakuData.method

userTimeFile = 'meta_event.user_time_table.csv'
userDateFile = 'meta_event.user_schedual.csv'
groupTimeFile = 'meta_event.group_time_table.csv'
groupDateFile = 'meta_event.group_schedual.csv'

userTimeDict = dict()
userScheDict = dict()
groupTimeDict = dict()
groupScheDict = dict()
userTimeDictAdd = dict()
userScheDictAdd = dict()
groupTimeDictAdd = dict()
groupScheDictAdd = dict()
userTimeDictDel = False
userScheDictDel = False
groupTimeDictDel = False
groupScheDictDel = False
restoreLock = threading.Lock()

for dct in hakuData.method.read_dict_csv_file(userTimeFile, ['user_id', 'time', 'message']):
    if dct['user_id'] in userTimeDict:
        userTimeDict[dct['user_id']].append({'time':dct['time'], 'message':dct['message']})
    else:
        userTimeDict[dct['user_id']] = [{'time':dct['time'], 'message':dct['message']}]
for dct in hakuData.method.read_dict_csv_file(groupTimeFile, ['group_id', 'time', 'message']):
    if dct['group_id'] in groupTimeDict:
        groupTimeDict[dct['group_id']].append({'time':dct['time'], 'message':dct['message']})
    else:
        groupTimeDict[dct['group_id']] = [{'time':dct['time'], 'message':dct['message']}]
for dct in hakuData.method.read_dict_csv_file(userDateFile, ['user_id', 'date', 'message']):
    if dct['user_id'] in userScheDict:
        userScheDict[dct['user_id']].append({'date':dct['date'], 'message':dct['message']})
    else:
        userScheDict[dct['user_id']] = [{'date':dct['date'], 'message':dct['message']}]
for dct in hakuData.method.read_dict_csv_file(groupDateFile, ['group_id', 'date', 'message']):
    if dct['group_id'] in groupScheDict:
        groupScheDict[dct['group_id']].append({'date':dct['date'], 'message':dct['message']})
    else:
        groupScheDict[dct['group_id']] = [{'date':dct['date'], 'message':dct['message']}]

print(userTimeDict)
print(groupTimeDict)
print(userScheDict)
print(groupScheDict)

def main(msgDict):
    msg = list(msgDict['raw_message'].split())
    if len(msg) == 1:
        return '小白的自动提醒设置~'
    retMsg = '''alarm <type> <command>
type: time, date
command: list, add [code] [message], del [line]
line: list命令显示的行号
code: 对于time命令来说如23:05为2305，对于date命令来说11月4日为1104，前导零可省略，小白并不检测其合法性
message: 文字信息，可以包含小白支持的命令
两种type均至多五条'''
    if msgDict['message_type'] == 'private':
        qqid = str(msgDict['user_id'])
        if msg[1] == 'time' and len(msg) > 2:
            if msg[2] == 'list':
                if qqid in userTimeDict:
                    lenth = len(userTimeDict[qqid])
                    retMsg = f'现在小白记录了{lenth}条记录:'
                    if lenth > 5: lenth = 5
                    retMsg += '\ntime message'
                    for i in range(0, lenth):
                        retMsg += f"\n{userTimeDict[qqid][i]['time']} {userTimeDict[qqid][i]['message']}"
                else:
                    retMsg = '小白这里好像没有你的记录欸'
            elif msg[2] == 'add' and len(msg) > 4:
                retMsg = '未开放'
            elif msg[2] == 'del' and len(msg) == 4:
                retMsg = '未开放'
        elif msg[1] == 'date' and len(msg) > 2:
            if msg[2] == 'list':
                if qqid in userScheDict:
                    lenth = len(userScheDict[qqid])
                    retMsg = f'现在小白记录了{lenth}条记录:'
                    if lenth > 5: lenth = 5
                    retMsg += '\ndate message'
                    for i in range(0, lenth):
                        retMsg += f"\n{userScheDict[qqid][i]['date']} {userScheDict[qqid][i]['message']}"
                else:
                    retMsg = '小白这里好像没有你的记录欸'
            elif msg[2] == 'add' and len(msg) > 4:
                retMsg = '未开放'
            elif msg[2] == 'del' and len(msg) == 4:
                retMsg = '未开放'
    elif msgDict['message_type'] == 'group':
        qqid = str(msgDict['group_id'])
        if msg[1] == 'time' and len(msg) > 2:
            if msg[2] == 'list':
                if qqid in groupTimeDict:
                    lenth = len(groupTimeDict[qqid])
                    retMsg = f'现在小白记录了{lenth}条记录:'
                    if lenth > 5: lenth = 5
                    retMsg += '\ntime message'
                    for i in range(0, lenth):
                        retMsg += f"\n{groupTimeDict[qqid][i]['time']} {groupTimeDict[qqid][i]['message']}"
                else:
                    retMsg = '小白这里好像没有你的记录欸'
            elif msg[2] == 'add' and len(msg) > 4:
                retMsg = '未开放'
            elif msg[2] == 'del' and len(msg) == 4:
                retMsg = '未开放'
        elif msg[1] == 'date' and len(msg) > 2:
            if msg[2] == 'list':
                if qqid in groupScheDict:
                    lenth = len(groupScheDict[qqid])
                    retMsg = f'现在小白记录了{lenth}条记录:'
                    if lenth > 5: lenth = 5
                    retMsg += '\ndate message'
                    for i in range(0, lenth):
                        retMsg += f"\n{groupScheDict[qqid][i]['date']} {groupScheDict[qqid][i]['message']}"
                else:
                    retMsg = '小白这里好像没有你的记录欸'
            elif msg[2] == 'add' and len(msg) > 4:
                retMsg = '未开放'
            elif msg[2] == 'del' and len(msg) == 4:
                retMsg = '未开放'
    return retMsg
