from datetime import datetime
from mega import Mega
from time import sleep, time
from traceback import format_exc
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
import logging
import re
import os


try:
    # 關閉log
    DISABLE_LOG = int(os.environ.get('DISABLE_LOG'))
    # 設定紀錄log等級 預設DEBUG, DEBUG,INFO,WARNING,ERROR,CRITICAL
    LOG_DEBUG_LEVEL = os.environ.get('LOG_DEBUG_LEVEL', 'DEBUG')
except:
    format_exc()

try:
    LOG_SIZE = int(os.environ.get('LOG_SIZE'))
    LOG_DAYS = int(os.environ.get('LOG_DAYS'))
except:
    format_exc()

if DISABLE_LOG:
    logging.disable(logging.CRITICAL)

logger = logging.getLogger('mega備份')

if LOG_DEBUG_LEVEL == 'INFO':
    logger.setLevel(logging.INFO)
elif LOG_DEBUG_LEVEL == 'WARNING':
    logger.setLevel(logging.WARNING)
elif LOG_DEBUG_LEVEL == 'ERROR':
    logger.setLevel(logging.ERROR)
elif LOG_DEBUG_LEVEL == 'CRITICAL':
    logger.setLevel(logging.CRITICAL)
else:
    logger.setLevel(logging.DEBUG)

if not os.path.exists('logs'):
    os.makedirs('logs')

if LOG_SIZE:
    log_handler = RotatingFileHandler('logs/mega.log', maxBytes=LOG_SIZE, backupCount=5)
elif LOG_DAYS:
    log_handler = TimedRotatingFileHandler('logs/mega.log', when='D', backupCount=LOG_DAYS)
else:
    log_handler = TimedRotatingFileHandler('logs/mega.log', when='D', backupCount=7)

log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)


