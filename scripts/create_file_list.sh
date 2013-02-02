#!/bin/bash

# $1: direktori
# --unit-_test: execute SH unit cases.

# ToDo:

NOTEXISTS_ERROR="does not exist."
NOTAFILE_ERROR="is not a regular file."

function generate_archivum_fajllista()
{
  find /media/ARCHIVUM_[12]/{CR2,IXUS970IS,JPG,HG10} -type f | sed 's/.*ARCHIVUM_[12]\///' | sort > fajllista_archivumban
}

# $1: fájlnév, amiből a listát kreálni kell
function extractData()
{
  fajlnev=`basename $1`
  case $fajlnev in
    JPG_[34567]*)
      sed_parancs=s/.*$fajlnev\\/// ;;
    JPG_8,*)
      sed_parancs=s/.*$fajlnev\\/// ;;
    KIMARADTAK_*)
      sed_parancs=s/.*$fajlnev\\/// ;;
    VEGYES_*)
      sed_parancs=s/.*$fajlnev\\/// ;;
    IXUS970IS_1 | IXUS970IS_2 | IXUS970IS_3*)
      sed_parancs=s/.*$fajlnev\\/// ;;
    JPG_*)
      sed_parancs=s/.*$fajlnev/JPG/;;
    CR2_*)
      sed_parancs=s/.*$fajlnev/CR2/;;
    IXUS970IS_*)
      sed_parancs=s/.*$fajlnev/IXUS970IS/;;
    HG10_46a)
      sed_parancs=s/.*HG10_46/HG10/;;
    HG10_*)
      sed_parancs=s/.*$fajlnev/HG10/;;
    *)
      return;
  esac
  sed $sed_parancs $1
}  

for arg
do
  case $arg in
    --unit-test)
     return;;
    *)
     if [ ! -e $arg  ] ; then
       echo $0: $arg $NOTEXISTS_ERROR
       exit 1
     fi
     if [ ! -f $arg  ] ; then
       echo $0: $arg $NOTAFILE_ERROR
       exit 1
     fi
     extractData $arg ;;
  esac
done

