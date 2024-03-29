# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE
"""
从 main.py 获取版本号

自动升级不更新 main.py
升级版本号需要整个重启
"""

import requests
import time
import haku_data.method

configDict = haku_data.method.get_config_dict()
serverConfig = configDict.get('server_config', {})
hakuConfig = configDict.get('haku_config', {})

PORT = serverConfig.get('listen_port', 8000)
PATH = haku_data.method.get_main_path()


def main(msgDict):
    resp = requests.get(url=f'http://127.0.0.1:{PORT}/VERSION', params={}, timeout=5)
    utime = time.asctime(time.gmtime(haku_data.method.get_update_time() + 8 * 3600))
    if resp.status_code == 200:
        hakuBotVer = resp.text
    else:
        hakuBotVer = '获取版本号失败'
    return f'小白哦~\n{hakuBotVer}\n最后更新: {utime}'
