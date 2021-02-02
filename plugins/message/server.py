# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import hakuData.status
import time

def main(msgDict):
    msgList = list(msgDict['message'].split())
    timeNow = time.time()
    if len(msgList) < 2:
        ans = 'Read haku-manager data.'
        statusDict, refreshTime = hakuData.status.get_status('haku-manager')
        if statusDict:
            ans += '\n在线列表如下:'
            print(statusDict)
            for s in statusDict['status'].keys():
                if timeNow - statusDict['status'][s]['time'] > 30.0:
                    continue
                ans += f'\n{s}'
            ans += f"\n上报错误总计: {statusDict['errors']}"
        else:
            ans += '\n没有查询到 haku-manager 的信息'
    else:
        serverName = msgList[1]
        statusDict, refreshTime = hakuData.status.get_status('haku-manager')
        if statusDict:
            if (serverName in statusDict['status']) and statusDict['status'][serverName]['status']:
                myDict = statusDict['status'][serverName].copy()
                ans = f'''查询到{serverName}最近的记录
在 {int(timeNow-myDict['time'])}s 之前
uptime: {myDict['status']['time']['uptime']}
-temperature-
cpu temp: {myDict['status']['temp']['cpu_temp']}
sys temp: {myDict['status']['temp']['sys_temp']}
fan status: {myDict['status']['temp']['fan_status']}
-cpu info-
cpu cores: {myDict['status']['cpu']['cpu_cores']}
load average: {myDict['status']['cpu']['load_average']}
wa: {myDict['status']['cpu']['wa']}
-disk info-
bi: {myDict['status']['disk']['bi']}
bo: {myDict['status']['disk']['bo']}
-memory info-
free: {myDict['status']['memory']['free']/1024} MB
buff: {myDict['status']['memory']['buff']/1024} MB
cache: {myDict['status']['memory']['cache']/1024} MB
-swap info-
si: {myDict['status']['swap']['si']}
so: {myDict['status']['swap']['so']}
-process info-
r: {myDict['status']['process']['r']}
b: {myDict['status']['process']['b']}
-net info-
card bytes packets errors drops'''
                for k in myDict['status']['net'].keys():
                    ans += f"\n{k} {myDict['status']['net'][k]['bytes']} {myDict['status']['net'][k]['packets']} {myDict['status']['net'][k]['errors']} {myDict['status']['net'][k]['drops']}"
            else:
                ans = f'没有查询到 {serverName} 的信息'
        else:
            ans = '没有查询到 haku-manager 的信息'

    return ans
