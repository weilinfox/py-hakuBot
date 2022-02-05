# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE
"""
马克思主义
"""

import random
import haku_data.method as method


configDict = method.get_config_dict()
hakuConfig = configDict.get('haku_config', {})
ADMINQID = hakuConfig.get('admin_qq', 0)


def handle_open():
    conn = method.sqlite_default_db_open('message', 'marx')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS marx(id BIGINT, mksvy VARCHAR(2048));')
    cur.execute('SELECT mksvy FROM marx WHERE id=0;')
    count = cur.fetchall()
    try:
        if count:
            count = int(count[0][0])
        else:
            count = 0
            cur.execute('INSERT INTO marx (id, mksvy) VALUES(0, "0");')
    except Exception as e:
        e.with_traceback()
        method.sqlite_db_close(conn)
        conn = None
        count = 0

    return conn, count


def handle_add(msg):
    conn, count = handle_open()
    if not conn:
        return '添加失败'
    try:
        count += 1
        cur = conn.cursor()
        cur.execute('INSERT INTO marx(id, mksvy) VALUES(?, ?);', (count, msg))
        cur.execute(f'UPDATE marx SET mksvy="{count}" WHERE id=0;')
        method.sqlite_db_close(conn)
    except Exception as e:
        e.with_traceback()
        method.sqlite_db_close(conn)
        return f'添加失败: {e}'
    return '添加成功'


def handle_check():
    conn, count = handle_open()
    if not conn:
        return '啊嘞嘞出错了，一定是数据库炸了不是咱!'
    if count == 0:
        return '库里啥也没有'
    nid = random.randint(1, count)
    cur = conn.cursor()
    cur.execute('SELECT mksvy FROM marx WHERE id=?;', (nid,))
    msg = cur.fetchall()[0][0]
    method.sqlite_db_close(conn)
    return msg


def main(msgdict):
    msg = msgdict['message'].split()
    if len(msg) > 2 and msg[1] == 'add':
        if msgdict['user_id'] != ADMINQID:
            return '无权限'
        msg = msgdict['message'].split(None, 2)
        return handle_add(msg[2])
    else:
        return handle_check()


