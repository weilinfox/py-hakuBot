# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import logging

myLogger = logging.getLogger('hakuBot')
pluginModules = dict()

def new_event(msgDict):
    global myLogger
    myLogger.info('call meta event')

def link_modules(plgs):
    global pluginModules
    pluginModules = plgs
