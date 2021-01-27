# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import subprocess, requests
import hakuData.method
import hakuCore.cqhttpApi

configDict = hakuData.method.get_config_dict()
serverConfig = configDict.get('server_config', {})
hakuConfig = configDict.get('haku_config', {})

PORT = serverConfig.get('listen_port', 8000)
PATH = hakuData.method.get_main_path()

def main(msgDict):
    output = subprocess.getoutput(f'cd {PATH} && git pull')
    rep = requests.get(url=f'http://127.0.0.1:{PORT}/UPDATE', params={})
    return f'{output}\n{rep.status_code}'
