# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import haku_core.api_cqhttp

reportQid = -1
reportGid = -1


def init_report(qid, gid):
    global reportGid, reportQid
    reportQid, reportGid = qid, gid


def report(msg):
    if reportQid > 99999: haku_core.cqhttpApi.send_private_msg(reportQid, msg)
    if reportGid > 99999: haku_core.cqhttpApi.send_group_msg(reportGid, msg)
