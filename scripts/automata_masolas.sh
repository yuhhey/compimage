#!/bin/bash

. /home/smb/SajatFejlesztes/FotoWorkflow/scripts/FotoWorkflow.conf


# Teljes update minden archivumból
UpdateKepek ()
{
    for i in $FWF_HD_ARCHIVE_REGEXP
    do
	./update_thumbs.sh $i/IXUS970IS $i/CR2 $i/JPG $FWF_THUMBNAILS
    done
}    

# Csak nagyon szimplán, mindent bedrótozva

while [ 1 == 1 ]
do
    konyvtar=`./a.out /media`
#    echo finally something to do...
    sleep 0.2
    case "$konyvtar" in
      $FWF_SD_MOUNTPOINT)
	forras=$FWF_HD_ARCHIVE/$FWF_SD_MOUNTPOINT/dcim/100canon
	cel=$FWF_TARGET_IXUS970IS ;;
      SYMLINK_$FWF_SD_MOUNTPOINT)
	forras=$FWF_HD_ARCHIVE/$konyvtar
	cel=$FWF_TARGET_IXUS970IS ;;
      $FWF_CF_MOUNTPOINT)
	forras=$FWF_HD_ARCHIVE/$FWF_CF_MOUNTPOINT/dcim/771canon
	cel=$FWF_TARGET_CR2 ;;
      SYMLINK_$FWF_CF_MOUNTPOINT)
	forras=$FWF_HD_ARCHIVE/$konyvtar
	cel=$FWF_TARGET_CR2 ;;
      $FWF_HG10_MOUNTPOINT)
        pushd $FWF_TARGET_HG10
	cel=`date +%Y_%m_%d`
	mkdir $cel
	rsync -av $FWF_HD_ARCHIVE/$FWF_HG10_MOUNTPOINT/avchd/ $cel
	popd 
	continue ;;
      ASUSMMBackup)
	pushd /media/ASUSMMBackup
        rsync -av /media/ASUSWL700gE/{Zene,filmek} .
	popd
	continue ;;
# Hibakezelés
	*failed*)
	    echo Notifier error
	    exit ;;
# Egyéb /media - beli események
	*)
	    echo Új könyvár: /media/$konyvtar
		echo Nincs vele teendő
	    continue ;;
    esac
    echo Másolas indul: $forras-\>$cel
    ./masolasKartyarol.sh $forras $cel
    Xdialog --title "Nyúlő!!!" --msgbox "Vedd ki a kártyát" 10 50 &
    echo Másolás vége.
    echo update file list
    ./masolasKartyarol.sh --generate-archive-content
    echo Frissítem a kis képeket. Ez eltarthat egy darabig
    ./update_thumbs.sh $FWF_TARGET_IXUS970IS $FWF_TARGET_CR2 $FWF_TARGET_JPG $FWF_THUMBNAILS

    echo Go back sleeping...
done
