# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE
"""
定义数据文件的路径、存取方法
暂存静态的配置
配置文件使用 json
数据库使用 sqlite3 和 csv
"""

import os
import sys
import threading
import json
import csv
import sqlite3
import logging
import hakuData.log

# 路径检测和初始化
mainPath = os.path.normpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dataPath = mainPath + '/files'
dataPath = os.path.normpath(dataPath)
csvPath = dataPath + '/csv'
csvFiles = set()
sqlitePath = dataPath + '/sqlite'
sqliteFiles = set()
jsonPath = dataPath + '/json'
jsonFiles = set()
configFile = dataPath + '/config.json'
keysFile = dataPath + '/keys.json'
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
if not os.path.exists(keysFile):
    print('edit {}'.format(keysFile))
    kys = open(keysFile, 'w')
    kys.write('''{
    "sample":"myKey"
}''')
    kys.close()
if not os.path.exists(configFile) or not os.path.isfile(configFile):
    print('edit {}'.format(configFile))
    config = open(configFile, 'w')
    # default config data
    config.write('''{
    "server_config":{
        "listen_host": "127.0.0.1",
        "listen_port": 8000,
        "post_url": "127.0.0.1:8001",
        "access_token": "",
        "threads": true,
        "processes": 1,
        "log_level": "INFO",
        "console_log_level": "INFO"
    },
    "haku_config":{
        "admin_qq": -1,
        "admin_group": -1,
        "index": "."
    }
}''')
    config.close()
    print('The initial config file has created, you should edit it manually.')
    sys.exit()

# 主配置
confFile = open(configFile, "r")
configFileDict = json.loads(confFile.read())
confFile.close()

# keys
kysFile = open(keysFile, 'r')
keysFileDict = json.loads(kysFile.read())
kysFile.close()

# 获取各目录配置文件
filenamesLock = threading.Lock()

# logger
hakuData.log.init_log_path(logPath)
myLogger = None


def build_logger():
    """
    获取全局logger 等待 logger 配置完成后调用
    :return: 无返回值
    """
    global myLogger
    myLogger = logging.getLogger('hakuBot')


def get_filenames():
    """
    获取 csv sqlite json 子目录下的所有文件
    :return: 无返回值
    """
    global csvFiles, sqliteFiles, jsonFiles, filenamesLock
    with filenamesLock:
        f = os.walk(csvPath)
        csvFiles = set(next(f)[2])
        f = os.walk(sqlitePath)
        sqliteFiles = set(next(f)[2])
        f = os.walk(jsonPath)
        jsonFiles = set(next(f)[2])


get_filenames()


def get_main_path():
    """
    获取工作目录绝对路径
    :return: main.py 所在目录绝对路径
    """
    return mainPath


def get_data_path():
    """
    获取 files 目录绝对路径
    :return: files 目录绝对路径
    """
    return dataPath


def get_plugin_path(routerName, mdlName):
    """
    获取插件绝对路径
    :param routerName: router 名
    :param mdlName: 插件名
    :return: 插件的绝对路径
    """
    return f'{mainPath}/plugins/{routerName}/{mdlName}.py'


# config.json路径
def get_config_json():
    """
    获取 config.json
    :return: config.json 的绝对路径
    """
    return configFile


# config.json内容
def get_config_dict():
    """
    获取 config.json 的内容
    :return: json 键值对
    """
    return configFileDict


# keys.json路径
def get_keys_json():
    """
    获取 keys.json
    :return: keys.json 的绝对路径
    """
    return keysFile


# keys.json内容
def get_keys_dict():
    """
    获取 keys.json 的内容
    :return: json 键值对
    """
    return keysFileDict


# keys.json查询
def search_keys_dict(field):
    """
    从 keys.json 的内容中查询
    :param field: 待查询的键
    :return: 键对应的值 不存在返回 ''
    """
    return keysFileDict.get(field, '')


# 插件配置路径
def get_plugin_config_json(plgName):
    """
    获取插件权限配置 不存在则创建默认配置
    :param plgName: 自定义文件名
    :return: 权限配置dict
    """
    global jsonPath, jsonFiles
    fileName = f'{plgName}.json'
    filePath = "{}/{}".format(jsonPath, fileName)
    # print(jsonFiles)
    if not fileName in jsonFiles:
        if os.path.exists(filePath):
            if myLogger: myLogger.error(f'{fileName} exists but not in jsonFiles.')
            else: print(f'{fileName} exists but not in jsonFiles.')
        else:
            conf = open(filePath, "w")
            conf.write('''{
    "auth": {
        "allow_group":[],
        "allow_user":[],
        "block_group":[],
        "block_user":[],
        "no_error_msg": false
    }
}
''')
            conf.close()
            jsonFiles.add(fileName)
    return filePath


