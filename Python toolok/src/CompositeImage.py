# -*- coding: utf-8 -*-

import pyexiv2
import os.path
import datetime
from math import floor
import subprocess
import glob

 
class SingleImage(object):
    def __init__(self, fn):
        self._fn = fn
    
    def name(self, basename=False):
        if basename:
            return os.path.basename(self._fn)
        else:
            return self._fn
    

    def __getitem__(self, key):
        if not hasattr(self, '_metadata'):
            self._metadata = pyexiv2.ImageMetadata(self._fn)
            self._metadata.read()
        
        tag = self._metadata[key]
        return tag.value
    
    def __eq__(self, si):
        return (si._fn == self._fn)


class CompositeImage(object):
    def __init__(self):
        self._images = dict()

        
    def __setitem__(self, key, value):
        self._images[key] = value
        
    def __len__(self):
        return len(self._images)
    
    def __getitem__(self, key):
        return self._images[key]
    
    def __iter__(self):
        return iter(self._images.keys())
    
    def add(self, img):
        self[img.name()] = img # Amíg csak a fájlnév egyezés esetén tekintünk 2 képet egyformának, addig jó.
        
    def getFilelist(self, basename=False):
        if basename:
            return [os.path.basename(f) for f in self._images.keys()]
        else:
            return self._images.keys()
                

class CompositeImageCollector:
    def __init__(self,checker_list=None):
        self._checkers = checker_list
        self._images = CompositeImage()
        self.setNextCollector(None)
        
    def getCompImage(self):
        return self._images
        
    'TODO!!!: Erre itt nincs feltétlenül szükség. A parser használhat egy listát, aminek az elejéhez\
     adhatja a következő checkert. Ezzel az eredmény felhasználása és a darabszám meghatározása sokkal\
     egyszerűbbé válik. Azt kell elhatározni, hogy a chain of controlt bele akarom-e építeni az objektumba.\
     vagy meghagyom a felhasználó számára.'
    def setNextCollector(self, collector):
        self._next_collector = collector
        

    def collected(self):
        return len(self._images) > 1

    def check(self, img):
        if len(self._images) == 0:
            # We need to call all the checkers to handle stateful ones
            # such as AEBchecker. Otherwise we get false hits with 2 images.
            # CollectHDRStrategyTest.test_64076506falsePositive tests this case
            for chk in self._checkers:
                chk(self._images, img)
            self._images.add(img)
            return True
        
        for collect in self._checkers:
            if not collect(self._images, img):
                if (None != self._next_collector) and (not self.collected()):
                    key = self._images.getFilelist()
                    return self._next_collector.check(self._images[key[0]])
                else:
                    return False
        
        self._images.add(img)
        return True
        
    def setCheckers(self,chkrs):
        self._checkers = chkrs
        
    
class SingleImageCollector(CompositeImageCollector):    
    def check(self, img):
        self._images.add(img)
        return False
    
    def collected(self):
        return False


class TimeStampChecker:
    def __init__(self, maxdiff):
        self.maxdiff = maxdiff
    def __call__(self, comp_img, simg):
        """ Checks if the images represented by their metadata in 'adict' where all taken within
            'maxtimediff=45sec'. Returns True if yes, false otherwise. """
        maxtimediff = datetime.timedelta(seconds=self.maxdiff)
        datum_pair = timestampFromMetadata(simg)
        datumshot = datum_pair[0]
        for k in comp_img:
            datum_from_seq_pair = timestampFromMetadata(comp_img[k])
            datum_from_seq = datum_from_seq_pair[0]
            datum_from_seq_saved = datum_from_seq_pair[1]
            if (abs(datumshot - datum_from_seq_saved) < maxtimediff):
                return True
        return False


class AEBChecker:
    def __init__(self):
        self.ebvs = list()
    
    def __call__(self, comp_img, s_img):
        
        ebv = s_img['Exif.Photo.ExposureBiasValue']
        if len(self.ebvs) != 0:
            #ebv = comp_img[key][Sequence.METADATA]['Exif.Photo.ExposureBiasValue'].value
            if ebv in self.ebvs:
                return False
        
        self.ebvs.append(ebv)
        return True
    

