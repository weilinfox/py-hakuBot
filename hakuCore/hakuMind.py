# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import time, importlib

pluginModules = dict()

def no_such_module(msgDict):
    print('no such module: {}', msgDict[post_type])

def new_event(msgDict):
    global pluginModules
    msgType = msgDict.get('post_type', 'NULL')
    if msgType == 'NULL': return
    mdl = 'hakuRouter.{}'.format(msgType)
    imp = pluginModules.get(mdl, None)
    if imp is None:
        try:
            imp = importlib.import_module('hakuRouter.{}'.format(msgType))
            imp.link_modules(pluginModules)
        except Exception as e:
            print(e)
            no_such_module(msgDict)
        else:
            pluginModules[msgType] = imp
    try:
        imp.new_event(msgDict)
    except Exception as e :
        print(e)

def link_modules(plgs):
    global pluginModules
    pluginModules = plgs

    failedList = []
    print('update plugins')

    #for md in failedList:
        #modules.
        
