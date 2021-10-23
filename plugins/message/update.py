# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import subprocess
import requests
import time
import hakuData.method

configDict = hakuData.method.get_config_dict()
serverConfig = configDict.get('server_config', {})
hakuConfig = configDict.get('haku_config', {})

PORT = serverConfig.get('listen_port', 8000)
PATH = hakuData.method.get_main_path()
onupdate = False


def main(msgDict):
    global onupdate
    if onupdate:
        return '已有更新任务正在执行'
    onupdate = True
    onfailure = True
    trys = 0
    durition = time.time()
    while onfailure:
        trys += 1
        output = subprocess.getoutput(f'cd {PATH} && git pull')
        outsplit = output.split()
        if 'Already' in outsplit and "date." in outsplit:
            onfailure = False
        else:
            time.sleep(5)
    durition = int(time.time() - durition)
    try:
        rep = requests.get(url=f'http://127.0.0.1:{PORT}/UPDATE', params={}, timeout=20)
    except Exception as e:
        repmsg = f'UPDATE request failed:\n {e}'
    else:
        if rep.status_code == 200:
            repmsg = '代码更新成功'
        else:
            repmsg = f'UPDATE failed with code {rep.status_code}'
    onupdate = False

    return f'{repmsg}\ngit pull 尝试 {trys} 次\n耗时 {durition} 秒'
