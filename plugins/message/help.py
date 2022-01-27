# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import hakuData.method

configDict = hakuData.method.get_config_dict()
serverConfig = configDict.get('server_config', {})
hakuConfig = configDict.get('haku_config', {})

INDEX = hakuConfig.get('index', '.')

coms = {
    'baidu': '百度搜索',
    'weather': '天气预报',
    'qqmusic': 'QQ 音乐',
    'music': '网易云音乐',
    'wyy': '网抑云',
    'yiyan': '一言',
    'ubuntu': 'ubuntu 软件包搜索',
    'debian': 'debian 软件包搜索',
    'arch': 'archlinux 软件包搜索',
    'loongnix': 'loongnix20 软件包搜索',
    'loongnews': '龙芯开源社区新闻订阅',
    'rss': 'rss 订阅设置',
    'alarm': '自动提醒设置',
    'note': '简单的记事本',
    'echo': '小白不是复读机！',
    'notice': '附加功能配置',
    'ping': '检查小白是否在线',
    'version': '版本号',
}


def main(msgDict):
    comm = msgDict['raw_message'].split()
    if len(comm) > 1 and comm[1] in coms.keys():
        ans = coms[comm[1]]
    else:
        ans = '常用指令：'
        for s in coms.keys():
            ans += ' ' + s
        ans += '\n' + INDEX + 'help + 命令 查看简单的描述'
    return ans


if __name__ == '__main__':
    print(main({'raw_message': 'help'}))
    print(main({'raw_message': 'help  ping '}))
