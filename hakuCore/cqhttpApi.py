# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

'''
由于没有找到cqhttp的文档, 故实现了兼容cqhttp协议的OneBot的Api作为替代, 兼容一定标准的api在注释中已标明, 自定义api用(hakuBot)标明
重点实现go-cqhttp的协议, 重复的api优先实现go-cqhttp的版本, 部分自定义api为cq码封装, 封装的cq码标准亦标出
OneBot_v11 api依照这里 https://github.com/howmanybots/onebot/blob/master/v11/specs/api/public.md
go-cqhttp api依照这里 https://github.com/Mrs4s/go-cqhttp/blob/master/docs/cqhttp.md
所有api都返回一个元祖 (<状态码>, <响应消息字典>)
状态码40x代表http请求错误, 部分404码为进行操作前函数进行的操作合法性检查发现错误, 其他为cqhttp状态码, 列如下:
0 成功, 1 进入异步执行而结果未知, 100 参数缺失或参数无效, 102 返回的数据无效(如没有权限), 103 操作失败(如没有权限),
104 凭证失效而操作失败(可尝试清除缓存解决), 201 工作线程池未正确初始化而无法执行异步任务
'''

import requests, logging, json
import hakuData.log

uploadUrl = ''
uploadToken = ''
uploadProtocol = ''
myLogger = logging.getLogger('hakuBot')

def init_api_url(ptcl, url, token):
    global uploadUrl, uploadToken, uploadProtocol
    uploadProtocol, uploadUrl, uploadToken = (ptcl, url, token)

def send_cqhttp_request(path, params):
    myLogger.info(f'Send message to {path} : {params}')
    # 如果需要token
    if uploadToken: params['access_token'] = uploadToken
    return requests.get(url=f'{uploadProtocol}://{uploadUrl}{path}',params=params)

def parse_cqhttp_resp(resp):
    if resp.status_code == 200:
        respDict = json.loads(resp.text)
        return respDict['retcode'], respDict['data']
    else:
        return resp.status_code, {}

# 发送私聊(OneBot_v11) 返回 message_id
# auto_escape 消息内容是否作为纯文本发送(即不解析CQ码)
def send_private_msg (uid, msg, auto_escape = False):
    resp = send_cqhttp_request('/send_private_msg', {'user_id':uid, 'message':msg, 'auto_escape':auto_escape})
    return parse_cqhttp_resp(resp)

# 发送群消息(OneBot_v11) 返回 message_id
def send_group_msg (gid, msg, auto_escape = False):
    resp = send_cqhttp_request('/send_group_msg', {'group_id':gid, 'message':msg, 'auto_escape':auto_escape})
    return parse_cqhttp_resp(resp)

# 发送戳一戳(hakuBot) (go-cqhttp_cq) 返回 message_id 返回为0的message_id
def send_group_poke(gid, uid):
    return send_group_msg('/send_group_msg', {'group_id':gid, 'message':f'[CQ:poke,qq={uid}]'})

# 发送群xml消息(hakuBot) (OneBot_v11_cq) 返回 message_id
def send_group_xml(gid, xmlMsg):
    # 此处添加html实体化处理逻辑 [CQ:xml,data=<?xml ...]
    return 404, {}

# 发送私聊xml消息(hakuBot) (OneBot_v11_cq) 返回 message_id
def send_private_xml(uid, xmlMsg):
    # 此处添加html实体化处理逻辑
    return 404, {}

# 发送群json消息(hakuBot) (OneBot_v11_cq) 返回 message_id
def send_group_json(gid, jsonMsg):
    jsonMsg = jsonMsg.replace(',', '&#44;').replace('&', '&amp;').replace('[', '&#91;').replace(']', '&#93;')
    return send_group_msg(gid, f'[CQ:json,data={jsonMsg}]')

# 发送私聊json消息(hakuBot) (OneBot_v11_cq) 返回 message_id
def send_private_json(uid, jsonMsg):
    jsonMsg = jsonMsg.replace(',', '&#44;').replace('&', '&amp;').replace('[', '&#91;').replace(']', '&#93;')
    return send_private_msg(uid, f'[CQ:json,data={jsonMsg}]')

# 发送群tts消息(hakuBot) (go-cqhttp_cq) 返回 message_id
def send_group_tts(gid, msg):
    return send_group_msg(gid, f'[CQ:tts,text={msg}]')

