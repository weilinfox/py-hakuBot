# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import json
import hakuData.method

configFile = open(hakuData.method.get_config_json(), "r")
configDict = json.loads(configFile.read())
configFile.close()
serverConfig = configDict.get('server_config', {})
hakuConfig = configDict.get('haku_config', {})

INDEX = hakuConfig.get('index', '.')

pluginModules = dict()

def new_event(msgDict):
    if INDEX in msgDict['message']:
        print(msgDict['message'])

def link_modules(plgs):
    global pluginModules
    pluginModules = plgs 
