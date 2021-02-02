# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import logging, time, threading
import hakuCore.cqhttpApi
import hakuData.method

configDict = hakuData.method.get_config_dict()
serverConfig = configDict.get('server_config', {})
hakuConfig = configDict.get('haku_config', {})

INDEX = hakuConfig.get('index', '.')

def new_event(msgDict):
    if msgDict['notice_type'] == 'group_increase':
        greetMsg = f'欢迎欢迎，进了群就是一家人了~\n{INDEX}help 查看给小白的指示哦'
        hakuCore.cqhttpApi.send_group_msg(msgDict['group_id'], '[CQ:at,qq=' + str(msgDict['user_id']) + ']\n' + greetMsg)
    elif msgDict['notice_type'] == 'lucky_king':
        greatMsg = '运气王出现了'
        hakuCore.cqhttpApi.send_group_msg(msgDict['group_id'], '[CQ:at,qq=' + str(msgDict['target_id']) + ']\n' + greetMsg)
