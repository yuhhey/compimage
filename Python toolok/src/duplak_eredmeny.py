# -*- coding: utf-8 -*-
import os
import pickle


def duplak_betolt(pickle_fajlnev):
    global d
    f=open(pickle_fajlnev, "r")
    d=pickle.loads(f.read())
    f.close()

def duplikalt(d, fajlnev):
    for i in d.keys():
        if len(d[i]) > 1:
            if (fajlnev in d[i]):
                return True

    return False

def duplikalt_feldolgozo_rekurzio(d, dirname, fnames):
    global nem_torolheto
    global torolheto_lista

    print "DFR:"+dirname
    if nem_torolheto:
        print 'visszatérés rekurzióból'
        return
#    print dirname,fnames
    for fname in fnames:
        teljesnev=os.path.join(dirname, fname)
        if os.path.isfile(teljesnev):
            if False == duplikalt(d, teljesnev):
                nem_torolheto=True
                return
        if os.path.isdir(teljesnev):
            fnames.remove(fname)
            print "Rekurzio:"+dirname, teljesnev
            os.path.walk(teljesnev, duplikalt_feldolgozo_rekurzio, d)
            if nem_torolheto:
                return
    torolheto_lista.append(dirname)

def duplikalt_feldolgozo(d, dirname, fnames):
    global nem_torolheto

    nem_torolheto=False
    print "Checking "+dirname
    duplikalt_feldolgozo_rekurzio(d, dirname, fnames)

#def duplikalt_dir(d, konyvtar):
    

torolheto_lista=[]

d=dict()

duplak_betolt("_storage")

duplak=0
i=0
ugras=1
for i in d.keys():
    d[i].sort()
    if (len(d[i]) > 1) and (1 == ugras):
        duplak+=1
        print len(d[i])
        for f in range(len(d[i])):
            print '[%d] "%s"'% (f,d[i][f])
        c=raw_input('Művelet - (n)ext, +(s)záz, (v)ége:')
        if 's' == c:
            ugras=100
        elif 'v' == c:
            break
        else:
            ugras=1
    ugras = max(1, ugras - 1)
       
           
       


print duplak
