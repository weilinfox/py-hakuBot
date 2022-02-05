# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import logging

myLogger = logging.getLogger('hakuBot')

blockSet = {'采购补贴', '充值返券', '抢先购', '会员专享'}


def has_block_word(text) -> bool:
    for w in blockSet:
        if w in text:
            myLogger.debug(f'BlockWord:\n Find {w} in {text}.')
            return True
    return False