class CollectHDRStrategy:
    def readFiles(self, fl):
        imgs = []
        for fn in fl:
            imgs.append(SingleImage(fn))
        
        imgs.sort(key=lambda si:(timestampFromMetadata(si))[0])
        return imgs

    def parseFileList(self, fl):
        imgs = self.readFiles(fl)
        
        cic = CompositeImageCollector([TimeStampChecker(maxdiff=7), AEBChecker()])
        sic = SingleImageCollector()
        cic.setNextCollector(sic)
        hdrs = []
        for si in imgs:
            if not cic.check(si):
                if cic.collected():
                    hdrs.insert(0, cic)
                cic = CompositeImageCollector([TimeStampChecker(maxdiff=7), AEBChecker()])
                cic.check(si)
                cic.setNextCollector(sic)
        
        if cic.collected():
            hdrs.insert(0, cic)
        return hdrs, sic
 
      
def timestampFromMetadata(simg):
    """ Returns (exposure started, exposure ended) of the image described by simg"""
    
    datum=simg['Exif.Photo.DateTimeOriginal']    
    exposure = simg['Exif.Photo.ExposureTime']
    dt = (datum, datum + datetime.timedelta(microseconds = floor(exposure * 1000000)))
    return dt


class SymlinkGenerator():
    def __init__(self):
        self.targetDir=""
        
    def setTargetDir(self,d):
        self.targetDir = os.path.realpath(d)
        self.rawDir = os.path.join(self.targetDir, 'CR2')
        
    def __call__(self, cimg):
        if self.targetDir == "":
            d = os.path.curdir
            self.setTargetDir(d)
        
        if not os.path.exists(self.rawDir):
            os.makedirs(self.rawDir)
            
        os.chdir(self.rawDir)
        for f in cimg.getFilelist():
            bn = os.path.basename(f)
            if not os.path.exists(bn):
                os.symlink(f, bn)
        

class HDRGenerator():
    def __init__(self):
        pass
    
    
    def setParams(self, targetdir, ext, prefix):
        self._target_dir = targetdir
        self._ext = ext
        self._prefix = prefix
        
        
    def __call__(self, cimg):
        
        fl = cimg.getFilelist()
        img_subdir = self._ext[1:]
        tif_list = [os.path.join(self._target_dir, img_subdir, os.path.splitext(os.path.basename(f))[0]+self._ext) for f in fl]
        align_cmd = ['align_image_stack', '-atmp', '-p%s.pto' % os.path.join(self._target_dir, self._prefix)] + tif_list
        print align_cmd
        subprocess.call(align_cmd)
        
        enfuse_cmd = ['enfuse', '-o%s' % os.path.join(self._target_dir, self._prefix+self._ext)] + ['tmp%04d.tif'%i for i in range(len(fl))]
        print enfuse_cmd
        subprocess.call(enfuse_cmd)
        
        for fn in glob.glob('tmp[0-9][0-9][0-9][0-9]*'):
            os.remove(fn)
        
class ShellScriptWriter:
    """Represents script logic. Returns script elements as strings"""
    def __init__(self):
        self.buf = ''
        self.indent = ''

    def __str__(self):
        return self.buf

    def __eq__(self, other):
        return self.buf == other

    def addCommand(self, command):
        self.buf += self.indent + command + "\n"
        

    def endCondition(self):
        self.buf += "fi\n"
        self.indent = self.indent[:-4]
    
    def genIndexedFn(self, prefix, index, ext):
        return '%s_%04d.%s' %(prefix, index, ext)
    
    def genIndexedDn(self, prefix, index):
        return '%s_%04d' % (prefix, index)
    
    def startCondition(self, cond):
        self.buf += "if [ " + cond + " ] ; then\n"
        self.indent += '    '
        
    def saveScript(self, filename):
        fout = open(filename, 'w')
        fout.write(str(self))
        fout.close()