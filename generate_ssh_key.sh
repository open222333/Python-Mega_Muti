source `dirname -- "$0"`/.env

# 生成key不使用密碼 key存在則不做動作
< /dev/zero ssh-keygen -f $HOME/.ssh/$KEYNAME -N ''

ssh-copy-id -o StrictHostKeyChecking=no -i $HOME/.ssh/$KEYNAME.pub root@$KEY_TARGET_HOST