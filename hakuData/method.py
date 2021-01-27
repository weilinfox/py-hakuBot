# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import os, sys, threading, json, csv
import hakuData.log

# 路径检测和初始化
mainPath = os.path.normpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dataPath = mainPath + '/files'
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
'''{
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
}'''
        )
    config.close()
    print('The initial config file has created, you should edit it manually.')
    sys.exit()

# 主配置
configFilePath = dataPath + '/config.json'
configFile = open(configFilePath, "r")
configFileDict = json.loads(configFile.read())
configFile.close()

# 获取各目录配置文件
filenamesLock = threading.Lock()
def get_filenames():
    global csvFiles, sqliteFiles, jsonFiles, filenamesLock
    with filenamesLock:
        f = os.walk(csvPath)
        csvFiles = set(next(f)[2])
        f = os.walk(sqlitePath)
        sqliteFiles = set(next(f)[2])
        f = os.walk(jsonPath)
        jsonFiles = set(next(f)[2])

def get_main_path():
    return mainPath

def get_data_path():
    return dataPath

def get_plugin_path(routerName, mdlName):
    return f'{mainPath}/plugins/{routerName}/{mdlName}.py'

# config.json路径
def get_config_json():
    return configFilePath
# config.json内容
def get_config_dict():
    return configFileDict

# 插件配置路径
def get_plugin_config_json(plgName):
    global jsonPath, jsonFiles
    fileName = f'{plgName}.json'
    filePath = "{}/{}".format(jsonPath, fileName)
    # print(jsonFiles)
    if not fileName in jsonFiles:
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
    jsonFiles.add(fileName)
    return filePath

# csv文件操作
csvFileLock = threading.Lock()
csvUpdateSet = set() # csv update一次性标志
def touch_csv_file(fileName, headers):
    global csvFiles, csvFileLock
    if fileName in csvFiles:
        return 1
    filePath = f'{csvPath}/{fileName}'
    with csvFileLock:
        csvf = open(filePath, 'w', newline='')
        writer = csv.DictWriter(csvf, headers)
        writer.writeheader()
        csvf.close()
        csvFiles.add(fileName)

def read_dict_csv_file(fileName, headers):
    global csvFiles, csvFileLock
    filePath = f'{csvPath}/{fileName}'
    if not fileName in csvFiles:
        touch_csv_file(fileName, headers)
        return []
    else:
        with csvFileLock:
            dictList = []
            csvf = open(filePath, newline='')
            reader = csv.DictReader(csvf)
            for s in reader:
                dictList.append(s)
            csvf.close()
        return dictList

def write_dict_csv_file(fileName, headers, fileDict):
    global csvFiles, csvFileLock, csvUpdateSet
    if not fileName in csvFiles:
        raise FileNotFoundError(f'No such csv file: {fileName}')
    filePath = f'{csvPath}/{fileName}'
    with csvFileLock:
        csvf = open(filePath, 'w', newline='')
        writer = csv.DictWriter(csvf, headers)
        writer.writeheader()
        for dct in fileDict:
            writer.writerow(dct)
        csvf.close()
        csvUpdateSet.add(fileName)
    return 0

def get_csv_update_flag(fileName):
    global csvUpdateSet, csvFileLock
    flag = False
    with csvFileLock:
        if fileName in csvUpdateSet:
            csvUpdateSet.remove(fileName)
            flag = True
    return flag

get_filenames()
hakuData.log.init_log_path(logPath)

if __name__ == '__main__':
    print('csvFiles {}'.format(csvFiles))
    print('sqliteFiles {}'.format(sqliteFiles))
    print('jsonFiles {}'.format(jsonFiles))
