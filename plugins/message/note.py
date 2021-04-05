# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

usrDict = dict()

def main (msgDict):
    global usrDict
    req = list(msgDict['raw_message'].split(' ', 1))
    if (len(req) == 1):
        if usrDict.get(msgDict['user_id']):
            return usrDict[msgDict['user_id']]
        else:
            return "log用于简单的备忘，然后你好像没有告诉过小白什么欸~"
    else:
        usrDict[msgDict['user_id']] =  req[1]
        return f"小白记住了：{usrDict[msgDict['user_id']]}"

