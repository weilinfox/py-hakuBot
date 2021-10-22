#!/bin/python3
# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import sys
import os
import requests
import json


def main(args):
    if len(args) != 1 or args[0] == 'help':
        print('''
Usage: operate [COMMAND]          Run hakuBot command

       COMMAND:
            VERSION     Get hakuBot version
            UPDATE      Update hakuBot
''')
        return 0

    configFile = os.path.normpath(os.path.dirname(os.path.abspath(__file__))) + '/files/config.json'
    print(f'Load config file: {configFile}')
    port = 0
    if os.path.exists(configFile):
        with open(configFile, 'r') as conFile:
            try:
                configJson = json.loads(conFile.read()).get('server_config', {})
            except:
                print('Load hakuBot config file failed.')
            else:
                port = configJson.get('listen_port', 0)
        if not port:
            print('Get hakuBot listen port failed.')
            return 1
    else:
        print('Cannot find hakuBot config file.')
        return 1
    print(f'Opration will be send to host: 127.0.0.1:{port}')
    try:
        resp = requests.get(f'http://127.0.0.1:{port}/{args[0]}', {})
    except Exception as e:
        print(f'Request failed:\n{e}')
    else:
        if resp.status_code == 200:
            print('Opration succeeded with return code 200.')
            print(f'Return text: {resp.text}')
        else:
            print(f'Opration unexpectedly returned code {resp.status_code}.')
            print(f'Return text: {resp.text}')
            return 1
    return 0


if __name__ == "__main__":
   main(sys.argv[1:])
