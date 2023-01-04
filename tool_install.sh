if [ $2 ]; then
	PM_NAME=$2
else
	PM_NAME=$1
fi

if [ -x "$(command -v apt-get)" ]; then
	apt-get install $PM_NAME -y
elif [ -x "$(command -v yum)" ]; then
	yum install $PM_NAME -y
else
	echo "other"
fi
