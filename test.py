#!/bin/python3
# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE
"""
运行测试
"""

import threading
import requests
import time
import logging
import main as hakubot
import test.cqhttp as cqhttp


SENDHOST = '127.0.0.1'
SENDPORT = hakubot.PORT
sendurl = f'http://{SENDHOST}:{SENDPORT}'
LISTENURL = hakubot.POSTURL.split(':', 1)
LISTENHOST = LISTENURL[0]
LISTENPORT = int(LISTENURL[1])
listenurl = f'http://{LISTENHOST}:{LISTENPORT}'

cqhttp.cqhttp_init(LISTENHOST, LISTENPORT)

testthreads = list()
testfunctions = list()
groupmsgdict = {'message': '这是一个测试',
                'message_type': 'private',
                'post_type': 'message',
                'raw_message': '这是一个测试',
                'self_id': 2000000000,
                'time': time.time(),
                'user_id': 2000000002}
usermsgdict = {'message': '这是一个测试',
                'message_type': 'group',
                'post_type': 'message',
                'raw_message': '这是一个测试',
                'group_id': 2000000001,
                'self_id': 2000000000,
                'time': time.time(),
                'user_id': 2000000002}

mylogger = logging.getLogger('hakuBot')


def test_server_start():
    """
    启动所有测试服务器
    :return: 成功返回 True 失败返回 False
    """
    bot = threading.Thread(target=hakubot.haku_start, args=[])
    cq = threading.Thread(target=cqhttp.cqhttp_start, args=[])
    bot.start()
    cq.start()
    time.sleep(0.5)
    return bot.is_alive() and cq.is_alive()


def test_server_stop():
    """
    关闭所有测试服务器
    :return: 无返回值
    """
    requests.get(url=f'{listenurl}/STOP')
    requests.get(url=f'{sendurl}/STOP')


def test_server_version():
    """
    获取所有测试服务器的版本号
    :return: 格式化后的版本号
    """
    return f'''hakubot version: {requests.get(url=f'{listenurl}/VERSION').text}
test cqhttp version: {requests.get(url=f'{sendurl}/VERSION').text}'''


def test_bot_busy():
    """
    获取 hakubot 当前执行线程数量
    :return: 是否 > 0
    """
    res = requests.get(url=f'{sendurl}/THREADS').text.split()
    n = int(res[1])
    return n > 0


if test_server_start():
    mylogger.info('测试服务器启动成功')
else:
    mylogger.info('测试服务器启动失败！')
    test_server_stop()
    exit(-1)

print(test_server_version())


def test_send(msgdict):
    res = requests.post(url=sendurl, json=msgdict)
    print(f'请求返回 {res.status_code} {res.text}')


# 消息发送测试
def test_message_group():
    test_send(groupmsgdict)


def test_message_private():
    test_send(usermsgdict)


# ping 测试
def test_message_group_ping():
    global groupmsgdict
    groupmsgdict['message'] = groupmsgdict['raw_message'] = '.ping'
    test_send(groupmsgdict)


def test_message_private_ping():
    global usermsgdict
    usermsgdict['message'] = usermsgdict['raw_message'] = '.ping'
    test_send(usermsgdict)


# weather 测试
def test_message_group_weather():
    global groupmsgdict
    groupmsgdict['message'] = groupmsgdict['raw_message'] = '.weather 浙江 金华'
    test_send(groupmsgdict)


def test_message_group_weather_0():
    global groupmsgdict
    groupmsgdict['message'] = groupmsgdict['raw_message'] = '.weather 浙江 北京'
    test_send(groupmsgdict)


def test_message_private_weather():
    global usermsgdict
    usermsgdict['message'] = usermsgdict['raw_message'] = '.weather 浙江 金华'
    test_send(usermsgdict)


def test_message_private_weather_0():
    global usermsgdict
    groupmsgdict['message'] = usermsgdict['raw_message'] = '.weather 浙江 北京'
    test_send(usermsgdict)


# rss 测试
def test_message_group_rss():
    global groupmsgdict
    groupmsgdict['message'] = groupmsgdict['raw_message'] = '.rss help'
    test_send(groupmsgdict)


def test_message_group_rss_0():
    global groupmsgdict
    groupmsgdict['message'] = groupmsgdict['raw_message'] = '.rss add link https://github.com/weilinfox/py-hakuBot/tags.atom'
    test_send(groupmsgdict)


def test_message_group_rss_1():
    global groupmsgdict
    groupmsgdict['message'] = groupmsgdict['raw_message'] = '.rss test'
    test_send(groupmsgdict)


def test_message_group_rss_2():
    global groupmsgdict
    groupmsgdict['message'] = groupmsgdict['raw_message'] = '.rss help'
    test_send(groupmsgdict)


def test_message_group_rss_3():
    global groupmsgdict
    groupmsgdict['message'] = groupmsgdict['raw_message'] = '.rss del 1'
    test_send(groupmsgdict)


def test_message_group_rss_4():
    global groupmsgdict
    groupmsgdict['message'] = groupmsgdict['raw_message'] = '.rss del 0'
    test_send(groupmsgdict)


def test_message_private_rss():
    global usermsgdict
    usermsgdict['message'] = usermsgdict['raw_message'] = '.rss help'
    test_send(usermsgdict)


def test_message_private_rss_0():
    global usermsgdict
    usermsgdict['message'] = usermsgdict['raw_message'] = '.rss add link https://github.com/weilinfox/py-hakuBot/tags.atom'
    test_send(usermsgdict)


def test_message_private_rss_1():
    global usermsgdict
    usermsgdict['message'] = usermsgdict['raw_message'] = '.rss test'
    test_send(usermsgdict)


