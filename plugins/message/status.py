# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import hakuData.status
import time

def main(msgDict):
    msgDct, msgTm = hakuData.status.get_status('message')
    metaDct, metaTm = hakuData.status.get_status('meta_event')
    ans = f'Current time: {time.asctime(time.gmtime(time.time() + 8 * 3600))}'
    ans += f'\n\nRouter message:\n{msgDct}'
    ans += f'\nLast Update: {time.asctime(time.gmtime(msgTm + 8 * 3600))}'
    ans += f'\n\nRouter meta_event:\n{metaDct}'
    ans += f'\nLast Update: {time.asctime(time.gmtime(metaTm + 8 * 3600))}'

    return ans
