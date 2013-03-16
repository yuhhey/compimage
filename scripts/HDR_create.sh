#!/bin/bash

# $1: az eredményfájl teljes neve kiterjesztéssel

let do_align=0
let do_enfuse=0

while [ "$1" ]
do
    case $1 in
	--align | -a)
	    let do_align=1 ;;
	--enfuse | -e)
	    let do_enfuse=1
# TODO:
	    enfuse_output="$2"
	    shift ;;
	--tca_correct | -t)
	    let do_tca_correct=1
    esac
    shift
done

echo $do_align $do_enfuse $enfuse_output $do_tca_correct

if [ $do_enfuse -eq 1 ] ; then
    if [ $do_align -eq 0 ] ; then
	echo enfuse align_image_stack nélkül. Remélem tudod mit csinálsz:-D!
    fi
fi


# Leginkabb a sigma lencshez kell
if [ $do_tca_correct -eq 1 ] ; then
    for i in *.tiff
    do
	fulla `tca_correct -o abcv $i | grep -e -r` $i
    done
fi

# Kézből készített HDR képeknél ez szükséges
if [ $do_align -eq 1 ] ; then
    align_image_stack -a AIS_ img_????_corr.tiff
fi

# HDR képpé fésüljük a bemenetet.
if [ $do_enfuse -eq 1 ] ; then
    enfuse -o "$enfuse_output" AIS_????.tif
fi
