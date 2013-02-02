FAJL=`echo $1 | sed 's/\.//'`
MERET=`ls -b --block-size 1 -d -s "$1" | awk '{print $1}'`
printf "%14d %s\n" $MERET "$DVD_LABEL$FAJL"
