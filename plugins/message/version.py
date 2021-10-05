# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import requests
import hakuData.method
import hakuCore.cqhttpApi

configDict = hakuData.method.get_config_dict()
serverConfig = configDict.get('server_config', {})
hakuConfig = configDict.get('haku_config', {})

PORT = serverConfig.get('listen_port', 8000)
PATH = hakuData.method.get_main_path()

def main(msgDict):
    resp = requests.get(url=f'http://127.0.0.1:{PORT}/VERSION', params={}, timeout=5)
    if resp.status_code == 200:
        hakuBotVer = resp.text
    else:
        hakuBotVer = '获取版本号失败'
    return f'小白哦~\n{hakuBotVer}'
