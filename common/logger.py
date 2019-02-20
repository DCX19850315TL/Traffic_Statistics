#!/usr/bin/env python
#_*_ coding:utf-8 _*_
'''
@author: tanglei
@contact: tanglei_0315@163.com
@file: logger.py
@time: 2019/1/23 15:33
'''
import os
import logging
import logging.config
import logging.handlers
import ConfigParser

#定义setting配置文件路径
setting_file = os.path.join(os.path.abspath('conf'),'setting.ini')
conf = ConfigParser.ConfigParser()
conf.read(setting_file)
#定义正常日志的文件路径
InfoFile = conf.get("logger","INFO_FILE")
#定义错误日志的文件路径
ErrorFile = conf.get("logger","ERROR_FILE")
#单个日志文件的大小
FileSize = int(conf.get("logger","FILE_SIZE"))
#轮训保留的日志文件个数
RotationNumber = int(conf.get("logger","ROTATION_NUMBER"))
def logger(level):

    if not os.path.isfile(InfoFile):
        open(InfoFile, "w+").close()
    if not os.path.isfile(ErrorFile):
        open(ErrorFile, "w+").close()

    #定义字典内容
    log_setting_dict = {"version":1,
                        "incremental":False,
                        "disable_existing_loggers":True,
                        "formatters":{"precise":
                                          {"format":"%(asctime)s %(filename)s(%(lineno)d - %(processName)s - %(threadName)s - %(funcName)s): %(levelname)s %(message)s",
                                           "datefmt":"%Y-%m-%d %H:%M:%S"}},
                        "handlers":{"handlers_RotatingFile_INFO":
                                        {"level": "INFO",
                                         "formatter": "precise",
                                         "class": "logging.handlers.RotatingFileHandler",
                                         "filename": InfoFile,
                                         "mode": "a",
                                         "maxBytes": FileSize*1024*1024,
                                         "backupCount": RotationNumber
                                         },
                                    "handlers_RotatingFile_ERROR":
                                        {"level": "ERROR",
                                         "formatter": "precise",
                                         "class": "logging.handlers.RotatingFileHandler",
                                         "filename": ErrorFile,
                                         "mode": "a",
                                         "maxBytes": FileSize * 1024 * 1024,
                                         "backupCount": RotationNumber
                                         }},
                        "loggers":{"logger_INFO":
                                       {"level":"INFO",
                                        "handlers":["handlers_RotatingFile_INFO"],},
                                   "logger_ERROR":
                                       {"level":"ERROR",
                                        "handlers": ["handlers_RotatingFile_ERROR"],}}}
    logging.config.dictConfig(log_setting_dict)

    if level == "INFO":
        logger = logging.getLogger("logger_INFO")
    elif level == "ERROR":
        logger = logging.getLogger("logger_ERROR")
    return logger

Logger_Info_file = logger("INFO")
Logger_Error_file = logger("ERROR")
#测试
a = [1,2]

try:
    print a[2]
except Exception,e:
    Logger_Error_file.exception(e)

'''
logger_INFO = logging.getLogger("logger_INFO")
logger_ERROR = logging.getLogger("logger_ERROR")
logger_INFO.info("aaaaaa")
logger_ERROR.error("bbbbbb")
logger_ERROR.exception("cccccc")
#测试程序
a = [0,1]
#向日志中输入异常日志
try:
    print a[3]
except Exception,e:
    logger_ERROR.exception(e)
#主动抛出一个异常，并写入到文件中。如果真实出现了异常还是将异常信息输入到文件，而不是自定义异常。
try:
    print a[1]
    raise Exception("a")
except Exception,e:
    logger_ERROR.exception(e)
'''