# 发送群链接分享(hakuBot) (OneBot_v11_cq) 返回 message_id
# shareUrl 分享链接, title 内容标题, content 内容描述, image 图片url
def send_group_share_link(gid, shareUrl, title, content, image=''):
    if image:
        return send_group_msg(gid, f'[CQ:share,url={shareUrl},title={title},content={content},image={image}]')
    else:
        return send_group_msg(gid, f'[CQ:share,url={shareUrl},title={title},content={content}')

# 发送私聊链接分享(hakuBot) (OneBot_v11_cq) 返回 message_id
def send_private_share_link(uid, shareUrl, title, content, image=''):
    if image:
        return send_private_msg(uid, f'[CQ:share,url={shareUrl},title={title},content={content},image={image}]')
    else:
        return send_private_msg(uid, f'[CQ:share,url={shareUrl},title={title},content={content}]')

# 发送群音乐分享(hakuBot) (OneBot_v11_cq) 返回 message_id
# musicType 包括 qq QQ音乐, 163 网易云音乐, xm 虾米音乐
def send_group_share_music(gid, musicType, musicId):
    if not (musicType in ['qq', '163', 'xm']):
        return 404, {}
    return send_group_msg(gid, f'[CQ:music,type={musicType},id={musicId}]')

# 发送私聊音乐分享(hakuBot) (OneBot_v11_cq) 返回 message_id
def send_private_share_music(uid, musicType, musicId):
    if not (musicType in ['qq', '163', 'xm']):
        return 404, {}
    return send_private_msg(uid, f'[CQ:music,type={musicType},id={musicId}]')

# 发送群自定义音乐分享(hakuBot) (OneBot_v11_cq) 返回 message_id
# jumpUrl 点击后跳转目标URL, musicUrl 音乐URL, title 标题
def send_group_share_my_music(gid, jumpUrl, musicUrl, title, musicType='custom', image=''):
    if musicType in ['qq', '163', 'xm']:
        return 404, {}
    if image:
        return send_group_msg(gid, f'[CQ:music,type={musicType},url={jumpUrl},audio={musicUrl},title={title},image={image}]')
    else:
        return send_group_msg(gid, f'[CQ:music,type={musicType},url={jumpUrl},audio={musicUrl},title={title}]')

# 发送私聊自定义音乐分享(hakuBot) (OneBot_v11_cq) 返回 message_id
def send_private_share_my_music(uid, jumpUrl, musicUrl, title, musicType='custom', image=''):
    if musicType in ['qq', '163', 'xm']:
        return 404, {}
    if image:
        return send_private_msg(uid, f'[CQ:music,type={musicType},url={jumpUrl},audio={musicUrl},title={title},image={image}]')
    else:
        return send_private_msg(uid, f'[CQ:music,type={musicType},url={jumpUrl},audio={musicUrl},title={title}]')

# 发送消息(OneBot_v11) 返回 message_id
def send_msg (msgType, sid, msg, auto_escape = False):
    resp = ''
    if msgType == 'private':
        resp = send_cqhttp_request('/send_msg', {'message_type':'private', 'user_id':sid, 'message':msg, 'auto_escape':auto_escape})
    elif msgType == 'group':
        resp = send_cqhttp_request('/send_msg', {'message_type':'group', 'group_id':sid, 'message':msg, 'auto_escape':auto_escape})
    else:
        myLogger.error('No such message type: {}'.format(msgType))
        return 404, {}
    return parse_cqhttp_resp(resp)

# 回复(hakuBot) 按照传入的msgDict判断私聊和群发 返回 message_id
def reply_msg (msgDict, msg, auto_escape = False):
    msgType = msgDict.get('message_type', '')
    if msgType == 'private':
        return send_msg (msgType, msgDict['user_id'], msg, auto_escape)
    elif msgType == 'group':
        return send_msg (msgType, msgDict['group_id'], msg, auto_escape)
    else:
        myLogger.error('Not a legal message: {}'.format(msgDict))
        return 404, {}

# 撤回消息(OneBot_v11) 无返回信息
def delete_msg (msgId):
    resp = send_cqhttp_request('/delete_msg', {'message_id':msgId})
    return parse_cqhttp_resp(resp)

# 获取消息(go-cqhttp) 返回 time 时间, message_type 消息类型, message_id 消息id, real_id 消息真实id, sender 发送人信息, message 消息内容
def get_msg (msgId):
    resp = send_cqhttp_request('/get_msg', {'message_id':msgId})
    return parse_cqhttp_resp(resp)

