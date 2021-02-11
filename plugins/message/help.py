# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import hakuData.method

configDict = hakuData.method.get_config_dict()
serverConfig = configDict.get('server_config', {})
hakuConfig = configDict.get('haku_config', {})

INDEX = hakuConfig.get('index', '.')

def main(msgDict):
    msgList = list(msgDict['message'].split())
    ans = f'''指令前缀 {INDEX}
usage: help [options]
    0  通用指令
    1  状态指令'''

    if len(msgList) > 1:
        try:
            code = int(msgList[1])
            if code == 0:
                ans = '''通用指令:
alarm
baidu
bc
bing
bingFull
echo
forecast
music
qqmusic
run
weather
wttrin
wyy
yiyan'''
            elif code == 1:
                ans = '''状态指令:
ping
server
status
time
update
version'''
            else:
                ans = '参数非法\n\n' + ans
        except:
            ans = '参数非法\n\n' + ans

    return ans

