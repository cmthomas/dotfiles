#!/bin/sh

HOST=$(hostname -s)
UNAME=$(uname)
BASEDIR=$(dirname $0)

cd $BASEDIR
FILELIST="shared/*"
if [ -d host-$HOST ]; then
	FILELIST="$FILELIST host-$HOST/*"
	echo Including host-specific files for ${HOST}.
else
	echo No host-specific files for ${HOST}.
fi

echo
echo -n "Installing files... "

for item in $FILELIST; do
	if [ $(basename $item) = "config" ]; then
		mkdir $HOME/.config
		for xdgitem in $item/*; do
			ln -sf $PWD/$xdgitem $HOME/.config/$(basename $xdgitem)
		done

		continue
	fi

        if [ $(basename $item) = "bin" ]; then
		mkdir $HOME/bin
		for script in $item/*; do
			ln -sf $PWD/$script $HOME/bin/$(basename $script)
		done

		continue
	fi

	ln -sf $PWD/$item ~/.$(basename $item)
done
echo done.
