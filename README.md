# py-hakuBot

- 小白不仅是机器人，也掌管了狸的大部分服务。 

hakuBot，利用go-cqhttp在大部分平台快速构建的qq机器人。

可以基于go-cqhttp的http报文格式自主扩展，使hakuBot也可以响应其他自定义事件。通过两级插件方便扩展和删减插件：第一级为通过 ``post_type`` 判断插件类型，调用 ``hakuRouter`` 下的对应模块处理；第二级为第一级插件模块调用 ``plugins`` 下的对应包中的插件，包名即第一级插件的模块名。

## 测试环境

| 系统 | 架构 | Python版本 |
|:---:|:---:|:--------:|
|Fedora 28 |mips64el |python 3.6|
|Loongnix 20|loongarch64|python 3.8|
|Arch Linux Arm |aarch64 |python 3.9|
|Arch Linux |x86_64 |python 3.9|
|Ubuntu 21.04|x86_64 |python 3.9|
|Windows 7 |x86_64 |python 3.9|
|Windows 10 |x86_64 |python 3.10|

首次运行，可以运行 ``test.py`` 检查环境是否可以正常运行 hakubot 。该测试会测试模块和必要的插件。

除了 python3 外， hakubot 还依赖 git 命令， Windows 环境下请注意环境变量的配置。

## 特色插件

| 插件名   |     功能            |
|:-------|:------------------:|
| debian  |   Debian 包查询    |
| ubuntu  |   Ubuntu 包查询    |
| arch    |   Archlinux 包查询 |
| loongnix|   Loongnix 包查询  |
| mao     |   毛主席语录        |
| marx    |   马克思主义        |
| rss     |   自定义群 rss 推送  | 
| baidu   |   百度搜索          |
| bing    |   必应搜索          |
| music   |   网易云音乐         |
| qqmusic |   QQ 音乐           |
| notice  |   自定义入群欢迎     |
| weather |   和风天气          |
| update  |   自主升级          |


## 快速上手

首次运行hakuBot会自动生成一个合法的 ``files`` 目录，其中包含了 ``keys.json`` ``config.json`` 两个初始配置文件。编辑初始配置文件后hakuBot即可与go-cqhttp正常通信。

## 插件开发

插件通常被放置在 ``plugins/message/`` 目录下。

``plugins/message/`` 目录下的插件通过go-cqhttp接收到的消息来调用，如 ``ping`` 插件通过类似 ``.ping`` 的指令调用。其中指令前的前导符号可以在 ``config.json`` 中设置。

### 最简单的插件

插件只需要一个具有一个参数的 ``main(msgDict)`` 即可，该函数返回一个字符串，hakuBot会将其作为回复发送。 ``msgDict`` 是go-cqhttp的报文内容，格式可以参考文档中的 “go-cqhttp 的报文示例” 一节。

比如最简单的 ``ping`` 命令，返回一个 ``pong``

```python
def main(msgDict):
    return 'Pong!'
```

插件也可以调用cqhttp和go-cqhttp的api，它们被定义在 ``hakuCore.cqhttpApi`` 模块中。函数名和api的终结点相同，但是以 ‘\_’ 开头的api，前导的 ‘\_’ 被去掉。

``hakuCore.cqhttpApi`` 模块中定义了所有 go-cqhttp api 以及不与其冲突的 OneBot v11 api ，并以函数的形式实现了部分常用的CQ码。

如果插件返回 ``None`` 或一个空字符串，则不会被发送。

### 插件初始化

插件只被载入一次，之后的每一次都是调用同一个插件对象下的 ``main()`` 。写在插件最外面的代码会在插件载入时执行一次，这可以作为插件的初始化，而数据可以被缓存。

比如下面的 ``ping`` 命令：

```python
cnt = 0

def main(msgDict):
	global cnt
	cnt += 1
    return f'Pong {cnt}!'
```

多次调用的返回将如下：

```
Pong 1!
Pong 2!
Pong 3!
...
```

注意hakuBot在自主升级时会重载所有除了 ``main.py`` 的模块和插件，此时插件会被重新初始化，即前面的代码中 ``cnt`` 被重新置0。

### 插件数据持久化

为了使插件的数据可以持久化存储，插件中可以设置一个函数 ``quit_plugin()`` 。它没有参数。如果存在，它会在hakuBot重载插件前被自动调用。 数据的持久化逻辑可以在插件中实现，也可以使用 ``hakuData.method`` 模块中已有的函数（已经实现csv和json）。

为了演示 ``quit_plugin()`` 的作用，简单修改了 ``ping`` 命令：

```python
cnt = 0

def main(msgDict):
	global cnt
	cnt += 1
    return f'Pong {cnt}!'

def quit_plugin():
    print('Quit ping plugin.')
```

多次调用以及重载时的返回和控制台打印将如下：

```
Pong 1!
Pong 2!
Pong 3!
Quit ping plugin.
# reload ping
Pong 1!
Pong 2!
Pong 3!
...
```

### 插件日志

日志的记录使用 ``logging`` 模块，其日志记录等级配置（在config.json中配置）是全局的。使用下面的代码创建一个和hakuBot相绑定的记录器：

```python
import logging
myLogger = logging.getLogger('hakuBot')
```

## 代码更新

hakuBot 具有一个代码更新插件 ``plugins/message/update.py`` ，可以通过调用该插件更新代码。

代码的更新通过在 hakuBot 根目录运行 ``git pull`` 并检查命令返回的退出码实现，若网络不佳则会一直运行直到退出码为 ``0`` 。随后该插件向 flask 发送 UPDATE http 请求，触发模块的重新载入。

如果更新后的代码出现运行错误导致无法再次调用该插件重新升级，则需要手动干预并通过运行 ``operate.py`` 发送 UPDATE 请求，示例如下：

