# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

import haku_data.status
import time

def main(msgDict):
    msgDct, msgTm = haku_data.status.get_status('message')
    metaDct, metaTm = haku_data.status.get_status('meta_event')
    mainDct, mainTm = haku_data.status.get_status('__main__')
    run_time = int(time.time()-mainDct['start_time'])
    ans = f'Current time: {time.asctime(time.gmtime(time.time() + 8 * 3600))}'
    ans += f'\n\nUp time: {run_time//86400} days {(run_time%86400)//3600}:{(run_time%3600)//60}:{run_time%60}'
    ans += f'\n\nRouter message:\n{msgDct}'
    ans += f'\nLast Update: {time.asctime(time.gmtime(msgTm + 8 * 3600))}'
    ans += f'\n\nRouter meta_event:\n{metaDct}'
    ans += f'\nLast Update: {time.asctime(time.gmtime(metaTm + 8 * 3600))}'

    return ans
