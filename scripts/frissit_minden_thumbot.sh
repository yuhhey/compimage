#!/bin/bash

. /home/smb/SajatFejlesztes/FotoWorkflow/scripts/FotoWorkflow.conf


# Teljes update minden archivumból
for i in $FWF_HD_ARCHIVE_REGEXP
do
    ./update_thumbs.sh $i/IXUS970IS $i/CR2 $i/JPG $FWF_THUMBNAILS
done
