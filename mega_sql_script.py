from general.mega_backup import MegaListen, logger
import sys
import os


MEGA_ACCOUNT = os.environ.get('MEGA_ACCOUNT')
MEGA_PASSWORD = os.environ.get('MEGA_PASSWORD')
MEGA_LISTEN_DIR = os.environ.get('MEGA_LISTEN_DIR', None)
MEGA_EXPIRED_DAYS = os.environ.get('MEGA_EXPIRED_DAYS', None)

argv_len = len(sys.argv)
if argv_len == 4:
    try:
        mega_upload_id = int(sys.argv[1])
        mega_schedule_quantity = int(sys.argv[2])
        listen_type = int(sys.argv[3])
    except Exception as e:
        logger.error(e)

if not MEGA_LISTEN_DIR:
    try:
        MEGA_LISTEN_DIR = 'target_dir'
        if not os.path.exists(MEGA_LISTEN_DIR):
            os.mkdir(MEGA_LISTEN_DIR)
    except Exception as err:
        logger.error(err)
else:
    MEGA_LISTEN_DIR = MEGA_LISTEN_DIR

try:
    if MEGA_EXPIRED_DAYS != None:
        MEGA_EXPIRED_DAYS = int(MEGA_EXPIRED_DAYS)
except Exception as err:
    logger.error(err)

type_dict = {
    0: '分割',
    1: '上傳',
    2: '檢查過期'
}

setting_info = {
    'MEGA帳號': MEGA_ACCOUNT,
    'MEGA密碼': MEGA_PASSWORD,
    '監聽功能': type_dict[listen_type]
}

ml = MegaListen(
    dir_path=MEGA_LISTEN_DIR,
    mega_account=MEGA_ACCOUNT,
    mega_password=MEGA_PASSWORD,
    listen_type=listen_type
)

if listen_type == 0:
    # 分割設定
    ml.set_file_extension('tar')
elif listen_type == 1:
    # 上傳設定
    ml.set_pattern(r'\.tar\._[\d]{1,10}')
    setting_info['監聽資料夾'] = MEGA_LISTEN_DIR
    setting_info['上傳 ID'] = mega_upload_id
    setting_info['上傳 執行總數'] = mega_schedule_quantity
elif listen_type == 2:
    # 過期天數設定
    ml.set_expired_days(MEGA_EXPIRED_DAYS)
    setting_info['保留天數'] = MEGA_EXPIRED_DAYS

logger.info(setting_info)

ml.set_schedule_quantity(mega_schedule_quantity)
ml.listen(cannal_id=mega_upload_id)
