#!/bin/python3
# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import flask
import time, json, importlib, threading, os, traceback, random
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
FLASKLOGLEVEL = 'ERROR'
FLASKCLOGLEVEL = 'ERROR'
FLASKLOGGER = logging.getLogger('werkzeug')
FLASKDEBUG = False

ADMINQID = hakuConfig.get('admin_qq', 0)
ADMINGID = hakuConfig.get('admin_group', 0)

# 初始化log
hakuLog.init_log_level(LOGLEVEL, CLOGLEVEL)
hakuLog.init_flack_log_level(FLASKLOGLEVEL, FLASKCLOGLEVEL)
# 这里强制设置 由于一直无效
FLASKLOGGER.setLevel(logging.WARNING)
logging.config.dictConfig(hakuLog.logDict)
myLogger = logging.getLogger('hakuBot')
dataMethod.build_logger()
myLogger.info('logger init finished.')

# 线程控制
flaskApp = flask.Flask(__name__)
updateLock = threading.Lock()
threadLock = threading.Lock()
threadIdList = []
threadDict = {}
threadCount = 0

# 初始化hakuCore
callHaku.link_modules(pluginDict)
hakuApi.init_api_url(POSTPROTOCOL, POSTURL, TOKEN)
hakuPlg.link_modules(pluginDict)
hakuCore.report.init_report(ADMINQID, ADMINGID)

startTime = time.time()
hakuStatus.regest_router('__main__', {'start_time': startTime})


def get_thread_id():
    # 获取新thread id
    global threadIdList
    while True:
        newId = random.random()
        threadIdList.append(newId)
        if threadIdList.count(newId) > 1:
            threadIdList.remove(newId)
            continue
        return newId


def save_thread_id(thrObj, nid):
    global threadIdList, threadDict, threadCount, threadLock
    if threadCount == 0:
        threadLock.acquire()
    threadDict[nid] = thrObj
    threadCount += 1


def del_thread_id(nid):
    global threadIdList, threadDict, threadCount, threadLock
    threadDict.pop(nid)
    threadIdList.remove(nid)
    threadCount -= 1
    if threadCount == 0:
        threadLock.release()


def clear_thread_id():
    # 清理threadDict
    global threadDict, threadIdList
    popKeys = list()
    for nid in threadDict.keys():
        if not threadDict[nid].is_alive():
            popKeys.append(nid)
    for nid in popKeys:
        del_thread_id(nid)


def new_thread(msgDict, nid):
    global updateLock, threadLock, threadDict, threadCount, modules, threadIdList
    # update期间不允许新事件
    if updateLock.locked():
        del_thread_id(nid)
        # 清理
        clear_thread_id()
        return
    # 新事件 逻辑
    try:
        retCode = callHaku.new_event(msgDict)
    except:
        myLogger.exception('RuntimeError')
    # 线程记录和锁
    del_thread_id(nid)
    myLogger.debug(f'{threadCount} thread(s) is/are running currently')


def update_thread():
    global updateLock, threadCount, threadLock
    # 同时只允许一个update线程
    if updateLock.locked():
        return
    # update锁 期间不允许更多线程进入
    with updateLock:
        myLogger.debug(f'Waiting for {threadCount} threads...')
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
            hakuStatus.regest_router('__main__', {'start_time': startTime})
            # 重载插件
            delPlugin = list()
            for md in pluginDict.keys():
                if 'quit_plugin' in dir(pluginDict[md]):
                    try:
                        myLogger.debug(f'Try to run {md}.quit_plugin')
                        # eval(md + '.quit_plugin')()
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


# 事件触发
@flaskApp.route('/', methods=['POST'])
def newMsg():
    global threadDict, threadCount, threadLock
    try:
        msgDict = flask.request.get_json()
    except:
        myLogger.exception('RuntimeError')
    else:
        nid = get_thread_id()
        newThread = threading.Thread(target=new_thread, args=[msgDict, nid], daemon=True)
        save_thread_id(newThread, nid)
        newThread.start()
    return ''


# update触发
@flaskApp.route('/UPDATE', methods=['POST', 'GET'])
def updateMsg():
    newThread = threading.Thread(target=update_thread, args=[], daemon=True)
    newThread.start()
    return ''


@flaskApp.route('/VERSION', methods=['POST', 'GET'])
def versionMsg():
    return VERSION


@flaskApp.route('/THREADS', methods=['POST', 'GET'])
def threadMsg():
    msg = f'threadCount: {threadCount}\nLen of threadIdList: {len(threadIdList)}'
    for key in threadDict:
        msg += f'\n{key}: {threadDict[key].ident}'
    return msg


@flaskApp.route('/STATUS', methods=['GET'])
def statusMsg():
    nm = flask.request.args.get('name', '')
    if nm:
        dct, tm = hakuStatus.get_status(nm)
        return json.dumps({'message': dct, 'time': tm})
    else:
        return json.dumps({'message': 'invalid args', 'time': int(time.time())})


# 运行flask
if __name__ == "__main__":
    flaskApp.run(host=HOST, port=PORT, debug=FLASKDEBUG, threaded=THREAD, processes=PROCESS)