def test_message_private_rss_2():
    global usermsgdict
    usermsgdict['message'] = usermsgdict['raw_message'] = '.rss help'
    test_send(usermsgdict)


def test_message_private_rss_3():
    global usermsgdict
    usermsgdict['message'] = usermsgdict['raw_message'] = '.rss del 1'
    test_send(usermsgdict)


def test_message_private_rss_4():
    global usermsgdict
    usermsgdict['message'] = usermsgdict['raw_message'] = '.rss del 0'
    test_send(usermsgdict)


def test_message_group_baidu():
    global groupmsgdict
    groupmsgdict['message'] = groupmsgdict['raw_message'] = '.baidu github'
    test_send(groupmsgdict)


def test_message_private_baidu():
    global usermsgdict
    usermsgdict['message'] = usermsgdict['raw_message'] = '.baidu github'
    test_send(usermsgdict)


def test_message_group_bing():
    global groupmsgdict
    groupmsgdict['message'] = groupmsgdict['raw_message'] = '.bing github'
    test_send(groupmsgdict)


def test_message_private_bing():
    global usermsgdict
    usermsgdict['message'] = usermsgdict['raw_message'] = '.bing github'
    test_send(usermsgdict)


def test_message_group_music():
    global groupmsgdict
    groupmsgdict['message'] = groupmsgdict['raw_message'] = '.music 社会主义好'
    test_send(groupmsgdict)


def test_message_private_music():
    global usermsgdict
    usermsgdict['message'] = usermsgdict['raw_message'] = '.music 社会主义好'
    test_send(usermsgdict)


def test_message_group_qqmusic():
    global groupmsgdict
    groupmsgdict['message'] = groupmsgdict['raw_message'] = '.qqmusic 社会主义好'
    test_send(groupmsgdict)


def test_message_private_qqmusic():
    global usermsgdict
    usermsgdict['message'] = usermsgdict['raw_message'] = '.qqmusic 社会主义好'
    test_send(usermsgdict)


def test_message_group_notice():
    global groupmsgdict
    groupmsgdict['message'] = groupmsgdict['raw_message'] = '.notice'
    test_send(groupmsgdict)


def test_message_group_notice_0():
    global groupmsgdict
    groupmsgdict['message'] = groupmsgdict['raw_message'] = '.notice on greet'
    test_send(groupmsgdict)


def test_message_group_notice_1():
    global groupmsgdict
    groupmsgdict['message'] = groupmsgdict['raw_message'] = '.notice off greet'
    test_send(groupmsgdict)


def test_message_group_notice_2():
    global groupmsgdict
    groupmsgdict['message'] = groupmsgdict['raw_message'] = '.notice greet greetmsg'
    test_send(groupmsgdict)


def test_message_group_notice_3():
    global groupmsgdict
    groupmsgdict['message'] = groupmsgdict['raw_message'] = '.notice show greet'
    test_send(groupmsgdict)


def test_message_private_notice():
    global usermsgdict
    usermsgdict['message'] = usermsgdict['raw_message'] = '.notice'
    test_send(usermsgdict)


def test_message_private_notice_0():
    global usermsgdict
    usermsgdict['message'] = usermsgdict['raw_message'] = '.notice on greet'
    test_send(usermsgdict)


def test_message_private_notice_1():
    global usermsgdict
    usermsgdict['message'] = usermsgdict['raw_message'] = '.notice off greet'
    test_send(usermsgdict)


def test_message_private_notice_2():
    global usermsgdict
    usermsgdict['message'] = usermsgdict['raw_message'] = '.notice greet greetmsg'
    test_send(usermsgdict)


def test_message_private_notice_3():
    global usermsgdict
    usermsgdict['message'] = usermsgdict['raw_message'] = '.notice show greet'
    test_send(usermsgdict)


def test_message_group_update():
    global groupmsgdict
    groupmsgdict['message'] = groupmsgdict['raw_message'] = '.update'
    test_send(groupmsgdict)
    test_send(groupmsgdict)


testfunctions = [test_message_group,
                 test_message_private,
                 test_message_group_ping,
                 test_message_private_ping,
                 test_message_group_weather,
                 test_message_group_weather_0,
                 test_message_private_weather,
                 test_message_private_weather_0,
                 test_message_group_rss,
                 test_message_group_rss_0,
                 test_message_group_rss_1,
                 test_message_group_rss_2,
                 test_message_group_rss_3,
                 test_message_group_rss_4,
                 test_message_private_rss,
                 test_message_private_rss_0,
                 test_message_private_rss_1,
                 test_message_private_rss_2,
                 test_message_private_rss_3,
                 test_message_private_rss_4,
                 test_message_group_baidu,
                 test_message_private_baidu,
                 test_message_group_bing,
                 test_message_private_bing,
                 test_message_group_music,
                 test_message_private_music,
                 test_message_group_qqmusic,
                 test_message_private_qqmusic,
                 test_message_group_notice,
                 test_message_group_notice_0,
                 test_message_group_notice_1,
                 test_message_group_notice_2,
                 test_message_group_notice_3,
                 test_message_private_notice,
                 test_message_private_notice_0,
                 test_message_private_notice_1,
                 test_message_private_notice_2,
                 test_message_private_notice_3,
                 test_message_group_update
                 ]

for f in testfunctions:
    testthreads.append(threading.Thread(target=f, args=[], daemon=True))
print('Starting tests...')
time.sleep(1)
testcount = 0
for t in testthreads:
    testcount += 1
    print('--------------------------------------------------------------------------------')
    t.start()
    t.join()
    while test_bot_busy():
        time.sleep(0.5)
    print(f'Test {testcount} finished.')
print('--------------------------------------------------------------------------------')

print('Test finished.')
test_server_stop()