```sh
python3 operate.py UPDATE
```

由于代码更新并不能更新主程序 ``main.py`` 的代码， flask 部分通常并不会被错误的更新损坏。

## 细节

### 主要模块和目录

``hakuCore`` 是hakuBot的核心，实现事件的分发给第一级插件（hakuCore/hakuMind）、cqhttp的api实现（hakuCore/cqhttpApi）、故障上报（hakuCore/report）； ``hakuData`` 实现对不同数据文件的操作（hakuData/method）、 ``logging`` 模块的配置（hakuData/log）、第一级插件的状态记录（hakuData/status）； ``hakuRouter`` 是第一级插件，插件名对应go-cqhttp中的 ``post_type`` 字段； ``plugins`` 是第二级插件，以第一级插件的插件名分包。

所有数据文件存放在 ``files`` 目录下的特定位置， ``files`` 目录是自动生成的，首次运行hakuBot会自动创建一个合法的目录结构，不存在但是被需要的配置文件会在首次读取时自动创建并写入默认配置。 ``files/config.json`` 记录了hakuBot的配置信息； ``files/json/`` 主要存放各个插件的配置信息，主要是权限信息；  ``files/log/`` 用于存放运行日志； ``files/csv/`` 和 ``files/sqlite/`` 的作用并没有被定义，主要用于插件实现数据的持久化。

主要模块和插件（即不包含 ``main.py``） 可以实现手动热重载，用于自主升级。主要模块对象名均加入到了 ``modules`` 集合中，它们的热重载正是通过遍历这个集合实现的，在集合中的顺序需要注意模块间的依赖关系。

### 插件

由于重载插件和数据持久化执行时需要所有其他插件相关的线程退出，插件不允许常驻内存。hakuBot并不会主动杀死线程，但是无法正常退出的线程会在自主升级时导致消息处理的停止。重载插件/退出程序时会自动执行每个插件下的 ``quit_plugin()`` 函数（如果存在），可以在其中执行数据持久化相关逻辑。

插件的重载通过 ``main.py`` 中的 ``pluginDict`` 实现，它通过 ``link_modules()`` 向 ``hakuCore/hakuMind`` 和 ``hakuCore/plugin`` 传递该字典， ``hakuCore/hakuMind`` 在载入第一级插件时将第一级插件记录其中， ``hakuCore/plugin`` 在载入第二级插件时将第二级插件记录其中。重载时重载 ``pluginDict`` 中的所有对象。因此所有第一级插件必须通过 ``hakuCore/plugin`` 调用第二级插件。

第一级插件（router）的状态对hakuBot的正常运行非常重要，因此指定了一个模块用于状态的统计，也就是 ``hakuData/status`` ，所有模块都可以注册并记录状态，其他插件可以随意调用其中的数据。注册插件要求其插件名是唯一的，如果注册时发现插件名并非唯一，会在日志中记录错误信息，但是并不保证修改状态记录时会被阻止（理论上插件名不唯一并不可能发生）。

### 插件权限

每个插件在 ``files/json/`` 目录中都对应一个配置文件，如果不存在则会在首次调用插件时自动创建。配置中的 ``auth`` 字段用于权限配置， 包含 ``allow_group`` ``allow_user`` ``block_group`` ``block_user`` ``no_error_msg`` 五个字段，用途为名称字面意思。其中当 ``no_error_msg`` 为 ``false`` 时将调用一个特殊的第二级插件： ``auth_failed`` 。

每次第一级插件调用第二级插件时都会通过 ``hakuData.method.get_plugin_config_json()`` 读取对应的配置并进行准入判断，如果判断失败则试图调用 ``auth_failed`` 。为了防止 ``auth_failed`` 被误触发，可以在其配置文件中置 ``allow_user`` 为 ``[0]``，  ``no_error_msg`` 为 ``true`` 。

注意 ``hakuRouter/meta_event`` 在调用群组设置的定时调用插件时 ``user_id`` 为 ``-1`` 。错误阻止这一id将造成群组定时调用插件失败。

### 调用 keys

如果插件调用了一些第三方api，可能需要key的支持。因此hakuBot设置了一个 ``keys.json`` 并在 ``hakuData/method`` 中提供了查找key的函数，可以使插件方便地调用。

### notice

``notice`` 是 hakuRouter 下的一级插件，用于管理群事件。实现的群事件包括群文件上传、入群欢迎、群运气王等。

该一级插件可能导致 bot 发送过多的消息，这可以通过 [notice](plugins/message/notice.py) 二级插件来配置。 ``notice`` 二级插件实现的功能包括自定义群欢迎信息以及 pastebin 功能、群文件上传提示功能和整个 ``notice`` 一级插件功能的打开和关闭，并使用 sqlite3 存储。

## go-cqhttp 的报文示例

### meta_event

```
{'interval': 5000, 'meta_event_type': 'heartbeat', 'post_type': 'meta_event', 'self_id': 27505, 'status': {'app_enabled': True, 'app_good': True, 'app_initialized': True, 'good': True, 'online': True, 'plugins_good': None, 'stat': {'packet_received': 17, 'packet_sent': 15, 'packet_lost': 0, 'message_received': 0, 'message_sent': 0, 'disconnect_times': 0, 'lost_times': 0}}, 'time': 1611308002}
```

### message

```
{'font': 0, 'message': '这是一个测试', 'message_id': 15945 'message_type': 'private', 'post_type': 'message', 'raw_message': '这是一个测试', 'self_id': 27505, 'sender': {'age': 0, 'nickname': '昵称', 'sex': 'unknown', 'user_id': 25218}, 'sub_type': 'friend', 'time': 16113, 'user_id': 25218}
```

