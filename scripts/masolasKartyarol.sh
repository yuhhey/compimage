#!/bin/bash

usage="$0 source destination"
DIRNOTEXIST=" - Directory does not exist: "

. /home/smb/SajatFejlesztes/FotoWorkflow/scripts/FotoWorkflow.conf

# A fájlnevek konverziója itt történik. A FAJLNEV változóban tárolja a konvertált fájlnevet.
convert_filename()
{
  FAJLNEV=`echo $1 | tr '[a-z] ' '[A-Z]_'`
}

CheckExistingFile()
{
  if [ ! -f "$FWF_FILE_LIST" ] ; then
# -follow nélkül a symlinkeket nem követi
      find "$cel" -follow -type f > "$FWF_FILE_LIST"
  fi
  grep $1 "$FWF_FILE_LIST" &> /dev/null
}

NemFuttat()
{
  let letezik=0
  let masolva=0
  for i in $forras/*
  do
    if [ ! -f "$i" ] ; then
      continue
    fi
    fajlnev=`basename "$i"`
    direktori=`stat "$i" | grep Módos | awk '{print $2}' | sed 's/-/_/g'`
    mkdir -p $cel/$direktori
    convert_filename "$fajlnev" # FAJLNEV változóban adja vissza az átalakított fájlnevet
    celfajl="$cel/$direktori/$FAJLNEV"
# Csak a yyyy_mm_dd/fajlnev stringet használjuk a keresésre, mivel az archivum
# több diszken és több mountpointon lehet, ezért a teljes path nem használható
    if  CheckExistingFile "$direktori/$FAJLNEV" ; then
#      echo $celfajl létezik
      let letezik++
    else
# Ha nincsen, akkor másoljuk
      cp -p "$i" $celfajl
      if [ 0 -ne $? ] ; then
        rm $celfajl
        echo nem sikerült a másolás: $celfajl
        exit
      fi
      let masolva++
    fi
  done
  echo Másolva: $masolva, Már az archivumban: $letezik
}

SetExifDateToTimeStamp()
{
  for i in $1/*.[Jj][Pp][Gg]
  do
    convert_filename `basename "$i"| tr '[a-z] ' '[A-Z]_'`
    FAJLNEV=$1/$FAJLNEV
# Ez FAT fájlrendszer alatt továbbra is hibát fog jelezni
    if [ ! -f "$FAJLNEV" ] ; then
      mv "$i" "$FAJLNEV" &> /dev/null
    fi
    jhead -ft $FAJLNEV >&/dev/null
  done

# CR2 canon RAW file-ok kezelése. Minden fájlt amelyiknek a végén 2-es van CR2nek értelmez.
# Ez nem baj addig, amíg csak a fényképezőről jövő fájlokat kezelünk
  for i in $1/*2
  do
    convert_filename `basename "$i"| tr '[a-z] ' '[A-Z]_'`
    FAJLNEV=$1/$FAJLNEV

# Valamiért mindig hibát jelez.
    if [ ! -f $FAJLNEV ] ; then
      mv "$i" $FAJLNEV &> /dev/null
    fi
    if [ -f "$FAJLNEV" ] ; then
      touch "$FAJLNEV" -t $(exifgrep DateTimeOriginal "$FAJLNEV" | sed "s/.* '//
s/:[0-9]\{2\}'//
s/[: ]//g")
    fi
  done
}

for arg
do
    case $arg in
	--unit-test)
	    return ;;
	--help)
	    echo $0 $usage
	    exit ;;
	--generate-archive-content)
	    if [ -f $FWF_FILE_LIST ] ; then
		rm $FWF_FILE_LIST
	    fi
	    CheckExistingFile pistike 
	    exit ;;
    esac
done

if [ 0 = $# ] ; then
 echo $usage
 exit
fi

forras="$1"
cel="$2"

if [ ! -d "$forras" ] ; then
  echo $0 $DIRNOTEXIST $forras
  exit
fi

if [ ! -d "$cel" ] ; then
  echo $0 $DIRNOTEXIST $cel
  exit
fi

forras=`cd "$forras" ; pwd`
cel=`cd "$cel"; pwd`

FWF_FILE_LIST=$cel/teljes_filelista

# Letöröljük az aktuális fájllistát, hogy a lehető legfrissebb legyen a dupla
# másolás elkerülése végett.
rm $FWF_FILE_LIST

#pushd $forras
SetExifDateToTimeStamp $forras
#popd
NemFuttat
