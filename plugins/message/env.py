# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import haku_data.status
import time

def main(msgDict):
    msgList = list(msgDict['message'].split())
    timeNow = time.time()
    if len(msgList) < 2:
        ans = 'Read haku-manager data.'
        statusDict, refreshTime = haku_data.status.get_status('haku-manager')
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
        statusDict, refreshTime = haku_data.status.get_status('haku-manager')
        if statusDict:
            if (serverName in statusDict['status']) and statusDict['status'][serverName]['status']:
                myDict = statusDict['status'][serverName].copy()
                if 'env_data' in myDict['status'].keys():
                    ans = f'''查询到{serverName}最近的环境记录
在 {int(timeNow-myDict['time'])}s 之前
env data dict:
{myDict['status']['env_data']}'''
                else:
                    ans = f'{serverName} 没有环境检测功能'
            else:
                ans = f'没有查询到 {serverName} 的信息'
        else:
            ans = '没有查询到 haku-manager 的信息'

    return ans
