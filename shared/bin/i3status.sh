#!/bin/sh

i3status -c $HOME/.i3status.conf | while :; do
	read line
	echo "$(cat $HOME/.swreport)^fg(#333333)^p(5;-2)^ro(2)^p()^fg()^p(5)$line" || exit 1
done
