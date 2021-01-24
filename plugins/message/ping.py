# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import logging
myLogger = logging.getLogger('hakuBot')

myLogger.info('Load ping plugin.')

def main(msgDict):
    return 'Pong!'

def quit_plugin():
    myLogger.info('Quit ping plugin.')
