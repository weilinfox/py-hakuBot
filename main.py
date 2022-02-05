#!/bin/python3
# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE
"""
hakuBot 主程序
"""

import flask
import time
import json
import importlib
import threading
import os
import traceback
import random
import logging.config
import haku_data.log as haku_log
import haku_data.method as data_method
import haku_data.status as haku_status
import haku_core.haku_mind as call_haku
import haku_core.api_cqhttp as cqhttp_api
import haku_core.plugin as haku_plugin
import haku_core.report

if os.name == 'posix':
    import signal

# 版本
VERSION = 'py-hakuBot v0.0.5'

# 模块记录 用于reload
modules = (haku_log, haku_status, data_method, call_haku, cqhttp_api, haku_plugin, haku_core.report)
pluginDict = dict()

# 读取配置
configDict = data_method.get_config_dict()
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
haku_log.init_log_level(LOGLEVEL, CLOGLEVEL)
haku_log.init_flack_log_level(FLASKLOGLEVEL, FLASKCLOGLEVEL)
# 这里强制设置 由于一直无效
FLASKLOGGER.setLevel(logging.WARNING)
logging.config.dictConfig(haku_log.get_log_dict())
myLogger = logging.getLogger('hakuBot')
data_method.build_logger()
myLogger.info('logger init finished.')

# 线程控制
flaskApp = flask.Flask(__name__)
updateLock = threading.Lock()
threadLock = threading.Lock()
threadIdList = []
threadDict = {}
threadCount = 0

hakupid = os.getpid()

# 初始化hakuCore
call_haku.link_modules(pluginDict)
cqhttp_api.init_api_url(POSTPROTOCOL, POSTURL, TOKEN)
haku_plugin.link_modules(pluginDict)
haku_core.report.init_report(ADMINQID, ADMINGID)

startTime = time.time()
haku_status.regest_router('__main__', {'start_time': startTime})


def get_thread_id():
    """
    获取新 thread id
    :return: int
    """
    global threadIdList
    while True:
        nid = random.random()
        threadIdList.append(nid)
        if threadIdList.count(nid) > 1:
            threadIdList.remove(nid)
            continue
        return nid


def save_thread_id(thread, nid):
    """
    将 thread id 保存在 threadDict 中构成 id: thread object 键值对
    :param thread: thread 对象
    :param nid: thread id
    :return: 无返回值
    """
    global threadIdList, threadDict, threadCount, threadLock
    if threadCount == 0:
        threadLock.acquire()
    threadDict[nid] = thread
    threadCount += 1


def del_thread_id(nid):
    """
    删除一个 thread id ，此时该 thread 应当已经停止
    :param nid: thread id
    :return: 无返回值
    """
    global threadIdList, threadDict, threadCount, threadLock
    threadDict.pop(nid)
    threadIdList.remove(nid)
    threadCount -= 1
    if threadCount == 0:
        threadLock.release()


def clear_thread_id():
    """
    从 threadDict 清除异常退出的 thread id
    :return: 无返回值
    """
    global threadDict, threadIdList
    popkeys = list()
    for nid in threadDict.keys():
        if not threadDict[nid].is_alive():
            popkeys.append(nid)
    for nid in popkeys:
        del_thread_id(nid)


def haku_start():
    """
    启动 hakubot flask 服务器 程序将在这里阻塞
    :return: 无返回值
    """
    flaskApp.run(host=HOST, port=PORT, debug=FLASKDEBUG, threaded=THREAD, processes=PROCESS)


def new_thread(msgdict, nid):
    """
    处理新消息请求
    :param msgdict: cqhttp message dictionary
    :param nid: thread id
    :return: 无返回值
    """
    global updateLock, threadLock, threadDict, threadCount, modules, threadIdList
    # update期间不允许新事件
    if updateLock.locked():
        del_thread_id(nid)
        # 清理
        clear_thread_id()
        return
    # 新事件 逻辑
    try:
        retcode = call_haku.new_event(msgdict)
    except:
        myLogger.exception('RuntimeError')
    # 线程记录和锁
    del_thread_id(nid)
    myLogger.debug(f'{threadCount} thread(s) is/are running currently')