# 获取合并转发消息(go-cqhttp) 返回 message 使用 消息的数组格式表示 的消息内容 每条消息内容包括 content 内容, sender 发送者, time 时间
def get_forward_msg (mid):
    resp = send_cqhttp_request('/get_forward_msg', {'id':mid})
    return parse_cqhttp_resp(resp)

# 发送合并转发(群)(go-cqhttp) 参数中 msgList 是一个消息列表 返回 message_id
def send_group_forward_msg(gid, msgList):
    resp = send_cqhttp_request('/send_group_forward_msg', {'group_id':gid, 'messages':msgList})
    return parse_cqhttp_resp(resp)

# 发送好友赞(OneBot_v11) 无返回信息
def send_like(uid, tm):
    resp = send_cqhttp_request('/send_like', {'user_id':uid, 'time':tm})
    return parse_cqhttp_resp(resp)

# 群组踢人(OneBot_v11) 无返回信息
def set_group_kick(gid, uid, reject_add_request = False):
    resp = send_cqhttp_request('/set_group_kick', {'user_id':uid, 'group_id':gid, 'reject_add_request':reject_add_request})
    return parse_cqhttp_resp(resp)

# 群组单人禁言(OneBot_v11) 无返回信息
def set_group_ban(gid, uid, duration = 3600):
    resp = send_cqhttp_request('/set_group_ban', {'user_id':uid, 'group_id':gid, 'duration':duration})
    return parse_cqhttp_resp(resp)

# 群组单人取消禁言(hakuBot) 无返回信息
def cancel_group_ban(gid, uid):
    return set_group_ban(gid, uid, 0)

# 群组匿名用户禁言(OneBot_v11) 无返回信息 暂不支持
def set_group_anonymous_ban():
    return 404, {}

# 群组全员禁言(OneBot_v11) 无返回信息
def set_group_whole_ban(gid, enable = True):
    resp = send_cqhttp_request('/set_group_whole_ban', {'group_id':gid, 'enable':enable})
    return parse_cqhttp_resp(resp)

# 群组取消全员禁言(hakuBot) 无返回信息
def cancel_group_whole_ban(gid):
    return set_group_whole_ban(gid, False)

# 群组设置管理员(OneBot_v11) 无返回信息
def set_group_admin(gid, uid, enable = True):
    resp = send_cqhttp_request('/set_group_admin', {'group_id':gid, 'user_id':uid, 'enable':enable})
    return parse_cqhttp_resp(resp)

# 群组取消管理员(hakuBot) 无返回信息
def cancel_group_admin(gid, uid):
    return set_group_admin(gid, uid, False)

# 群组匿名聊天(OneBot_v11) 无返回信息
def set_group_anonymous(gid, enable = True):
    resp = send_cqhttp_request('/set_group_anonymous', {'group_id':gid, 'enable':enable})
    return parse_cqhttp_resp(resp)

# 取消群组匿名聊天(hakuBot) 无返回信息
def cancel_group_anonymous(gid):
    return set_group_anonymous(gid, False)

# 设置群名片(OneBot_v11) 无返回信息
def set_group_card(gid, uid, card = ''):
    resp = send_cqhttp_request('/set_group_card', {'group_id':gid, 'user_id':uid, 'card':card})
    return parse_cqhttp_resp(resp)

# 删除群名片(hakuBot) 无返回信息
def cancel_group_card(gid, uid):
    return set_group_card(gid, uid)

# 设置群名(go-cqhttp) 无返回信息
def set_group_name(gid, nm):
    if len(nm) == 0:
        return 404, {}
    resp = send_cqhttp_request('/set_group_name', {'group_id':gid, 'group_name':nm})
    return parse_cqhttp_resp(resp)

# 设置群头像(go-cqhttp) cache=0 关闭缓存 i_file 支持file协议URL,网络URL,base64编码
def set_group_portrait(gid, i_file, cache=1):
    if len(i_file) == 0 or not (cache in [0, 1]):
        return 404, {}
    resp = send_cqhttp_request('/set_group_portrait', {'group_id':gid, 'file':i_file, 'cache':cache})
    return parse_cqhttp_resp(resp)

# 退出群组(OneBot_v11) 无返回信息
def set_group_leave(gid, is_dismiss = False):
    resp = send_cqhttp_request('/set_group_leave', {'group_id':gid, 'is_dismiss':is_dismiss})
    return parse_cqhttp_resp(resp)

