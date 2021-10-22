# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE
"""
notice 配置
自定义入群欢迎
设置 入群欢迎 notice 功能 pastebin 上传 打开与关闭
"""

import hakuRouter.notice as notice
import hakuData.method

configDict = hakuData.method.get_config_dict()
serverConfig = configDict.get('server_config', {})
hakuConfig = configDict.get('haku_config', {})

INDEX = hakuConfig.get('index', '.')
ADMINQID = hakuConfig.get('admin_qq', 0)
ADMINGID = hakuConfig.get('admin_group', 0)


def handle_help():
    return f'''notice 配置
{INDEX}notice [greet msg | on fun | off fun | show fun] [gid]
greet msg:      自定义入群欢迎消息
on fun:         打开功能
off fun:        关闭功能
show fun:       显示功能状态

fun:
    greet:      入群欢迎
    pb:         群新文件自动 pb 上传
    notice:     整个 notice 功能
gid:
    操作的群号，默认当前群，指定群需要 bot 管理权限
'''


def handle_greet(gid, msg):
    if notice.notice_update_greetmsg(gid, msg):
        return f'更新成功: {msg}'
    else:
        return '更新失败'


def handle_on(gid, fun):
    if notice.notice_update_block(gid, fun, True):
        return '更新成功'
    else:
        return '更新失败'


def handle_off(gid, fun):
    if notice.notice_update_block(gid, fun, False):
        return '更新成功'
    else:
        return '更新失败'


def handle_show(gid, fun):
    flag = '关闭' if notice.notice_check_block(gid, fun) else '打开'
    msg = f'状态: {flag}'
    if fun == 'greet':
        msg = f'{msg}: {notice.notice_get_greet(gid)}'
    return msg


def main(msgDict):
    com = msgDict['message'].split()
    if len(com) <= 2:
        return handle_help()
    else:
        if msgDict['message_type'] == 'group':
            gid = msgDict['group_id']
            isadmin = ADMINQID == msgDict['user_id'] or ADMINGID == gid
        else:
            gid = 0
            isadmin = ADMINQID == msgDict['user_id']
        if isadmin:
            try: gid = int(com[3])
            except: pass
        if not gid:
            return '不被支持的私聊配置'

        if com[1] == 'greet':
            return handle_greet(gid, com[2])
        elif com[1] == 'on':
            return handle_on(gid, com[2])
        elif com[1] == 'off':
            return handle_off(gid, com[2])
        elif com[1] == 'show':
            return handle_show(gid, com[2])
        else:
            return f'非法命令: {com[1]}'
