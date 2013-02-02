#!/bin/bash
# Az archivumban lévő fájlok nevét nagybetűsíti. Nem kell használni, ha csak
# a masolasKartyarol.sh scripttel másolunk fájlokat az archivumba.


fajl=$1

d=`dirname "$fajl"`
b="`basename "$fajl" | tr '[a-z ]' '[A-Z_]'`"
if [ "$fajl" = $d/$b ] ; then
    echo $fajl-t nem kell nagybetűsíteni
else
    mv -i "$fajl" $d/$b
fi

  
# find $konyvtar -type f -exec call nagybetusit.sh "{}" \;
