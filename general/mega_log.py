from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
from traceback import format_exc
from datetime import datetime
import logging
import os


try:
    LOG_PATH = os.environ.get('LOG_PATH', 'logs')

    # 關閉log
    LOG_DISABLE = os.environ.get('LOG_DISABLE', False)
    if LOG_DISABLE == 'true' or LOG_DISABLE == 'True' or LOG_DISABLE == '1':
        LOG_DISABLE = True

    # 關閉記錄檔案
    LOG_FILE_DISABLE = os.environ.get('LOG_FILE_DISABLE', False)
    if LOG_FILE_DISABLE == 'true' or LOG_FILE_DISABLE == 'True' or LOG_FILE_DISABLE == '1':
        LOG_FILE_DISABLE = True

    # 設定紀錄log等級 預設WARNING, DEBUG,INFO,WARNING,ERROR,CRITICAL
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING')

    # 指定log大小(輸入數字) 單位byte
    LOG_SIZE = int(os.environ.get('LOG_SIZE', 0))
    # 指定保留log天數(輸入數字) 預設7
    LOG_DAYS = int(os.environ.get('LOG_DAYS', 7))
except Exception as err:
    format_exc()

# 建立log資料夾
if not os.path.exists(LOG_PATH) and not LOG_DISABLE:
    os.makedirs(LOG_PATH)

if LOG_DISABLE:
    logging.disable()
else:
    if LOG_SIZE:
        log_file = f'{LOG_PATH}/mega.log'
        log_file_handler = RotatingFileHandler(f'logs/{log_file}.log', maxBytes=LOG_SIZE, backupCount=5)
    else:
        log_file = f'{LOG_PATH}/{datetime.now().__format__("%Y%m%d")}.log'
        log_file_handler = TimedRotatingFileHandler(log_file, when='D', backupCount=LOG_DAYS)

    log_msg_handler = logging.StreamHandler()

    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file_handler.setFormatter(log_formatter)
    log_msg_handler.setFormatter(log_formatter)

    logger = logging.getLogger('test')

    if LOG_LEVEL == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    elif LOG_LEVEL == 'INFO':
        logger.setLevel(logging.INFO)
    elif LOG_LEVEL == 'WARNING':
        logger.setLevel(logging.WARNING)
    elif LOG_LEVEL == 'ERROR':
        logger.setLevel(logging.ERROR)
    elif LOG_LEVEL == 'CRITICAL':
        logger.setLevel(logging.CRITICAL)

    if not LOG_FILE_DISABLE:
        logger.addHandler(log_file_handler)
    logger.addHandler(log_msg_handler)
