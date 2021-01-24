# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import time
import logging

myLogger = logging.getLogger('hakuBot')

statusDict = dict()
refreshTime = dict()

def regest_router(routerName, initDict):
    global statusDict, refreshTime
    myLogger.debug(f'{routerName} regested with dict {initDict}')
    statusDict[routerName] = initDict
    refreshTime[routerName] = time.time()

def refresh_status(routerName, newDict):
    global statusDict, refreshTime
    myLogger.debug(f'{routerName} refreshed with dict {newDict}')
    statusDict[routerName] = newDict
    refreshTime[routerName] = time.time()

def get_status(routerName):
    return statusDict.get(routerName, {}), refreshTime.get(routerName, 0)
