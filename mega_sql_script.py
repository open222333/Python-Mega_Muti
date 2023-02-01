from general.mega_backup import MegaListen
from pprint import pprint
from traceback import format_exc
import sys
import os


MEGA_ACCOUNT = os.environ.get('MEGA_ACCOUNT')
MEGA_PASSWORD = os.environ.get('MEGA_PASSWORD')
MEGA_LISTEN_DIR = os.environ.get('MEGA_LISTEN_DIR', '')
MEGA_TEST_FILE = os.environ.get('MEGA_TEST_FILE', '')
MEGA_EXPIRED_DAYS = os.environ.get('MEGA_EXPIRED_DAYS', None)
IS_TEST = os.environ.get('MEGA_LISTEN_IS_TEST', False)

argv_len = len(sys.argv)
if argv_len == 4:
    try:
        mega_upload_id = int(sys.argv[1])
        mega_schedule_quantity = int(sys.argv[2])
        listen_type = int(sys.argv[3])
    except Exception as e:
        print(e)

if MEGA_LISTEN_DIR == '':
    MEGA_LISTEN_DIR = 'target_dir'
    if not os.path.exists(MEGA_LISTEN_DIR):
        os.mkdir(MEGA_LISTEN_DIR)
else:
    MEGA_LISTEN_DIR = MEGA_LISTEN_DIR

try:
    if MEGA_EXPIRED_DAYS != None:
        MEGA_EXPIRED_DAYS = int(MEGA_EXPIRED_DAYS)
except TypeError as err:
    format_exc()

type_dict = {
    0: '分割',
    1: '上傳',
    2: '檢查過期'
}

setting_info = {
    'MEGA_ACCOUNT': MEGA_ACCOUNT,
    'MEGA_PASSWORD': MEGA_PASSWORD,
    'MEGA_TEST_FILE': MEGA_TEST_FILE,
    'MEGA_LISTEN_DIR': MEGA_LISTEN_DIR,
    'MEGA_EXPIRED_DAYS': MEGA_EXPIRED_DAYS,
    'TEST': IS_TEST,
    'LISTEN_TYPE': type_dict[listen_type],
    'UPLOAD_ID': mega_upload_id,
    'SCHEDULE_QUANTITY': mega_schedule_quantity
}

pprint(setting_info)

ml = MegaListen(
    dir_path=MEGA_LISTEN_DIR,
    mega_account=MEGA_ACCOUNT,
    mega_password=MEGA_PASSWORD,
    test=IS_TEST,
    listen_type=listen_type
)

if listen_type == 0:
    # 分割設定
    ml.set_file_extension('tar')
elif listen_type == 1:
    # 上傳設定
    ml.set_pattern(r'\.tar\._[\d]{1,10}')
elif listen_type == 2:
    # 過期天數設定
    ml.set_expired_days(MEGA_EXPIRED_DAYS)

ml.set_schedule_quantity(mega_schedule_quantity)
ml.listen(cannal_id=mega_upload_id)
