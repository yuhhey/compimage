# -*- coding: utf-8 -*-

import os
import pyexiv2
import datetime
import math

def readDateTime(d, fajlnev):
    """Reads the exif creation data from fajlnev and adds it to the dictionary
    d. The index is the filename"""
    if fajlnev not in d:
        try:
            metadata=pyexiv2.ImageMetadata(fajlnev)
            metadata.read()
            tag_datum=metadata['Exif.Photo.DateTimeOriginal']
            datum=tag_datum.value
            if 'Canon EOS 5D Mark II' == metadata['Exif.Image.Model'].value:
                tag_szazadmp=metadata['Exif.Photo.SubSecTimeOriginal']
                szazadmp=int(tag_szazadmp.value)*10000
                datum=datum+datetime.timedelta(microseconds=szazadmp)

            d[fajlnev] = datum
        except Exception as e:
            print fajlnev, ' hibázott', type(e), e.args


l=os.listdir('/storage/Kepek/kepek_eredeti/CR2/2012_02_02_Mandalay')
os.chdir('/storage/Kepek/kepek_eredeti/CR2/2012_02_02_Mandalay')

def parsefiles(adict, alist):
    for fajlnev in alist:
        readDateTime(adict,fajlnev)

def listHDR(adict):
    hdr_treshold=datetime.timedelta(seconds=1)

    items=adict.items()
    items.sort()
    for i in range(2,len(items)):
        delta=items[i][1]-items[i-2][1]
        if delta <= hdr_treshold:
           print 'HDR gyanus:', items[i-2][0], items[i][0]
               

def feldolgozo(e, dirname, fnames):
    filelist=list()
    for fname in fnames:
        teljesnev=os.path.join(dirname, fname)
        if os.path.isfile(teljesnev) and ('.CR2' == os.path.splitext(teljesnev)[1]):
            filelist.append(teljesnev)

    if len(filelist) > 2:
        d=dict()
        parsefiles(d, filelist)
        listHDR(d)

def dump_hdr_gen_sh(adirname, pref):
    """Creates in adirname an HDR generator script named $(pref)_hdr_gen.sh,
    that creates HDR images of file triplets in adirname"""
    
    teljes_path=os.path.abspath(adirname)
    eredmeny_prefix=os.path.split(teljes_path)[1]
    script_nev=pref+'_hdr_gen.sh'

    l=list()
    

# ki kell válogatni az IMG_kezdetűeket
    for i in os.listdir(teljes_path):
        if ('IMG_' == i[0:4]):
            l.append(i)

    # Rendezni kell, mert az os.listdir az inode-ok sorrendjének megfelelő
    # sorrendben adja vissza fájlneveket. Ha mindig csak 3-asával adjuk a fájlokat
    # a HDR könyvtárhoz, akkor nincs gond. Erre azonban nem lehet számítani.
    # Még így is feltesszük, hogy a HDR sorozatok egymást kihagyás nélkül követő
    # sorozatok.
    l.sort()
    
    script=open(teljes_path+'/'+script_nev,'w')

    n_kep=len(l)/3
    # format_str='%sHDR%%0%dd.tif' % (pref, math.ceil(math.log(n_kep)))
    hdr_index_format_string = '%%0%dd' % math.ceil(math.log10(n_kep))
    for i in range(0, len(l)/3):
        
        # enfuse output
        hdr_output=('%sHDR'+hdr_index_format_string+'.tif') % (pref, i)
        aop = hdr_index_format_string % i
        condition_begin='if [ ! -f %s ] ; then\n' % hdr_output
        
        eki=3 * i # elso kep indexe
        pto_file=hdr_output + '.pto'
        align_image_stack_cmd='    align_image_stack -p %s -a %s %s %s %s\n'\
                               % (pto_file, aop, l[eki], l[eki+1], l[eki+2])
        
        enfip=aop+'000'
        enfuse_cmd='    enfuse -o %s %s %s %s\n'\
                    % (hdr_output, enfip+'0.tif', enfip+'1.tif', enfip+'2.tif')
        condition_end='fi\n'
        
        script.write(condition_begin)
        script.write(align_image_stack_cmd)
        script.write(enfuse_cmd)
        script.write(condition_end)
        
    script.close()
