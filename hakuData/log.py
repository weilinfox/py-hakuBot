# 此源代码的使用受 GNU AFFERO GENERAL PUBLIC LICENSE version 3 许可证的约束, 您可以在下面的链接找到该许可证.
# https://github.com/weilinfox/py-hakuBot/blob/main/LICENSE

logDict = {
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
            'backupCount': 16,
            'level': 'DEBUG',
            'delay': False
        },
        'console':{
            'class':'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default'
        }
    },
    'loggers': {
            'werkzeug': {
                'handlers': ['file', 'console']
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

def init_log_path(lgp):
    global logDict
    logDict['handlers']['file']['filename'] = lgp + '/hakuBot.log'

def init_log_level(lvl, clvl):
    global logDict
    if not lvl in ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'):
        lvl = 'INFO'
    if not clvl in ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'):
        clvl = 'INFO'
    logDict['handlers']['file']['level'] = lvl
    logDict['handlers']['console']['level'] = clvl
