# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import time, importlib
import logging

pluginModules = dict()
myLogger = logging.getLogger('hakuBot')


def new_event(msgDict):
    global pluginModules, myLogger
    msgType = msgDict.get('post_type', 'NULL')
    if msgType == 'NULL':
        myLogger.warning(f'Catch inlegal event: {msgDict}')
        return
    myLogger.debug(f'Catch new event, message type: {msgType}')
    mdl = 'hakuRouter.{}'.format(msgType)
    imp = pluginModules.get(mdl, None)
    if imp is None:
        try:
            imp = importlib.import_module('hakuRouter.{}'.format(msgType))
            myLogger.debug(f'Load new router: {msgType}')
        except ModuleNotFoundError:
            myLogger.warning('No such router: {}'.format(msgDict['post_type']))
        except:
            myLogger.exception('RuntimeError')
        else:
            pluginModules['hakuRouter.{}'.format(msgType)] = imp
    else:
        myLogger.debug(f'Reuse router: {msgType}')
    if imp:
        try:
            imp.new_event(msgDict)
        except:
            myLogger.exception('RuntimeError')


def link_modules(plgs):
    global pluginModules
    pluginModules = plgs

