# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import os, threading
import hakuData.log

# 路径检测和初始化
dataPath = os.path.normpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/files'
dataPath = os.path.normpath(dataPath)
csvPath = dataPath + '/csv'
csvFiles = {}
sqlitePath = dataPath + '/sqlite'
sqliteFiles = {}
jsonPath = dataPath + '/json'
jsonFiles = {}
configFile = dataPath + '/config.json'
logPath = dataPath + '/log'

if not os.path.exists(dataPath):
    print('mkdir {}'.format(dataPath))
    os.mkdir(dataPath)
if not os.path.exists(csvPath):
    print('mkdir {}'.format(csvPath))
    os.mkdir(csvPath)
if not os.path.exists(sqlitePath):
    print('mkdir {}', sqlitePath)
    os.mkdir(sqlitePath)
if not os.path.exists(jsonPath):
    print('mkdir {}', jsonPath)
    os.mkdir(jsonPath)
if not os.path.exists(logPath):
    print('mkdir {}', logPath)
    os.mkdir(logPath)
if not os.path.exists(configFile) or not os.path.isfile(configFile):
    print('edit {}', configFile)
    config = open(configFile, 'w')
    # default config data
    config.write(
'''
{
    "server_config":{
        "listen_host": "127.0.0.1",
        "listen_port": 8000,
        "post_url": "127.0.0.1:8001",
        "access_token": "",
        "threads": false,
        "processes": 1,
        "log_level": "INFO",
        "console_log_level": "INFO"
    },
    "haku_config":{
        "admin_qq": -1,
        "admin_group": -1,
        "index": "."
    }
}

'''
        )
    config.close()

# 获取各目录配置文件
filenamesLock = threading.Lock()
def get_filenames():
    global csvFiles, sqliteFiles, jsonFiles
    f = os.walk(csvPath)
    csvFiles = set(next(f)[2])
    f = os.walk(sqlitePath)
    sqliteFiles = set(next(f)[2])
    f = os.walk(jsonPath)
    jsonFiles = set(next(f)[2])

# config.json路径
def get_config_json():
    return dataPath + '/config.json'

# 插件配置路径
def get_plugin_config_json(fileName):
    global jsonPath, jsonFiles
    filePath = "{}/{}.json".format(jsonPath, fileName)
    # print(jsonFiles)
    if not f'{fileName}.json' in jsonFiles:
        conf = open(filePath, "w")
        conf.write(
'''
{
    "auth": {
        "allow_group":[],
        "allow_user":[],
        "block_group":[],
        "block_user":[],
        "no_error_msg": false
    }
}
'''
            )
        conf.close()
    with filenamesLock:
        get_filenames()
    return filePath

with filenamesLock:
    get_filenames()
hakuData.log.init_log_path(logPath)

if __name__ == '__main__':
    print('csvFiles {}'.format(csvFiles))
    print('sqliteFiles {}'.format(sqliteFiles))
    print('jsonFiles {}'.format(jsonFiles))
