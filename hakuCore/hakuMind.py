# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import time, importlib
import logging

pluginModules = dict()
myLogger = logging.getLogger('hakuBot')

def no_such_module(msgDict):
    global myLogger
    myLogger.warning('No such router: {}'.format(msgDict['post_type']))

def new_event(msgDict):
    global pluginModules, myLogger
    msgType = msgDict.get('post_type', 'NULL')
    if msgType == 'NULL': return
    mdl = 'hakuRouter.{}'.format(msgType)
    imp = pluginModules.get(mdl, None)
    if imp is None:
        try:
            imp = importlib.import_module('hakuRouter.{}'.format(msgType))
            imp.link_modules(pluginModules)
        except ModuleNotFoundError:
            no_such_module(msgDict)
        except:
            myLogger.exception('RuntimeError')
        else:
            pluginModules[msgType] = imp
    try:
        imp.new_event(msgDict)
    except:
        myLogger.exception('RuntimeError')

def link_modules(plgs):
    global pluginModules
    pluginModules = plgs

