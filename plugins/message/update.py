# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import subprocess, requests, time
import hakuData.method
import hakuCore.cqhttpApi

configDict = hakuData.method.get_config_dict()
serverConfig = configDict.get('server_config', {})
hakuConfig = configDict.get('haku_config', {})

PORT = serverConfig.get('listen_port', 8000)
PATH = hakuData.method.get_main_path()
onupdate = False

def main(msgDict):
    global onupdate
    if onupdate:
        return '已有update正在执行'
    onupdate = True
    onfailure = True
    output = ''
    while onfailure:
        output = subprocess.getoutput(f'cd {PATH} && git pull')
        outsplit = output.split()
        if 'Already' in outsplit and "date." in outsplit:
            onfailure = False
        else:
            time.sleep(5)
    rep = requests.get(url=f'http://127.0.0.1:{PORT}/UPDATE', params={}, timeout=20)
    onupdate = False
    return f'{output}\n{rep.status_code}'
