# -*- coding: utf-8 -*-
import os
import pickle

def feldolgozo(eredmeny, dirname, fnames):
    for fname in fnames:
        teljesnev=os.path.join(dirname, fname)
        if os.path.isfile(teljesnev):
            print 'Fájl: ', teljesnev
            cmd="md5sum " + '"'+teljesnev+'"'
            try:
                fp=os.popen(cmd)
                checksum,output = fp.read().split("  ")
                if checksum not in eredmeny:
                    eredmeny[checksum]=list()
                eredmeny[checksum].append(teljesnev)
                    
            except Exception as e:
                print "Hibazott:", teljesnev
                print type(e)
                print e.args
                print e
        else:
            print 'Direktori: ', teljesnev

def store_result(dir_to_check, data):
    l_atm=dir_to_check.split('/')
    delimiter='_'
    permanens_file=delimiter.join(l_atm)
    fout=open(permanens_file, 'w')
    fout.write(pickle.dumps(data))
    fout.close()

def print_result(d):
    for i in d :
        if len(d[i]) > 1:
            d[i].sort()
            for f in range(1,len(d[i])):
                print 'rm "%s"'%d[i][f]

def search_same(dir_to_check):
    d=dict()
    os.path.walk(dir_to_check, feldolgozo, d)
    store_result(dir_to_check, d)
    print_result(d)

search_same('/storage/MM/Konyvek')