class MegaBackupFile:
    """上傳檔案至mega
    """

    def __init__(self, file_path: str, mega_folder: str = None, test=False) -> None:
        """_summary_

        Args:
            file_path (str): 路徑
            mega_folder (str): 上傳的資料夾名稱, Defaults to None.
            test (bool): 是否為測試. Defaults to False.
        """
        self.file_path = file_path

        self.mega_folder = mega_folder
        self.mega_folder_id = None

        self.chunk_size = 500000000
        self.expired_days = 7
        self.test = test

    def set_mega_auth(self, account: str, password: str):
        """
        設置帳號

        Args:
            account (str): mega 帳號
            password (str): mega 密碼
        """
        mega = Mega()
        self.mega_client = mega.login(account, password)

    def set_chunk_size(self, size: int):
        """設置分割檔案大小 byte

        Args:
            size (int): byte
        """
        self.chunk_size = size

    def set_expired_days(self, days: int):
        """設置過期天數

        Args:
            days (int): 天數
        """
        self.expired_days = days

    def set_mega_folder_id(self, mega_folder_id: str):
        """設置mega資料夾id

        Args:
            mega_folder_id (str): mega id
        """
        self.mega_folder_id = mega_folder_id

    def __get_time_str(self, total_secends: int) -> str:
        """依照秒數 回傳時間

        Args:
            total_secends (int): 總秒數

        Returns:
            str: 時間字串
        """
        msg = ''
        seconds = total_secends % 60
        minutes = (total_secends // 60) % 60
        hours = ((total_secends // 60) // 60) % 24
        days = ((total_secends // 60) // 60) // 24
        if days != 0:
            msg += f"{days}天"
        if hours != 0:
            msg += f"{hours}時"
        if minutes != 0:
            msg += f"{minutes}分"
        msg += f"{int(seconds)}秒"
        return msg

    def __get_date(self, timestamp: int, format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """使用時間戳取得日期格式

        Args:
            timestamp (int): 時間戳
            format (str): 日期格式, Defaults to "%Y-%m-%d %H:%M:%S".

        Returns:
            str: 回傳日期格式 預設 2019-05-10 23:40:00
        """
        return datetime.utcfromtimestamp(timestamp).strftime(format)

    def __print_msg(self, msg: str):
        """顯示訊息

        Args:
            msg (str): 訊息內容
        """
        logger.info(f'=== {msg} ===')

    def __split_file(self, path: str, chunk_size: int = 1024 * 1024 * 5, filename: str = None):
        """分割檔案

        Args:
            path (str): 檔案路徑
            chunk_size (str): 分割大小. Defaults to 500MB 1024 * 1024 * 5
            filename (str, optional): 檔名. Defaults to None.
        """
        file_number = 1

        if not filename:
            filename = os.path.basename(path)
        file_dir = os.path.dirname(path)

        self.__print_msg(f'分割 {filename} 開始')

        try:
            with open(path, 'rb') as f:
                chunk = f.read(chunk_size)
                while chunk:
                    split_file = f'{file_dir}/{filename}._{str(file_number)}'
                    with open(f"{split_file}.temp", 'wb') as chunk_file:
                        chunk_file.write(chunk)
                    os.rename(f"{split_file}.temp", split_file)
                    file_number += 1
                    chunk = f.read(chunk_size)
        except Exception as err:
            logger.error(err)

        self.__print_msg(f'分割 {filename} 結束')

    def __cat_files(self, path: str, filename: str = None):
        """合併檔案

        Args:
            path (str): 檔案路徑
            filename (str, optional): 檔名. Defaults to None.
        """
        if not filename:
            filename = os.path.basename(path)
        file_dir = os.path.dirname(path)

        self.__print_msg(f'合併 {filename} 開始')

        command = f'cat {file_dir}/{filename}* >> {file_dir}/{filename}'
        logger.info(command)
        os.system(command)

        self.__print_msg(f'合併 {filename} 結束')

    def __upload_to_mega(self, path: str):
        """上傳至mega

        Args:
            path (str): 檔案路徑

        Returns:
            _type_: 非測試時回傳上傳資訊
        """
        # 取得檔案大小 MB
        tar_size = round(os.path.getsize(path) / float(1000 * 1000), 2)
        filename = os.path.basename(path)

        self.__print_msg(f'上傳資料 {filename} 至 {self.mega_folder}, 檔案大小 {tar_size} MB')

        upload_start_time = time()

        mega_info = self.mega_client.upload(
            filename=path,
            dest=self.mega_folder_id,
            dest_filename=filename
        )

        upload_end_time = time()

        take_time = self.__get_time_str(int(round(upload_end_time - upload_start_time, 0)))
        self.__print_msg(f'上傳資料 {filename} 至 {self.mega_folder} 完成,耗時{take_time}')

        return mega_info

    def __remove_mega_file_by_private_id(self, private_id, filename=None):
        """根據 private_id 刪除mega上檔案

        Args:
            private_id (_type_): 檔案id
            filename (_type_, optional): 檔案名稱. Defaults to None.
        """
        if filename:
            filename = filename
        else:
            filename = private_id

        self.__print_msg(f'刪除mega上的 {filename} 開始')
        try:
            self.mega_client.destroy(private_id)
        except Exception as err:
            logger.error(err)
        self.__print_msg(f'刪除mega上的 {filename} 結束')

    def __remove_file(self, path: str):
        """刪除檔案

        Args:
            path (str): 檔案路徑
        """
        filename = os.path.basename(path)
        self.__print_msg(f'刪除 {filename} 開始')
        try:
            os.remove(path)
        except Exception as err:
            logger.error(err)
        self.__print_msg(f'刪除 {filename} 結束')

    def __get_mega_folder_files(self):
        """取得 指定mega資料夾內所有檔案資訊

        [mega.py API_INFO.md 詳細說明](https://github.com/odwyersoftware/mega.py/blob/master/API_INFO.md)
        """
        # folder_id = self.mega_client.find(self.mega_folder)[0]
        folder_id = self.mega_folder_id
        all_files = self.mega_client.get_files()
        folder_files = {}
        for _, file_info in all_files.items():
            if file_info['p'] == folder_id:
                folder_files[file_info['h']] = file_info
        return folder_files

    def __is_expired(self, file_ts: int) -> bool:
        """檢查是否超出設定的期限日期

        Args:
            file_ts (int): 檔案創建 時間戳

        Returns:
            bool: _description_
        """
        now = int(round(time()))
        sec = now - file_ts
        expired_sec = self.expired_days * 24 * 60 * 60

        if sec > expired_sec:
            return True
        return False

    def check_mega_files(self):
        """刪除過期的mega檔案
        """
        start = time()
        self.__print_msg(f'檢查已超過{self.expired_days}天的檔案')
        files = self.__get_mega_folder_files()
        for private_id, info in files.items():
            if self.__is_expired(info['ts']):
                self.__print_msg(f'{info["a"]["n"]} 創建日期{self.__get_date(info["ts"])} 已超過{self.expired_days}天')
                self.__remove_mega_file_by_private_id(private_id, info['a']['n'])
        end = time()
        self.__print_msg(f'檢查完畢 耗時{self.__get_time_str(int(round(end - start)))}')

    def run_split(self, path=None):
        """執行分割
        """
        if path == None:
            path = self.file_path

        if os.path.getsize(self.file_path) > self.chunk_size:
            # 分割檔案
            self.__split_file(self.file_path, self.chunk_size)

            # 非測試時 刪除檔案
            if not self.test:
                self.__remove_file(self.file_path)
        else:
            filename = os.path.basename(self.file_path)
            file_dir = os.path.dirname(self.file_path)
            os.rename(self.file_path, f"{file_dir}/{filename}._1")

    def run(self, path=None):
        """執行上傳
        """
        if path == None:
            path = self.file_path

        info = self.__upload_to_mega(path)
        # 非測試時
        logger.info(info)

        # 非測試時 刪除檔案
        if not self.test:
            self.__remove_file(path)


class MegaListen:
    """監聽資料夾 若有符合條間的檔案則執行上傳至mega
    """

    def __init__(self, dir_path: str, mega_account: str, mega_password: str, listen_type: int = 1, test=False) -> None:
        """_summary_

        Args:
            dir_path (str): 監聽路徑
            mega_account (str): mega帳號
            mega_password (str): mega密碼
            test (bool, optional): 是否為測試. Defaults to False.
            listen_type (int): 0: 'split', 1: 'upload', 2: 'check_expired_file' . Defaults to 1.
        """
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        type_dict = {
            0: 'split',
            1: 'upload',
            2: 'check_expired_file'
        }

        self.dir_path = dir_path

        self.schedule_quantity = None

        self.mega_account = mega_account
        self.mega_password = mega_password

        self.test = test
        self.listen_type = type_dict[listen_type]
        self.is_sleep = False
        self.file_extensions = None
        self.pattern = None

        self.expired_days = None

    def set_file_extension(self, *extension: str):
        """設置 篩選副檔名條件

        extension: 指定副檔名
        """
        self.file_extensions = extension

    def set_expired_days(self, days: int):
        """設置過期天數

        Args:
            days (int): 天數
        """
        self.expired_days = days

    def set_schedule_quantity(self, schedule_quantity: int):
        """設置 排程數量

        Args:
            schedule_quantity (int): 排程數量
        """
        self.schedule_quantity = schedule_quantity

    def set_pattern(self, pattern):
        """設置 匹配檔名 pattern

        Args:
            pattern (_type_): re規則
        """
        self.pattern = pattern

    def __check_extension(self, filename: str):
        """檢查 是否符合副檔名條件
        若無設置file_extensions 則回傳True

        Args:
            filename (str): 檔名

        Returns:
            bool: 是否符合副檔名條件
        """
        if self.file_extensions:
            _, file_extension = os.path.splitext(filename)
            return file_extension[1:] in self.file_extensions
        else:
            return True

    def __check_filename(self, filename: str):
        """檢查檔名是否匹配
        若無設置pattern 則回傳True

        Args:
            filename (str): 檔名

        Returns:
            _type_: _description_
        """
        if self.pattern:
            return re.search(self.pattern, filename)
        else:
            return True

    def listen(self, cannal_id=None):
        """執行監聽
        """
        while True:
            for file in os.listdir(self.dir_path):

                msg = {
                    'files': os.listdir(self.dir_path),
                    'file': file,
                    'check_filename': self.__check_filename(file),
                    'check_extension': self.__check_extension(file)
                }
                logger.info(msg)

                if self.__check_filename(file) and self.__check_extension(file):
                    if self.listen_type == 'upload':
                        if self.schedule_quantity > 0:
                            split_num = int(re.findall(r'\.tar\._(.*)', file)[0])
                            s_info = {
                                'split_num': split_num,
                                'schedule_quantity': self.schedule_quantity,
                                'cannal_id': cannal_id,
                                'remainder': split_num % self.schedule_quantity
                            }
                            logger.info(s_info)
                            if s_info['remainder'] == s_info['cannal_id']:
                                mbf = MegaBackupFile(f'{self.dir_path}/{file}', test=self.test)
                                mbf.set_mega_auth(self.mega_account, self.mega_password)
                                if self.expired_days:
                                    mbf.set_expired_days(self.expired_days)
                                mbf.run()
                        else:
                            mbf = MegaBackupFile(f'{self.dir_path}/{file}', test=self.test)
                            mbf.set_mega_auth(self.mega_account, self.mega_password)
                            if self.expired_days:
                                mbf.set_expired_days(self.expired_days)
                            mbf.run()
                    elif self.listen_type == 'split':
                        mbf = MegaBackupFile(f'{self.dir_path}/{file}', test=self.test)
                        mbf.run_split()
                    elif self.listen_type == 'check_expired_file':
                        mbf = MegaBackupFile(f'{self.dir_path}/{file}', test=self.test)
                        mbf.set_mega_auth(self.mega_account, self.mega_password)

                        if self.expired_days:
                            mbf.set_expired_days(self.expired_days)
                        # 刪除過期的mega檔案
                        mbf.check_mega_files()

                    self.is_sleep = False
            else:
                if not self.is_sleep:
                    self.is_sleep = True
                    print('等候中')
                sleep(1)
