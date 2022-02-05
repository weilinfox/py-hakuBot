# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import os
import json
import logging
import importlib
import haku_core.api_cqhttp as hakuApi
import haku_data.method

pluginModules = dict()
myLogger = logging.getLogger('hakuBot')


# 准入规则 需要满足配置中的各条
def check_plugin_auth(msgDict, routerName, mdlName):
    allow = True
    plgName = f'plugins.{routerName}.{mdlName}'
    if not os.path.exists(haku_data.method.get_plugin_path(routerName, mdlName)):
        myLogger.warning(f'No such plugin: {plgName}')
        return False, True
    plgConf = haku_data.method.get_plugin_config_json(plgName)
    if not os.path.exists(plgConf):
        myLogger.error(f'Plugin configure file: {plgConf} not found.')
        return False, True
    plgFile = open(plgConf, 'r')
    plgJson = plgFile.read()
    plgFile.close()
    plgDict = json.loads(plgJson)
    # 没有auth字段 停止执行
    if not ('auth' in plgDict):
        return False
    # 准入判断
    no_error_msg = plgDict['auth'].get('no_error_msg', False)
    if msgDict['message_type'] == 'group':
        alwGrp = plgDict['auth'].get('allow_group', [])
        blkGrp = plgDict['auth'].get('block_group', [])
        if alwGrp:
            if not (msgDict['group_id'] in alwGrp): allow = False
        if msgDict['group_id'] in blkGrp: allow = False
    alwUsr = plgDict['auth'].get('allow_user', [])
    blkUsr = plgDict['auth'].get('block_user', [])
    if alwUsr:
        if not (msgDict['user_id'] in alwUsr): allow = False
    if msgDict['user_id'] in blkUsr: allow = False

    return allow, no_error_msg


def get_module(msgDict, routerName, mdlName):
    global pluginModules
    plgName = f'plugins.{routerName}.{mdlName}'
    plgModule = None
    allow, no_error_msg = check_plugin_auth(msgDict, routerName, mdlName)
    if not allow:
        myLogger.info(
            f"User {msgDict.get('user_id', 0)} of group {msgDict.get('group_id', 0)} was blocked while calling plugin {plgName}"
            )
        if no_error_msg: plgName = ''
        else: plgName = f'plugins.{routerName}.auth_failed'
    if plgName and plgName in pluginModules:
        plgModule = pluginModules[plgName]
        myLogger.debug(f'Reuse plugin: {plgName}')
    elif plgName:
        try:
            plgModule = importlib.import_module(plgName)
            myLogger.debug(f'Load plugin: {plgName}')
        except ModuleNotFoundError:
            myLogger.warning(f'Plugin not find: {plgName}')
        except:
            myLogger.exception('RuntimeError')
        else:
            pluginModules[plgName] = plgModule
    return plgModule


def run_module(msgDict, routerName, mdlName):
    plgModule = get_module(msgDict, routerName, mdlName)
    if plgModule:
        try:
            plgMsg = plgModule.main(msgDict)
            if plgMsg:
                hakuApi.reply_msg(msgDict, plgMsg)
        except:
            myLogger.exception('RuntimeError')


def link_modules(plgs):
    global pluginModules
    pluginModules = plgs
