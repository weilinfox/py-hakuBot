# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

__log_config = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(filename)s line %(lineno)d: %(message)s'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': './hakuBot.log',
            'maxBytes': 1000000,
            'backupCount': 64,
            'level': 'DEBUG',
            'delay': False
        },
        'console':{
            'class':'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default'
        },
        'flask_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': './hakuBot_flask.log',
            'maxBytes': 1000000,
            'backupCount': 16,
            'level': 'DEBUG',
            'delay': False
        },
        'flask_console':{
            'class':'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default'
        }
    },
    'loggers': {
            'werkzeug': {
                'handlers': ['flask_file', 'flask_console']
            },
            'hakuBot': {
                'handlers': ['file', 'console']
            }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': []
    }
}


def init_log_path(path):
    """
    配置日志文件目录
    :param path: 绝对路径
    """
    global __log_config
    __log_config['handlers']['file']['filename'] = path + '/hakuBot.log'
    __log_config['handlers']['flask_file']['filename'] = path + '/hakuBot.log'


def init_log_level(level, console_level):
    """
    配置日志文件等级
    :param level: 日志等级
    :param console_level: 终端日志等级
    """
    global __log_config
    if level not in ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'):
        level = 'INFO'
    if console_level not in ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'):
        console_level = 'INFO'
    __log_config['handlers']['file']['level'] = level
    __log_config['handlers']['console']['level'] = console_level


def init_flack_log_level(level, console_level):
    """
    配置终端打印日志等级
    :param level: 日志等级
    :param console_level: 终端日志等级
    """
    global __log_config
    if level not in ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'):
        level = 'INFO'
    if console_level not in ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'):
        console_level = 'INFO'
    __log_config['handlers']['flask_file']['level'] = level
    __log_config['handlers']['flask_console']['level'] = console_level


def get_log_dict():
    return __log_config
