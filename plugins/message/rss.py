# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

# rss推送
# 实现自动推送需要配合 py-hakuBot 的定时命令功能
# 命令为 [index]rss send

import time
import requests
import feedparser
import threading
import hakuCore.cqhttpApi as hakuApi
import hakuData.method as hakuMethod
import hakuData.addBlock as hakuBlock

groupData = hakuMethod.read_dict_csv_file(
    hakuMethod.get_csv_file_by_name("rss", "group_rss"), ["id", "link"]
    )
userData = hakuMethod.read_dict_csv_file(
    hakuMethod.get_csv_file_by_name("rss", "user_rss"), ["id", "link"]
    )
userDict = dict()
groupDict = dict()
linkUser = dict()
linkGroup = dict()
latestMsg = dict()
errorLink = dict()
dataLock = threading.Lock()
for data in groupData:
    latestMsg[data['link']] = {'title':'', 'link': ''}
    if data['id'] in groupDict: groupDict[data['id']].append(data['link'])
    else: groupDict[data['id']] = [data['link']]
    if data['link'] in linkGroup: linkGroup[data['link']].append(data['id'])
    else: linkGroup[data['link']] = [data['id']]
for data in userData:
    latestMsg[data['link']] = {'title':'', 'link': ''}
    if data['id'] in userDict: userDict[data['id']].append(data['link'])
    else: userDict[data['id']] = [data['link']]
    if data['link'] in linkUser: linkUser[data['link']].append(data['id'])
    else: linkUser[data['link']] = [data['id']]

writeCsvLock = threading.Lock()
def write_csv_file(typeNum):
    if typeNum:
        fileName = hakuMethod.get_csv_file_by_name("rss", "group_rss")
        linkDict = groupData
    else:
        fileName = hakuMethod.get_csv_file_by_name("rss", "user_rss")
        linkDict = userData
    with writeCsvLock:
        hakuMethod.write_dict_csv_file(fileName, ["id", "link"], linkDict)

