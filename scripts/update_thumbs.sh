#!/bin/bash
# Thumbokat kreal az IXUS970IS képeiből, lebutítja a JPG-et galéria használatra

# $Id: update_thumbs.sh 86 2010-03-28 12:00:01Z smb $

# $1: input directory, JPG fájlokkal
# $2: input directory, CR2 fájlokkal
# $3: input directory, JPG fájlokkal
# $4: thumb kimeneti direktori, teljes pathnévvel 

usage="Usage: $0 {directory for IXUS | -} {directory for CR2 | -} {directory for JPG | -} output_directory\n - stands for no operation\n use full path for all the directories"


for arg
do
  case $arg in
    --help | --hel | --he | --h)
      echo -e $usage 
      exit 1 ;;
  esac
done

case $# in
  4) ;;
  *) exec echo -e $usage
     exit 1 ;;
esac


function copy_dir_struct()
{
#  echo $1 $2
  pushd "$1"
  find . -type d -exec mkdir --parents "$2/{}" \;
  popd
}

# $4 - konverzió minõsége
# $3 - méret befoglaló négyzete
# $2 - konvertált fájl neve
# $1 - eredeti fájl neve

. /home/smb/SajatFejlesztes/common/scripts/multithread.sh

function set_quality_resize()
{
#  echo $1 $2 $3 $4
  if [ -f "$2" ] ; then
    echo $2 már létezik > /dev/null
  else

    exifautotran "$1"
    convert "$1" -scale $3x$3 -quality $4 "$2"
 fi
}

# $1 eredeti fájl
# $2 célfájl
function thumb_from_cr2()
{
  thumbfile=${1%.[Cc][Rr]2}.thumb.jpg
  thumbfile_out=${2%.[Cc][Rr]2}.THUMB.JPG
# echo THUMBFILE $thumbfile
  if [ -f $thumbfile_out ] ; then
    echo $thumbfile már létezik > /dev/null
  else
    dcraw -e $1
    set_quality_resize $thumbfile $thumbfile_out 1024 75 
    rm -f $thumbfile
#   mv $thumbfile.pisti $thumbfile
  fi
}

# altalanos jpg konverzió
# $1 IXUS input directory
# $2 output directory
# $3 aldirektori
# $4 számok maximális száma
function altalanos_jpg()
{
  copy_dir_struct "$1" "$2/$3"
  let kesz=0
  for i in `find $1 -name *.[Jj][Pp][Gg]`
  do
    wait_forlock 0.05
    l=$?
    case $l in
# Javíts meg!!! Ez itt 4 cpu - ra van optimalizálva.
    0 | 1 | 2 | 3)
      ( of=${i#$1} ; set_quality_resize "$i" "$2/$3/$of" 1024 75 ; let kesz++ ; rm mt_lock$l ) &
      let kesz++ ;;
#      echo $kesz/$4 ;;
    *) echo wait_forlock error l=$l
       exit ;;
    esac
  done
}

# CR2 konverzió
# $1 CR2 input directory
# $2 output directory
function CR2()
{
  let kesz=0
  copy_dir_struct $1 $2/CR2
  for i in `find $1 -name *.[Cc][Rr]2`
  do
    wait_forlock 0.05
    l=$?
    case $l in
    0 | 1 | 2 | 3)
      ( of=${i#$1} ; thumb_from_cr2 $i $2/CR2/$of ; rm mt_lock$l ) &
      let kesz++ ;;
#      echo $kesz/$NBR_CR2_EREDETI ;;
    *)
      echo wait_forlock error l=$l
      exit ;;
    esac
  done
}

case $4 in
  -) echo "Output directory must be specified"
     exit 1 ;;
esac

if [ ! -d $4 ] ; then
  mkdir --parents $4
fi

case $1 in
  -) echo "No IXUS directory specified" ;;
  *) NBR_IXUS_EREDETI=`find $1 -name *.[jJ][pP][gG] | wc -l`
     altalanos_jpg $1 $4 IXUS970IS $NBR_IXUS_EREDETI ;;
esac

case $2 in
  -) echo "No CR2 directory specified" ;;
  *) NBR_CR2_EREDETI=`find $2 -name *.[Cc][Rr]2 | wc -l`
     CR2 $2 $4 ;;
esac

case $3 in
  -) echo "No JPG directory specified" ;;
  *) NBR_JPG_EREDETI=`find $3 -name *.[jJ][pP][gG] | wc -l`
     altalanos_jpg $3 $4 JPG $NBR_JPG_EREDETI ;;
esac

# wait_for_last_lockot ki kell próbálni, hogy kell - e ide!!!!
