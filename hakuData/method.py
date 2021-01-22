# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import os

# check files
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
        "processes": 1
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

def get_filenames():
    global csvFiles, sqliteFiles, jsonFiles
    f = os.walk(csvPath)
    csvFiles = set(next(f)[2])
    f = os.walk(sqlitePath)
    sqliteFiles = set(next(f)[2])
    f = os.walk(jsonPath)
    jsonFiles = set(next(f)[2])

def get_config_json():
    return dataPath + '/config.json'

def get_plugin_config_json(fileName):
    global jsonPath, jsonFiles
    if fileName in jsonFiles:
        return "{}/{}".format(jsonPath, fileName)
    else:
        conf = open("{}/{}".format(jsonPath, fileName), "w")
        conf.write(
'''
{}
'''
            )
        conf.close()
        return "{}/{}".format(jsonPath, fileName)

get_filenames()

if __name__ == '__main__':
    print('csvFiles {}'.format(csvFiles))
    print('sqliteFiles {}'.format(sqliteFiles))
    print('jsonFiles {}'.format(jsonFiles))
