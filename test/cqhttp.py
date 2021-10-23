#!/bin/python3
# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE
"""
测试用伪 cqhttp 服务器
"""
import time

import flask
import threading
import logging
import os

if os.name == 'posix':
    import signal

VERSION = 'v0.0.1'
HOST = '127.0.0.1'
PORT = 8000
flaskApp = flask.Flask('test_cqhttp')
mypid = os.getpid()

mylogger = logging.getLogger('hakuBot')


def cqhttp_init(host, port):
    """
    初始化参数
    :param host: 监听 host
    :param port: 监听 port
    :return: 无返回值
    """
    global HOST, PORT
    HOST = host
    PORT = port


def cqhttp_start():
    """
    启动 cqhttp flask 服务器 程序将在这里阻塞
    :return: 无返回值
    """
    flaskApp.run(host=HOST, port=PORT, debug=False, threaded=True, processes=1)


def cqhttp_stop():
    """
    停止 cqhttp flask 服务器
    :return: 无返回值
    """
    time.sleep(0.5)
    mylogger.warning('Start to terminate cqhttp...')
    if os.name == 'posix':
        os.kill(mypid, signal.SIGINT)
        os.kill(mypid, signal.SIGINT)
    else:
        os.popen(f'taskkill.exe /PID {mypid} /T')


@flaskApp.route('/<path>', methods=['GET', 'POST'])
def flask_message(path):
    """
    新消息
    """
    print(f'{flask.request.method} /{path}')
    if path == 'VERSION':
        return VERSION
    elif path == 'STOP':
        mylogger.warning('Stop test cqhttp now.')
        thr = threading.Thread(target=cqhttp_stop, args=[], daemon=True)
        thr.start()
        return ''

    print(flask.request.args)
    return flask.jsonify({'retcode': 200, 'data': 'Success'})

