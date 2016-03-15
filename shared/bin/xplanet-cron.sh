#!/bin/sh

rm -f $HOME/Pictures/xplanet.png
rm -f $HOME/Pictures/xplanet-out.png

. $HOME/bin/location.sh

xplanet -projection rectangular -date_format "%a %e %b %Y %H:%M UT" -geometry 1920x1040 -gmtlabel -labelpos +5+5 -latitude $LATITUDE -longitude $LONGITUDE -num_times 1 -config $HOME/.xplanet/xplanet.conf -output $HOME/Pictures/xplanet.png

if [ $NUM_DISPLAYS -eq 1 ]; then
	mv $HOME/Pictures/xplanet.png $HOME/Pictures/xplanet-out.png
elif [ $NUM_DISPLAYS -eq 2 ]; then
	montage -tile x1 -geometry x1040 $HOME/Pictures/xplanet.png $HOME/Pictures/xplanet.png $HOME/Pictures/xplanet-out.png
fi

DISPLAY=:0.0 feh --no-xinerama --bg-center $HOME/Pictures/xplanet-out.png