# 解散群组(hakuBot) 无返回信息
def set_group_dismiss(gid):
    return set_group_leave(gid, True)

# 设置群组专属头衔(OneBot_v11) 无返回信息
def set_group_special_title(gid, uid, special_title = ''):
    resp = send_cqhttp_request('/set_group_special_title', {'group_id':gid, 'user_id':uid, 'special_title':special_title})
    return parse_cqhttp_resp(resp)

# 取消群组专属头衔(hakuBot) 无返回信息
def cancel_group_special_title(gid, uid):
    return set_group_special_title(gid, uid)

# 处理加好友请求(OneBot_v11) 无返回信息
def set_friend_add_request(flag, approve = True, remark = ''):
    if remark:
        resp = send_cqhttp_request('/set_friend_add_request', {'flag':flag, 'approve':approve, 'remark':remark})
    else:
        resp = send_cqhttp_request('/set_friend_add_request', {'flag':flag, 'approve':approve})
    return parse_cqhttp_resp(resp)

# 拒绝加好友请求(hakuBot) 无返回信息
def cancel_friend_add_request(flag):
    return set_friend_add_request(flag, False)

# 处理加群请求/邀请(OneBot_v11) 无返回信息
def set_group_add_request(flag, sub_type, approve = True, reason = ''):
    if reason:
        resp = send_cqhttp_request('/set_group_add_request', {'flag':flag, 'sub_type':sub_type, 'approve':approve, 'reason':reason})
    else:
        resp = send_cqhttp_request('/set_group_add_request', {'flag':flag, 'sub_type':sub_type, 'approve':approve})
    return parse_cqhttp_resp(resp)

# 拒绝加群请求/邀请(hakuBot) 无返回信息
def cancel_group_add_request(flag, sub_type, reason = ''):
    return set_group_add_request(flag, sub_type, False, reason)

# 获取登录号信息(OneBot_v11) 返回 user_id QQ号, nickname 昵称
def get_login_info():
    resp = send_cqhttp_request('/get_login_info', {})
    return parse_cqhttp_resp(resp)

# 获取陌生人信息(OneBot_v11) 返回 user_id QQ号, nickname 昵称, sex 性别, age 年龄
def get_stranger_info(uid, no_cache=False):
    resp = send_cqhttp_request('/get_stranger_info', {'user_id':uid, 'no_cache':no_cache})
    return parse_cqhttp_resp(resp)

# 获取好友列表(OneBot_v11) 返回数组 user_id QQ号, nickname 昵称, remark 备注名
def get_friend_list():
    resp = send_cqhttp_request('/get_friend_list', {})
    return parse_cqhttp_resp(resp)

# 获取用户VIP信息(go-cqhttp) 返回 user_id QQ号, nickname 用户昵称, level QQ等级, level_speed 等级加速度,
#                           vip_level 会员等级, vip_growth_speed 会员成长速度, vip_growth_total 会员成长总值
def get_vip_info(uid):
    resp = send_cqhttp_request('/_get_vip_info', {'user_id':uid})
    return parse_cqhttp_resp(resp)

# 获取群信息(OneBot_v11) 返回 group_id 群号, group_name 群名称, member_count 成员数, max_member_count 群容量
def get_group_info(gid, no_cache=False):
    resp = send_cqhttp_request('/get_group_info', {'group_id':gid, 'no_cache':no_cache})
    return parse_cqhttp_resp(resp)

# 获取群列表(OneBot_v11) 返回数组 group_id 群号, group_name 群名称, member_count 成员数, max_member_count 群容量
def get_group_list():
    resp = send_cqhttp_request('/get_group_list', {})
    return parse_cqhttp_resp(resp)

# 获取群成员信息(OneBot_v11)
# 返回 group_id 群号, user_id QQ号, nickname 昵称, card 群备注, sex 性别, age 年龄, area 地区
#      join_time 加群时间戳, last_sent_time 最后发言时间戳, level 成员等级, role 角色(owner, admin, member)
#      unfriendly 是否不良记录成员, title 专属头衔, title_expire_time 专属头衔过期时间戳, card_changeable 是否允许修改群名片
def get_group_member_info(gid, uid, no_cache=False):
    resp = send_cqhttp_request('/get_group_member_info', {'group_id':gid, 'user_id':uid, 'no_cache':no_cache})
    return parse_cqhttp_resp(resp)

