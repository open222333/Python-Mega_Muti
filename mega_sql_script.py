from general.mega_backup import MegaListen
from pprint import pprint
import sys
import os


MEGA_ACCOUNT = os.environ.get('MEGA_ACCOUNT')
MEGA_PASSWORD = os.environ.get('MEGA_PASSWORD')
MEGA_LISTEN_DIR = os.environ.get('MEGA_LISTEN_DIR', '')
MEGA_TEST_FILE = os.environ.get('MEGA_TEST_FILE', '')
IS_TEST = os.environ.get('MEGA_LISTEN_IS_TEST', False)

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

setting_info = {
    'MEGA_ACCOUNT': MEGA_ACCOUNT,
    'MEGA_PASSWORD': MEGA_PASSWORD,
    'MEGA_TEST_FILE': MEGA_TEST_FILE,
    'MEGA_LISTEN_DIR': MEGA_LISTEN_DIR,
    'TEST': IS_TEST,
    'UPLOAD': bool(is_upload),
    'UPLOAD_ID': mega_upload_id,
    'SCHEDULE_QUANTITY': mega_schedule_quantity
}

pprint(setting_info)

ml = MegaListen(
    dir_path=MEGA_LISTEN_DIR,
    mega_account=MEGA_ACCOUNT,
    mega_password=MEGA_PASSWORD,
    test=IS_TEST,
    upload=bool(is_upload)
)

if setting_info['UPLOAD']:
    ml.set_pattern(r'\.tar\._[\d]{1,10}')
else:
    ml.set_file_extension('tar')

ml.set_schedule_quantity(mega_schedule_quantity)
ml.listen(cannal_id=mega_upload_id)
