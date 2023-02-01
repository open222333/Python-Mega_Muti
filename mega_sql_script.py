from general.mega_backup import MegaListen
from pprint import pprint
from traceback import format_exc
import sys
import os


MEGA_ACCOUNT = os.environ.get('MEGA_ACCOUNT')
MEGA_PASSWORD = os.environ.get('MEGA_PASSWORD')
MEGA_LISTEN_DIR = os.environ.get('MEGA_LISTEN_DIR', '')
MEGA_EXPIRED_DAYS = os.environ.get('MEGA_EXPIRED_DAYS', None)

argv_len = len(sys.argv)
if argv_len == 4:
    try:
        mega_upload_id = int(sys.argv[1])
        mega_schedule_quantity = int(sys.argv[2])
        is_upload = int(sys.argv[3])
    except Exception as e:
        print(e)

if MEGA_LISTEN_DIR == '':
    MEGA_LISTEN_DIR = f'{os.path.dirname(__file__)}/target_dir'
    os.mkdir(MEGA_LISTEN_DIR)
else:
    MEGA_LISTEN_DIR = MEGA_LISTEN_DIR

try:
    if MEGA_EXPIRED_DAYS != None:
        MEGA_EXPIRED_DAYS = int(MEGA_EXPIRED_DAYS)
except TypeError as err:
    format_exc()

setting_info = {
    'MEGA_ACCOUNT': MEGA_ACCOUNT,
    'MEGA_PASSWORD': MEGA_PASSWORD,
    'MEGA_LISTEN_DIR': MEGA_LISTEN_DIR,
    'MEGA_EXPIRED_DAYS': MEGA_EXPIRED_DAYS,
    'UPLOAD': bool(is_upload),
    'UPLOAD_ID': mega_upload_id,
    'SCHEDULE_QUANTITY': mega_schedule_quantity
}

pprint(setting_info)

ml = MegaListen(
    dir_path=MEGA_LISTEN_DIR,
    mega_account=MEGA_ACCOUNT,
    mega_password=MEGA_PASSWORD,
    upload=bool(is_upload)
)

if setting_info['UPLOAD']:
    ml.set_pattern(r'\.tar\._[\d]{1,10}')
else:
    ml.set_file_extension('tar')

# 過期天數設定
ml.set_expired_days(MEGA_EXPIRED_DAYS)

ml.set_schedule_quantity(mega_schedule_quantity)
ml.listen(cannal_id=mega_upload_id)
