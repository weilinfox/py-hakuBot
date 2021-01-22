# py-hakuBot

- 小白不仅是机器人，也掌管了狸的大部分服务。 

hakuBot，利用go-cqhttp在龙芯和其他平台快速构建的qq机器人。

可以基于go-cqhttp的http报文格式自主扩展，使hakuBot也可以响应其他自定义事件。通过两级插件方便扩展和删减插件：第一级为通过 ``post_type`` 判断插件类型，调用 ``hakuRouter`` 下的对应模块处理；第二级为第一级插件模块调用 ``plugins`` 下的对应包中的插件，包名即第一级插件的模块名。

非插件的模块名请手动加入到 ``main.py`` 的 ``modules`` 集合中，加载的插件会自动加入集合。该集合用于更新后的自动模块重载。

``hakuCore`` 是hakuBot的核心， ``hakuData`` 实现对不同数据文件的操作。所有数据文件存放在 ``files`` 目录下的特定位置，且首次运行hakuBot会自动创建一个合法的目录结构。 ``files/config.json`` 记录了hakuBot的配置信息； ``files/json/`` 主要存放各个插件的配置信息，主要是权限信息；  ``files/log/`` 用于存放运行日志； ``files/csv/`` 和 ``files/sqlite/`` 的作用并没有被定义，主要用于插件实现数据的持久化。

由于重载插件和数据持久化执行时需要所有其他插件相关的线程退出，插件不允许常驻内存。如果发现插件超过一分钟仍未退出，将会被强制退出。重载插件/退出程序时会自动执行每个插件下的 ``quit_plugin()`` 函数（如果存在），可以在其中执行数据持久化相关逻辑。

插件的重载通过 ``main.py`` 中的 ``pluginDict`` 实现，它通过 ``link_modules()`` 向第一级插件传递该字典，第一级插件在载入插件时将插件的模块对象记录其中。重载时重载其中的所有对象。因此所有第一级插件必须包含一个 ``link_modules()`` 函数，并在载入新插件时以 ``{<模块名>:<模块对象>}`` 的方式向其中添加字段。


{'interval': 5000, 'meta_event_type': 'heartbeat', 'post_type': 'meta_event', 'self_id': 27505, 'status': {'app_enabled': True, 'app_good': True, 'app_initialized': True, 'good': True, 'online': True, 'plugins_good': None, 'stat': {'packet_received': 17, 'packet_sent': 15, 'packet_lost': 0, 'message_received': 0, 'message_sent': 0, 'disconnect_times': 0, 'lost_times': 0}}, 'time': 1611308002}

{'font': 0, 'message': '这是一个测试', 'message_id': 15945 'message_type': 'private', 'post_type': 'message', 'raw_message': '这是一个测试', 'self_id': 27505, 'sender': {'age': 0, 'nickname': '昵称', 'sex': 'unknown', 'user_id': 25218}, 'sub_type': 'friend', 'time': 16113, 'user_id': 25218}
