source `dirname -- "$0"`/.env

# 臨時備份目錄
OUT_DIR=`dirname -- "$0"`/db_bak_tmp

# 完整備份目錄路徑
TAR_DIR=`dirname -- "$0"`/db_bak_path

# 獲取當前系統時間
DATE=$(date +%Y%m%d%H%M)

# 若OUT_DIR不存在就建立
if [[ ! -e $OUT_DIR ]]; then
    mkdir $OUT_DIR
elif [[ ! -d $OUT_DIR ]]; then
    echo "$OUT_DIR already exists but is not a directory" 1>&2
fi

# 若TAR_DIR不存在就建立
if [[ ! -e $TAR_DIR ]]; then
    mkdir $TAR_DIR
elif [[ ! -d $TAR_DIR ]]; then
    echo "$TAR_DIR already exists but is not a directory" 1>&2
fi

# 最終保存的備份文件
TAR_BAK="mysqldb_bak_$HOSTNAME-$DATE.tar"

# 備份全部數據 若有帳密 則執行有帳密的指令
if [ $MYSQLDB_USER ]; then
	xtrabackup --user=$MYSQLDB_USER --password=$MYSQLDB_PASS --backup --target-dir=$OUT_DIR/$DATE
else
	echo "需要帳號密碼"
fi

# 打包為.tar格式
tar -cvf $TAR_DIR/$TAR_BAK -C$OUT_DIR $DATE

# 刪除暫存
if [[ -e $OUT_DIR/$DATE ]]
then
	echo "remove $OUT_DIR/$DATE" 1>&2
    rm -rf $OUT_DIR/$DATE
else
	echo "no $OUT_DIR/$DATE"
fi

# 刪除tar備份包$DAYS天前的備份文件
# find $TAR_DIR/ -mtime +$DAYS -name "*.tar" -exec rm -rf {} \;

# 使用key
if [ $USE_KEY ]; then
	if [ $USE_KEY == 1 ]; then
		if [[ ! -e $HOME/.ssh/$KEYNAME ]]; then
			sh `dirname -- "$0"`/generate_ssh_key.sh
		fi
	fi
fi

# 自動
if [ $AUTO_PASSWORD ]; then
	if [ $AUTO_PASSWORD == 1 ]; then
		if ! [ -x "$(command -v sshpass)" ]; then
			sh `dirname -- "$0"`/tool_install.sh sshpass
		fi
		rsync -Pav --temp-dir=/tmp --remove-source-files -e "sshpass -p$HOST_PASSWORD ssh" $TAR_DIR/$TAR_BAK root@$HOST:$TARGET_DIR
	else
		rsync -Pav --temp-dir=/tmp --remove-source-files -e ssh $TAR_DIR/$TAR_BAK root@$HOST:$TARGET_DIR
	fi
fi

exit
