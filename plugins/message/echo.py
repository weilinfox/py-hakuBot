# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import random

def main (msgDict):
    helpMsg = '''人类本质的一个实现～
由于不可告人的原因，过长的字段会被截断，包含中括号和大括号的字段可能复读失败
qaq'''
    req = list(msgDict['raw_message'].split(' ', 1))
    if (len(req) > 1 and req[1].strip() == 'help'):
        return helpMsg
    elif len(req) == 1 or (len(req) > 1 and len(req[1].strip()) == 0):
        return '好像心里空空的…'
    elif req[1].count('狗'):
        return '小白是狐不是狗!'
    else:
        ans = random.randint(0, 5)
        respond = ''
        if ans == 0:
            respond = '汝不会念嘛~\n' + req[1]
        elif ans == 1:
            respond = '小白是不会逃避的!\n' + req[1]
        else:
            respond = req[1]
        return respond
