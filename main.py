#!/bin/python3
# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import flask
import time, json, importlib, threading, os, traceback
import logging, logging.config
import hakuData.log as hakuLog
import hakuData.method as dataMethod
import hakuData.status as hakuStatus
import hakuCore.hakuMind as callHaku
import hakuCore.cqhttpApi as hakuApi
import hakuCore.plugin as hakuPlg
import hakuCore.report

# 版本
VERSION = 'py-hakuBot v0.0.2'

# 模块记录 用于reload
modules = ('hakuLog', 'hakuStatus', 'dataMethod', 'callHaku', 'hakuApi', 'hakuPlg', 'hakuCore.report')
pluginDict = dict()

# 读取配置
configDict = dataMethod.get_config_dict()
serverConfig = configDict.get('server_config', {})
hakuConfig = configDict.get('haku_config', {})

HOST = serverConfig.get('listen_host', '127.0.0.1')
PORT = serverConfig.get('listen_port', 8000)
POSTURL = serverConfig.get('post_url', '127.0.0.1:8001')
POSTPROTOCOL = 'http'
TOKEN = serverConfig.get('access_token', '')
THREAD = serverConfig.get('threads', False)
PROCESS = serverConfig.get('processes', 1)
LOGLEVEL = serverConfig.get('log_level', 'INFO')
CLOGLEVEL = serverConfig.get('console_log_level', 'INFO')
FLASKLOGLEVEL = 'WARNING'
FLASKCLOGLEVEL = 'WARNING'
FLASKDEBUG = False

ADMINQID = hakuConfig.get('admin_qq', 0)
ADMINGID = hakuConfig.get('admin_group', 0)

# 初始化log
hakuLog.init_log_level(LOGLEVEL, CLOGLEVEL)
hakuLog.init_flack_log_level(FLASKLOGLEVEL, FLASKCLOGLEVEL)
logging.config.dictConfig(hakuLog.logDict)
myLogger = logging.getLogger('hakuBot')
dataMethod.build_logger()
myLogger.info('logger init finished.')

# 线程控制
flaskApp = flask.Flask(__name__)
updateLock = threading.Lock()
threadLock = threading.Lock()
threadDict = dict()
threadCount = 0

# 初始化hakuCore
callHaku.link_modules(pluginDict)
hakuApi.init_api_url(POSTPROTOCOL, POSTURL, TOKEN)
hakuPlg.link_modules(pluginDict)
hakuCore.report.init_report(ADMINQID, ADMINGID)

startTime = time.time()
hakuStatus.regest_router('__main__', {'start_time':startTime})

def clear_threadDict():
    # 清理threadDict
    global threadDict
    popKeys = list()
    for thr in threadDict.keys():
        if not thr.is_alive():
            popKeys.append(thr)
    for thr in popKeys:
        threadDict.pop(thr)

def new_thread(msgDict):
    global updateLock, threadLock, threadDict, threadCount, modules
    # update期间不允许新事件
    # 例行清理
    if updateLock.locked():
        threadCount -= 1
        clear_threadDict()
        if threadLock.locked() and len(threadDict) == 0:
            threadCount = 0
            threadLock.release()
        return
    # 新事件 逻辑
    try:
        retCode = callHaku.new_event(msgDict)
    except:
        myLogger.exception('RuntimeError')
    # 线程记录和锁
    threadCount -= 1
    if (updateLock.locked() and threadCount <= 1) or threadCount < 1:
        if threadLock.locked():
            myLogger.debug('release threadLock')
            threadLock.release()
    clear_threadDict()
    myLogger.debug(f'{threadCount} threads are running currently')

def update_thread():
    global updateLock, threadCount, threadLock
    # 同时只允许一个update线程
    if updateLock.locked():
        threadCount -= 1
        return
    # update锁 期间不允许更多线程进入
    with updateLock:
        myLogger.debug(f'Waiting for {threadCount} threads...')
        # 防止死锁?
        if threadCount == 1 and threadLock.locked():
            threadLock.release()
            myLogger.debug('self release threadLock')
        # update逻辑
        with threadLock:
            myLogger.debug('start update process')
            errMsg1 = ''
            errMsg2 = ''
            errMsg3 = ''
            # 重载主要模块
            for md in modules:
                try:
                    importlib.reload(eval(md))
                except:
                    myLogger.exception('RuntimeError')
                    errMsg1 = traceback.format_exc()
            # 重新初始化module
            callHaku.link_modules(pluginDict)
            hakuLog.init_log_level(LOGLEVEL, CLOGLEVEL)
            hakuLog.init_flack_log_level(FLASKLOGLEVEL, FLASKCLOGLEVEL)
            dataMethod.build_logger()
            hakuApi.init_api_url(POSTPROTOCOL, POSTURL, TOKEN)
            hakuPlg.link_modules(pluginDict)
            hakuCore.report.init_report(ADMINQID, ADMINGID)
            hakuStatus.regest_router('__main__', {'start_time':startTime})
            # 重载插件
            delPlugin = list()
            for md in pluginDict.keys():
                if 'quit_plugin' in dir(pluginDict[md]):
                    try:
                        myLogger.debug(f'Try to run {md}.quit_plugin')
                        #eval(md + '.quit_plugin')()
                        pluginDict[md].quit_plugin()
                    except:
                        myLogger.exception('RuntimeError')
                        errMsg2 = traceback.format_exc()
                try:
                    myLogger.debug(f'Reload {md}')
                    pluginDict[md] = importlib.reload(pluginDict[md])
                except ModuleNotFoundError:
                    myLogger.debug(f'Find one plugin deleted during update: {md}')
                    delPlugin.append(md)
                except:
                    myLogger.exception('RuntimeError')
                    errMsg3 = traceback.format_exc()
            # 错误上报
            if errMsg1:
                hakuCore.report.report('Error occored while reloading module:')
                hakuCore.report.report(errMsg1)
            if errMsg2:
                hakuCore.report.report('Error occored while quit plugin:')
                hakuCore.report.report(errMsg2)
            if errMsg3:
                hakuCore.report.report('Error occored while reloading plugin:')
                hakuCore.report.report(errMsg3)
            # 删除不存在的plugin
            for md in delPlugin:
                pluginDict.pop(md)
    threadCount -= 1

# 事件触发
@flaskApp.route('/', methods=['POST'])
def newMsg():
    global threadDict, threadCount, threadLock
    try:
        msgDict = flask.request.get_json()
    except:
        myLogger.exception('RuntimeError')
    else:
        if threadCount == 0: threadLock.acquire()
        threadCount += 1
        newThread = threading.Thread(target=new_thread, args=[msgDict], daemon=True)
        threadDict[newThread] = time.time()
        newThread.start()
    return ''

# update触发
@flaskApp.route('/UPDATE', methods=['POST', 'GET'])
def updateMsg():
    global threadDict, threadCount
    threadCount += 1
    newThread = threading.Thread(target=update_thread, args=[], daemon=True)
    threadDict[newThread] = time.time()
    newThread.start()
    return ''

@flaskApp.route('/VERSION', methods=['POST', 'GET'])
def versionMsg():
    return VERSION

# 运行flask
if __name__ == "__main__":
    flaskApp.run(host=HOST, port=PORT, debug=FLASKDEBUG, threaded=THREAD, processes=PROCESS)