def get_default_plugin_config_json(routerName, mdlName):
    """
    获取插件权限配置 使用默认的配置文件名 不存在则创建默认配置
    :param routerName: router名
    :param mdlName: 模块名
    :return: 权限配置dict
    """
    return get_plugin_config_json(f'plugins.{routerName}.{mdlName}')


# csv文件操作
csvFileLock = threading.Lock()
csvUpdateSet = set() # csv update一次性标志


def csv_get_name(module, name):
    """
    获取唯一csv文件名
    :param module: 模块名称
    :param name: 自定义名称
    :return: 'module.name.csv'
    """
    return f"{module}.{name}.csv"


def csv_create_file(fileName, headers):
    """
    在 files/csv 目录创建csv文件
    :param fileName: 文件名
    :param headers: csv字典键列表
    :return: 无返回值
    """
    global csvFiles, csvFileLock
    filePath = f'{csvPath}/{fileName}'
    if fileName in csvFiles or os.path.exists(filePath):
        return 1
    with csvFileLock:
        csvf = open(filePath, 'w', newline='')
        writer = csv.DictWriter(csvf, headers)
        writer.writeheader()
        csvf.close()
        csvFiles.add(fileName)


def csv_read_dict(fileName, headers):
    """
    读取csv数据文件 若不存在则创建
    :param fileName: 文件名
    :param headers: csv字典键列表
    :return: dict键值对列表
    """
    global csvFiles, csvFileLock
    filePath = f'{csvPath}/{fileName}'
    if not fileName in csvFiles:
        resp = csv_create_file(fileName, headers)
        if resp:
            if myLogger: myLogger.error(f'Tough csv file {filePath} failed.')
            else: print(f'Tough csv file {filePath} failed.')
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


def csv_write_dict(fileName, headers, fileDict):
    """
    写入csv数据文件 文件必须存在
    :param fileName: 文件名
    :param headers: csv字典键列表
    :param fileDict: dict键值对列表
    :return: 恒为0
    """
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


def csv_append_dict(fileName, headers, fileDict):
    """
    向csv数据文件追加数据 文件必须存在
    :param fileName: 文件名
    :param headers: csv字典键列表
    :param fileDict: dict键值对列表
    :return: 恒为0
    """
    global csvFiles, csvFileLock, csvUpdateSet
    if not fileName in csvFiles:
        raise FileNotFoundError(f'No such csv file: {fileName}')
    filePath = f'{csvPath}/{fileName}'
    with csvFileLock:
        csvf = open(filePath, 'a', newline='')
        writer = csv.DictWriter(csvf, headers)
        for dct in fileDict:
            writer.writerow(dct)
        csvf.close()
        csvUpdateSet.add(fileName)
    return 0


def csv_check_update(fileName):
    """
    csv数据文件是否被修改 查询为True后flag将被清除
    :param fileName: 文件名
    :return: bool
    """
    global csvUpdateSet, csvFileLock
    flag = False
    with csvFileLock:
        if fileName in csvUpdateSet:
            csvUpdateSet.remove(fileName)
            flag = True
    return flag


# sqlite数据库操作
def sqlite_get_name(module, name):
    """
    获取默认sqlite文件名
    :param module: 模块名称
    :param name: 自定义名称
    :return: 'module.name.db'
    """
    return f"{module}.{name}.db"


def sqlite_db_open(name):
    """
    从 files/sqlite 目录打开sqlite数据库文件
    :param name: 文件名
    :return: sqlite connection对象 失败返回 None
    """
    try:
        conn = sqlite3.connect(f'{sqlitePath}/{name}')
    except sqlite3.OperationalError:
        return None
    return conn


def sqlite_default_db_open(router, module):
    """
    从 files/sqlite 目录打开默认sqlite数据库文件
    :param router: router名称
    :param module: 自定义名称
    :return: sqlite connection对象 失败返回 None
    """
    name = sqlite_get_name(router, module)
    return sqlite_db_open(name)


def sqlite_db_close(conn):
    """
    关闭 sqlite3.connection 对象
    :param conn: sqlite3.connection 对象
    :return: 无返回值
    """
    if conn:
        try:
            conn.commit()
            conn.close()
        except:
            pass


if __name__ == '__main__':
    print('csvFiles {}'.format(csvFiles))
    print('sqliteFiles {}'.format(sqliteFiles))
    print('jsonFiles {}'.format(jsonFiles))