# 获取群成员列表(OneBot_v11) 返回内容参考 get_group_member_info
def get_group_member_list(gid):
    resp = send_cqhttp_request('/get_group_member_list', {'group_id':gid})
    return parse_cqhttp_resp(resp)

# 发送群公告(go-cqhttp) 无返回消息
def send_group_notice(gid, msg):
    resp = send_cqhttp_request('/_send_group_notice', {'group_id':gid, 'content':msg})
    return parse_cqhttp_resp(resp)

# 获取群系统消息(go-cqhttp) 返回 invited_requests 邀请消息列表, join_requests 进群消息列表
# invited_requests 每个节点包括 request_id 请求id, invitor_uin 邀请者, invitor_nick 邀请者昵称, group_id 群号,
#                   group_name 群名, checked 是否已被处理, actor 处理者/未处理为0
# join_requests 每个节点包括 request_id 请求id, requester_uin 请求者id, requester_nick 请求者昵称, message 验证消息
#                 group_id 群号, group_name 群名, checked 是否已被处理, actor 处理者/未处理为0
def get_group_system_msg():
    resp = send_cqhttp_request('/get_group_system_msg', {})
    return parse_cqhttp_resp(resp)

# 获取群文件系统信息(go-cqhttp) 返回 file_count 文件总数, limit_count 文件上限, used_space 已使用空间, total_space 空间上限
def get_group_file_system_info(gid):
    resp = send_cqhttp_request('/get_group_file_system_info', {'group_id':gid})
    return parse_cqhttp_resp(resp)

# 获取群根目录文件列表(go-cqhttp) 返回 files 文件列表, folders 文件夹列表
# File字段包括 file_id 文件id, file_name 文件名, busid 文件类型, file_size 文件大小, upload_time 上传时间, dead_time 过期时间/永久0,
#              modify_time 最后修改时间, download_times 下载次数, uploader 上传者id, uploader_name 上传者名字
# Folder字段包括 folder_id 文件夹id, folder_name 文件名, create_time 创建时间, creator 创建者,
#               creator_name 创建者名字, total_file_count 子文件数量
def get_group_root_files(gid):
    resp = send_cqhttp_request('/get_group_root_files', {'group_id':gid})
    return parse_cqhttp_resp(resp)

# 获取群子目录文件列表(go-cqhttp) 返回 files 文件列表, folders 文件夹列表
def get_group_files_by_folder(gid, folderId):
    resp = send_cqhttp_request('/get_group_files_by_folder', {'group_id':gid, 'folder_id':folderId})
    return parse_cqhttp_resp(resp)

# 获取群文件资源链接(go-cqhttp) 返回 url 文件下载链接
def get_group_file_url(gid, fileId, busid):
    resp = send_cqhttp_request('/get_group_file_url', {'group_id':gid, 'file_id':fileId, 'busid':busid})
    return parse_cqhttp_resp(resp)

# 下载文件到缓存目录(go-cqhttp) 返回 file 下载文件的绝对路径
# headers格式: 字符串格式(注意[\r\n]为换行符) 'User-Agent=YOUR_UA[\r\n]Referer=https://localhost.localdomain'
#             json数组格式：
#                           [
#                               "User-Agent=YOUR_UA",
#                               "Referer=https://localhost.localdomain",
#                           ]
def download_file(fileUrl, threads, headers):
    resp = send_cqhttp_request('/download_file', {'url':fileUrl, 'thread_count':threads, 'headers':headers})
    return parse_cqhttp_resp(resp)

# 获取群at全体成员剩余次数(go-cqhttp) 返回 can_at_all 是否可以, remain_at_all_count_for_uin 剩余次数, remain_at_all_count_for_group 所有管理剩余次数
def get_group_at_all_remain(gid):
    resp = send_cqhttp_request('/get_group_at_all_remain', {'group_id':gid})
    return parse_cqhttp_resp(resp)

# 获取群消息历史记录(go-cqhttp) message_seq 为起始消息序号 可通过get_msg获得 返回 message 从起始序号开始的前19条消息列表
def get_group_msg_history(gid, message_seq):
    resp = send_cqhttp_request('/get_group_msg_history', {'group_id':gid, 'message_seq':message_seq})
    return parse_cqhttp_resp(resp)