def main(msgDict):
    global userDict, groupDict, linkUser, linkGroup, latestMsg, errorLink
    timeNow = time.time()
    com = msgDict['message'].split()
    if len(com) < 2 or com[1] == 'help':
        return '''小白的rss订阅:
list 查看所有订阅
add link 添加一条订阅
del No. 删除一条订阅
test 检测订阅是否正常
'''
    if com[1] == 'send':
        for lnk in latestMsg.keys():
            feedDict = feedparser.parse(lnk)
            feedMsg = list()
            if len(feedDict.entries) == 0:
                if lnk in errorLink:
                    if timeNow - errorLink[lnk] >= 48*3600:
                        feedMsg.append(f'链接 {lnk} 已经连续两天无法正常拉取消息了欸，要删了它咩？')
                        errorLink[lnk] = time.time()
                else:
                    errorLink[lnk] = timeNow
            else:
                if lnk in errorLink:
                    errorLink.pop(lnk)
                if latestMsg[lnk]['title']:
                    sendMax = min(len(feedDict.entries), 5)
                    for i in range(sendMax):
                        if latestMsg[lnk]['title'] == feedDict.entries[i].title:
                            break
                        elif timeNow - time.mktime(feedDict.entries[i].updated_parsed) + time.altzone > 300:
                            break
                        newMsg = f'{feedDict.entries[i].title}\n摘要: {feedDict.entries[i].summary}'
                        if not hakuBlock.has_block_word(newMsg):
                            feedMsg.append(newMsg.replace(feedDict.entries[i].link, ''))
                            feedMsg.append(feedDict.entries[i].link)
                    latestMsg[lnk]['title'] = feedDict.entries[0].title
                    latestMsg[lnk]['link'] = feedDict.entries[0].link
                else:
                    latestMsg[lnk]['title'] = feedDict.entries[0].title
                    latestMsg[lnk]['link'] = feedDict.entries[0].link
                    # print(timeNow - time.mktime(feedDict.entries[0].updated_parsed) + time.altzone)
                    if timeNow - time.mktime(feedDict.entries[0].updated_parsed) + time.altzone <= 300:
                        newMsg = f'{feedDict.entries[0].title}\n摘要: {feedDict.entries[0].summary}'
                        if not hakuBlock.has_block_word(newMsg):
                            feedMsg.append(newMsg.replace(feedDict.entries[0].link, ''))
                            feedMsg.append(feedDict.entries[0].link)
                    # print(feedMsg)
            for qid in linkUser.get(lnk, []):
                for msg in feedMsg:
                    hakuApi.send_private_msg(qid, msg)
            for qid in linkGroup.get(lnk, []):
                for msg in feedMsg:
                    hakuApi.send_group_msg(qid, msg)
    elif com[1] == 'list':
        ans = 'No.  link'
        n = 0
        if msgDict['message_type'] == 'private':
            if str(msgDict['user_id']) in userDict:
                userLink = userDict[str(msgDict['user_id'])]
            else:
                return '小白这里没有你的记录欸'
        else:
            if str(msgDict['group_id']) in groupDict:
                userLink = groupDict[str(msgDict['group_id'])]
            else:
                return '小白这里没有你的记录欸'
        for lnk in userLink:
            ans += f'\n{n}  {lnk}'
            n += 1
        return ans
    elif com[1] == 'test':
        if msgDict['message_type'] == 'private':
            if str(msgDict['user_id']) in userDict:
                userLink = userDict[str(msgDict['user_id'])]
            else:
                return '小白这里没有你的记录欸'
        else:
            if str(msgDict['group_id']) in groupDict:
                userLink = groupDict[str(msgDict['group_id'])]
            else:
                return '小白这里没有你的记录欸'
        ans = 'No.  状态'
        pos = 0
        for lnk in userLink:
            feedDict = feedparser.parse(lnk)
            try:
                if feedDict.status == 200:
                    if len(feedDict.entries):
                        ans += f'\n{pos} 正常'
                    else:
                        ans += f'\n{pos} 似乎不是一个推送链接'
                else:
                    ans += f'\n{pos} 发现错误:{feedDict.status}'
            except:
                ans += f'\n{pos} 似乎不是一个正常的链接'
            pos += 1
        return ans
    elif com[1] == 'add':
        if len(com) < 3: return '小白不知道你要添加什么 [CQ:face,id=176]'
        nLink = com[2]
        if msgDict['message_type'] == 'private':
            qid = str(msgDict['user_id'])
            if not qid in userDict:
                userDict[qid] = []
            userLink = userDict[qid]
            linkId = linkUser
            editData = userData
            writeType = 0
        else:
            qid = str(msgDict['group_id'])
            if not qid in groupDict:
                groupDict[qid] = []
            userLink = groupDict[qid]
            linkId = linkGroup
            editData = groupData
            writeType = 1
        if nLink in userLink: return '这个链接好像已经存在了欸'
        userLink.append(nLink)
        if nLink in linkId: linkId[nLink].append(qid)
        else: linkId[nLink] = [qid]
        with dataLock:
            editData.append({'id':qid, 'link':nLink})
            write_csv_file(writeType)
        return f'{nLink} 添加成功, 用 test 命令测试是否正常哦~'
    elif com[1] == 'del':
        if len(com) < 3: return '小白不知道你要删除什么 [CQ:face,id=176]'
        try:
            nLink = int(com[2])
        except ValueError:
            return 'del 命令需要一个行号, 通过 list 查看行号 [CQ:face,id=179]'
        if msgDict['message_type'] == 'private':
            qid = str(msgDict['user_id'])
            if not qid in userDict: return '好像没有什么可以删除的'
            userLink = userDict[qid]
            linkId = linkUser
            editData = userData
            writeType = 0
        else:
            qid = str(msgDict['group_id'])
            if not qid in groupDict: return '好像没有什么可以删除的'
            userLink = groupDict[qid]
            linkId = linkGroup
            editData = groupData
            writeType = 1
        if nLink < 0 or nLink >= len(userLink):
            return '小白奇了怪了, 你哪里有这个行号 [CQ:face,id=176]'
        delLink = userLink.pop(nLink)
        linkId[delLink].remove(qid)
        with dataLock:
            delPos = 0
            for dct in editData:
                if dct['id'] == qid and dct['link'] == delLink:
                    break
                delPos += 1
            editData.pop(delPos)
            write_csv_file(writeType)
        return f'订阅 {delLink} 删除成功~'
    else:
        return '小白不知道这要干什么欸'
