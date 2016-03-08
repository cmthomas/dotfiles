#!/bin/sh

HOST=$(hostname -s)
UNAME=$(uname)
BASEDIR=$(dirname $0)

cd $BASEDIR

if [ $UNAME = "Linux" ]; then
	echo -n "Installing base Linux package set... "
	sudo apt-get install $(cat shared-Linux-package-list)
	echo done.

	if [ -f $HOST-Linux-package-list ]; then
		echo
		echo -n "Installing host-specific packages for ${HOST}... "
		sudo apt-get install $(cat $HOST-Linux-package-list)
		echo done.
	fi
fi

./update.sh