# 获取群荣誉信息(OneBot_v11) infoType 为 (talkative, performer, legend, strong_newbie, emotion) 之一, 或 all 获取全部
# 返回 group_id 群号, current_talkative 当前龙王, talkative_list 历史龙王, performer_list 群聊之火
#       legend_list 群聊炽焰, strong_newbie_list 冒尖小春笋, emotion_list 快乐之源
# current_talkative 包括 user_id QQ号, nickname 昵称, avatar 头像URL, day_count 持续天数
# *_list            包括 user_id QQ号, nickname 昵称, avatar 头像URL, description 荣誉描述
def get_group_honor_info(gid, infoType):
    resp = send_cqhttp_request('/get_group_honor_info', {'group_id':gid, 'type':infoType})
    return parse_cqhttp_resp(resp)

# 获取Cookies(OneBot_v11) 返回 cookies Cookies
def get_cookies(domain):
    resp = send_cqhttp_request('/get_cookies', {'domain':domain})
    return parse_cqhttp_resp(resp)

# 获取CSRF Token(OneBot_v11) 返回 token CSRF Token
def get_csrf_token():
    resp = send_cqhttp_request('/get_csrf_token', {})
    return parse_cqhttp_resp(resp)

# 获取QQ相关接口凭证(OneBot_v11) 返回 cookies Cookies, token CSRF Token
def get_credentials(domain):
    resp = send_cqhttp_request('/get_credentials', {'domain':domain})
    return parse_cqhttp_resp(resp)

# 获取语音(OneBot_v11) 需要ffmpeg 返回 file 转换后的语音文件路径
def get_record(i_file, o_fmt):
    resp = send_cqhttp_request('/get_record', {'file':i_file, 'out_format':o_fmt})
    return parse_cqhttp_resp(resp)

# 获取图片(go-cqhttp) i_file 为图片缓存文件名 返回 size 图片源文件大小, filename 图片文件原名, file 图片下载地址
def get_image(i_file):
    resp = send_cqhttp_request('/get_image', {'file':i_file})
    return parse_cqhttp_resp(resp)

# 检查是否可以发送图片(OneBot_v11) 返回 yes 是或否
def can_send_image():
    resp = send_cqhttp_request('/can_send_image', {})
    return parse_cqhttp_resp(resp)

# 检查是否可以发送语音(OneBot_v11) 返回 yes 是或否
def can_send_record():
    resp = send_cqhttp_request('/can_send_record', {})
    return parse_cqhttp_resp(resp)

# 获取运行状态(go-cqhttp) 返回 online 当前在线, good 状态是否符合预期, stat 运行统计
#     下面的字段恒为True: app_initialized, app_enabled, plugins_good, app_good
# stat 运行统计包括下面的字段: packet_received 收到的数据包总数, packet_sent 发送的数据包总数, packet_lost 数据包丢失总数,
#                    message_received 接受信息总数, message_sent 发送信息总数, disconnect_times TCP链接断开次数, lost_times 账号掉线次数
def get_status():
    resp = send_cqhttp_request('/get_status', {})
    return parse_cqhttp_resp(resp)

# 获取版本信息(OneBot_v11) 识别go-cqhttp: {'go-cqhttp': True}
def get_version_info ():
    resp = send_cqhttp_request('/get_version_info', {})
    return parse_cqhttp_resp(resp)

# 重启bot(OneBot_v11) 无返回信息
def set_restart(delay = 0):
    resp = send_cqhttp_request('/set_restart', {'delay':delay})
    return parse_cqhttp_resp(resp)

# 清理缓存(OneBot_v11) 无返回信息
def clean_cache():
    resp = send_cqhttp_request('/clean_cache', {})
    return parse_cqhttp_resp(resp)

# 重载事件过滤器(go-cqhttp) 无返回信息
def reload_event_filter():
    resp = send_cqhttp_request('/reload_event_filter', {})
    return parse_cqhttp_resp(resp)

# 获取中文分词(go-cqhttp) 返回 slices 词组列表
def get_word_slices(content):
    resp = send_cqhttp_request('/.get_word_slices', {'content':content})
    return parse_cqhttp_resp(resp)

# 图片OCR(go-cqhttp) 仅支持接受的图片 返回 texts OCR结果列表, language 语言
# OCR结果列表 每个节点包括 text 文本, confidence 置信度, coordinates 坐标
def ocr_image(imageId):
    resp = send_cqhttp_request('/.ocr_image', {'image':imageId})
    return parse_cqhttp_resp(resp)


