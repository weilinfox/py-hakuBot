# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import flask
import time, json, importlib, threading
import hakuData.method as dataMethod
import hakuCore.hakuMind as callHaku

modules = {'dataMethod', 'callHaku'}
pluginDict = dict()

configFile = open(dataMethod.get_config_json(), "r")
configDict = json.loads(configFile.read())
configFile.close()
serverConfig = configDict.get('server_config', {})
hakuConfig = configDict.get('haku_config', {})

HOST = serverConfig.get('listen_host', '127.0.0.1')
PORT = serverConfig.get('listen_port', 8000)
THREAD = serverConfig.get('threads', False)
PROCESS = serverConfig.get('processes', 1)
FLASKDEBUG = False

app = flask.Flask(__name__)
updateLock = threading.Lock()
threadLock = threading.Lock()
threadDict = dict()
threadCount = 0

def clear_threadDict():
    global threadDict
    popKeys = list()
    for thr in threadDict.keys():
        if not thr.is_alive():
            popKeys.append(thr)
    for thr in popKeys:
        threadDict.pop(thr)

def new_thread(msgDict):
    global updateLock, threadLock, threadDict, threadCount, modules
    if updateLock.locked():
        threadCount -= 1
        clear_threadDict()
        if threadLock.locked() and len(threadDict) == 0:
            threadCount = 0
            threadLock.release()
        return
    try:
        retCode = callHaku.new_event(msgDict)
    except Exception as e:
        print(e)
    threadCount -= 1
    if (updateLock.locked() and threadCount <= 1) or threadCount < 1:
        if threadLock.locked():
            print('release threadLock')
            threadLock.release()
    clear_threadDict()

def update_thread():
    global updateLock, threadCount, threadLock
    if updateLock.locked(): return
    with updateLock:
        print('wait for threads')
        if threadLock.locked() and threadCount == 1:
            print('self release threadLock')
            threadLock.release()
        with threadLock:
            print('start update process')
            for md in modules:
                try:
                    importlib.reload(eval(md))
                except Exception as e:
                    print(e)

    callHaku.link_modules(pluginDict)
    for md in pluginDict.keys():
        if 'quit_plugin' in dir(pluginDict[md]):
            try:
                eval(md + 'quit_plugin')()
            except Exception as e:
                print(e)
        try:
            pluginDict[md] = importlib.reload(pluginDict[md])
        except Exception as e:
            print(e)
        else:
            # 一级插件
            if not '.' in md:
                pluginDict[md].link_modules(pluginDict)
    threadCount -= 1


@app.route('/', methods=['POST'])
def newMsg():
    global threadDict, threadCount, threadLock
    try:
        msgDict = flask.request.get_json()
    except Exception as e:
        print(e)
    else:
        if threadCount == 0: threadLock.acquire()
        threadCount += 1
        newThread = threading.Thread(target=new_thread, args=[msgDict], daemon=True)
        threadDict[newThread] = time.time()
        newThread.start()
    return ''

@app.route('/UPDATE', methods=['POST', 'GET'])
def updateMsg():
    global threadDict, threadCount
    threadCount += 1
    newThread = threading.Thread(target=update_thread, args=[], daemon=True)
    threadDict[newThread] = time.time()
    newThread.start()
    return ''

callHaku.link_modules(pluginDict)
app.run(host=HOST, port=PORT, debug=FLASKDEBUG, threaded=THREAD, processes=PROCESS)
