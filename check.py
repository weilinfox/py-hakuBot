#!/bin/python3
# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import flask, logging
import time, json, importlib, threading, os, traceback, random
import sys, getopt, os, requests, json, re

HOST = '0.0.0.0'
PORT = 8002
THREAD = False
PROCESS = 1
FLASKDEBUG = False
FLASKLOGGER = logging.getLogger('werkzeug')
FLASKLOGGER.setLevel(logging.WARNING)

flaskApp = flask.Flask(__name__)

configFile = os.path.normpath(os.path.dirname(os.path.abspath(__file__))) + '/files/config.json'
print(f'Load config file: {configFile}')
port = 0
if os.path.exists(configFile):
    with open(configFile, 'r') as conFile:
        try:
            configJson = json.loads(conFile.read()).get('server_config', {})
        except:
            print('Load hakuBot config file failed.')
        else:
            port = configJson.get('listen_port', 0)
    if not port:
        print('Get hakuBot listen port failed.')
        exit(1)
else:
    print('Cannot find hakuBot config file.')
    exit(1)
print(f'Opration will be send to host: 127.0.0.1:{port}')

def check(name):
    if len(name) > 64:
        return {'code': 400, "message": 'Request name too long.'}
    try:
        mt = re.match(r'[\d\w-]+', name)
        if not mt or name != mt.group(0):
            return {'code': 400, 'message': 'Request name check failed.'}
    except Exception as e:
        print(e)
        return {'code': 500, 'message': e}

    resjson = dict()
    try:
        resjson = requests.get(url=f'http://127.0.0.1:{port}/STATUS', params={'name':name}, timeout=(1,2)).json()
    except Exception as e:
        print(e)
        return {'code':400, 'message':'Request failed.'}

    return {'code': 200, 'message': resjson}

# 事件触发
@flaskApp.route('/STATUS', methods=['GET'])
def statusMsg():
    nm = flask.request.args.get('name', '')
    res = flask.make_response(flask.jsonify(check(nm)))
    res.headers['Access-Control-Allow-Origin'] = "*"
    res.headers['Access-Control-Allow-Methods'] = 'GET'
    return res

# 运行flask
if __name__ == "__main__":
    flaskApp.run(host=HOST, port=PORT, debug=FLASKDEBUG, threaded=THREAD, processes=PROCESS)