def update_thread():
    """
    处理模块重载请求
    :return: 无返回值
    """
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
            errmsg1 = ''
            errmsg2 = ''
            errmsg3 = ''
            # 重载主要模块
            for md in modules:
                try:
                    importlib.reload(md)
                except:
                    myLogger.exception('RuntimeError')
                    errmsg1 = traceback.format_exc()
            # 重新初始化module
            call_haku.link_modules(pluginDict)
            haku_log.init_log_level(LOGLEVEL, CLOGLEVEL)
            haku_log.init_flack_log_level(FLASKLOGLEVEL, FLASKCLOGLEVEL)
            data_method.build_logger()
            cqhttp_api.init_api_url(POSTPROTOCOL, POSTURL, TOKEN)
            haku_plugin.link_modules(pluginDict)
            haku_core.report.init_report(ADMINQID, ADMINGID)
            haku_status.regest_router('__main__', {'start_time': startTime})
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
                        errmsg2 = traceback.format_exc()
                try:
                    myLogger.debug(f'Reload {md}')
                    pluginDict[md] = importlib.reload(pluginDict[md])
                except ModuleNotFoundError:
                    myLogger.debug(f'Find one plugin deleted during update: {md}')
                    delPlugin.append(md)
                except:
                    myLogger.exception('RuntimeError')
                    errmsg3 = traceback.format_exc()
            # 错误上报
            if errmsg1:
                haku_core.report.report('Error occored while reloading module:')
                haku_core.report.report(errmsg1)
            if errmsg2:
                haku_core.report.report('Error occored while quit plugin:')
                haku_core.report.report(errmsg2)
            if errmsg3:
                haku_core.report.report('Error occored while reloading plugin:')
                haku_core.report.report(errmsg3)
            # 删除不存在的plugin
            for md in delPlugin:
                pluginDict.pop(md)


def terminate_thread():
    """
    处理服务停止请求
    :return: 无返回值
    """
    global updateLock, threadLock
    time.sleep(0.5)
    myLogger.warning('Loading terminate process...')
    with updateLock:
        myLogger.warning(f'Waiting for {threadCount} threads...')
        waitime = 0
        while threadLock.locked():
            if waitime > 600:
                myLogger.error('Timeout after 600 seconds, force stop now.')
                break
            clear_thread_id()
            waitime = waitime + 5
            time.sleep(5)
        # terminate 逻辑
        myLogger.warning('Start to terminate...')
        for md in pluginDict.keys():
            if 'quit_plugin' in dir(pluginDict[md]):
                try:
                    myLogger.info(f'Running {md}.quit_plugin...')
                    pluginDict[md].quit_plugin()
                except:
                    myLogger.exception('RuntimeError')
        try:
            if os.name == 'posix':
                os.kill(hakupid, signal.SIGINT)
                os.kill(hakupid, signal.SIGINT)
            else:
                os.popen(f'taskkill.exe /PID {hakupid} /F')
        except:
            myLogger.exception('RuntimeError')


# 事件触发
@flaskApp.route('/', methods=['POST'])
def new_message():
    """
    新 cqhttp 消息
    :return: 空字符串
    """
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
def update_message():
    """
    新 update 请求
    :return: 空字符串
    """
    newThread = threading.Thread(target=update_thread, args=[], daemon=True)
    newThread.start()
    return ''


@flaskApp.route('/VERSION', methods=['POST', 'GET'])
def version_message():
    """
    获取 main.py 版本
    :return: 格式化后的版本号字串
    """
    return VERSION


@flaskApp.route('/THREADS', methods=['POST', 'GET'])
def thread_message():
    """
    获取当前子线程状态
    :return: 格式化后的子线程状态字串
    """
    onupdate = 0
    if updateLock.locked():
        onupdate = 1
    msg = f'Totalthread: {threadCount+onupdate}\nLen of threadIdList: {len(threadIdList)}'
    for key in threadDict:
        msg += f'\n{key}: {threadDict[key].ident}'
    if onupdate:
        msg += f'\nUpdate thread is running.'
    return msg


@flaskApp.route('/STATUS', methods=['GET'])
def status_message():
    """
    从 haku_data/status.py 读取状态
    :return: 格式化后的状态字串
    """
    nm = flask.request.args.get('name', '')
    if nm:
        dct, tm = haku_status.get_status(nm)
        return json.dumps({'message': dct, 'time': tm})
    else:
        return json.dumps({'message': 'invalid args', 'time': int(time.time())})


@flaskApp.route('/STOP', methods=['GET'])
def flask_terminate():
    """
    停止 flask 服务器
    :return: 空字符串
    """
    thr = threading.Thread(target=terminate_thread, args=[], daemon=True)
    thr.start()
    return ''


# 运行flask
if __name__ == "__main__":
    print(__name__)
    haku_start()
