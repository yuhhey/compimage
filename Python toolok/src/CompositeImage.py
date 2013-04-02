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
        
    def keys(self):
        return self.getFileList()
                

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
    """ Checks if consequetive images are shot within 'maxdiff' sec.
        5DMarkII records the time of shot when it was started. The shot is ended +exposure_time
        second later. This checker test the time difference between finishing image N and
        starting image N+1. exposure_time becomes important for night shots."""
    """TODO: it checks for all the images within the composite image comp_img. The time difference can be big 
          in case of composite images with many images, e.g. panoramas. Especially taken during night.
          The HDRStrategy objects orders the images by their 'date time original' exif field, so there is room
          for perfomance improvement"""
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

    def parseFileList(self, fl, hdr_config=None):
        
        if hdr_config == None:
            hdr_config = HDRConfig(os.getcwd())
            
        imgs = self.readFiles(fl)
        
        cic = CompositeImageCollector(hdr_config.GetCheckers())
        sic = SingleImageCollector()
        cic.setNextCollector(sic)
        hdrs = []
        for si in imgs:
            print si.name()
            if not cic.check(si):
                if cic.collected():
                    hdrs.insert(0, cic.getCompImage())
                cic = CompositeImageCollector(hdr_config.GetCheckers())
                cic.check(si)
                cic.setNextCollector(sic)
        
        if cic.collected():
            hdrs.insert(0, cic.getCompImage())
        return hdrs, sic
    
    def parseDir(self, d, hdr_config=None):
        if hdr_config == None:
            hdr_config = HDRConfig(os.getcwd())
        
        path_with_wildcard = os.path.join(d, "*%s" % hdr_config.GetRawExt())
        fl = [fn for fn in glob.glob(path_with_wildcard)]
        return self.parseFileList(fl, hdr_config)
 
      
def timestampFromMetadata(simg):
    """ Returns (exposure started, exposure ended) of the image described by simg"""
    
    datum=simg['Exif.Photo.DateTimeOriginal']    
    exposure = simg['Exif.Photo.ExposureTime']
    dt = (datum, datum + datetime.timedelta(microseconds = floor(exposure * 1000000)))
    return dt


class SymlinkGenerator:
    def __init__(self):
        self.targetDir=""
        
    def __call__(self, cimg, hdr_config):
        target_dir = hdr_config.GetTargetDir()
        raw_ext = hdr_config.GetRawExt()
        raw_dir = os.path.join(target_dir, raw_ext[1:])
        
        
        if not os.path.exists(raw_dir):
            os.makedirs(raw_dir)
            
        os.chdir(raw_dir)
        for f in cimg.getFilelist():
            bn = os.path.basename(f)
            if not os.path.exists(bn):
                os.symlink(f, bn)


class HDRConfig():
    """Contains all the configuration data used in HDR sequence handling and final image generation"""
    def __init__(self,targetdir, raw_ext='.CR2', hdr_ext='.TIF', prefix='HDR', checkers=[TimeStampChecker(7), AEBChecker()]):
        self.SetTargetDir(targetdir)
        self.SetRawExt(raw_ext)
        self.SetImageExt(hdr_ext)
        self.SetPrefix(prefix)
        self.SetCheckers(checkers)
        
    def SetTargetDir(self, d):
        if d == "":
            self._target_dir = os.path.curdir
        else:
            self._target_dir = d
            
    def GetTargetDir(self):
        return self._target_dir
    
    def SetRawExt(self,raw_ext):
        self._raw_ext = raw_ext
        
    def GetRawExt(self):
        return self._raw_ext
      
    def SetImageExt(self, ext):
        self._output_ext = ext
        
    def GetImageExt(self):
        return self._output_ext
      
    def SetPrefix(self,prefix):
        self._prefix = prefix
        
    def GetPrefix(self):
        return self._prefix
    
    def SetCheckers(self, chkrs):
        self._checkers = chkrs
        
    def GetCheckers(self):
        return self._checkers

    def GetImageSubdir(self):
        return self.GetImageExt()[1:]

    def __str__(self):
        return "HDRConfig:\n" + \
               "targetDir:%s\n" % self.GetTargetDir() + \
               "rawExt:%s\n" % self.GetRawExt() + \
               "imgExt:%s\n" % self.GetImageExt() + \
               "prefix:%s\n" % self.GetPrefix()


class HDRGenerator():
    def __init__(self):
        pass    
        
    def __call__(self, cimg, hdr_config):
        
        def RawnameToImagename(f):
            image_subdir = hdr_config.GetImageSubdir()
            img_name = os.path.join(hdr_config.GetTargetDir(),
                                    image_subdir,
                                    os.path.splitext(os.path.basename(f))[0]+hdr_config.GetImageExt())
            return img_name
        
        fl = cimg.getFilelist()
        
        tif_list = [RawnameToImagename(f) for f in fl]
        pto_file = os.path.join(hdr_config.GetTargetDir(), hdr_config.GetPrefix())
        align_cmd = ['align_image_stack', '-atmp', '-p%s.pto' % pto_file] + tif_list
        subprocess.call(align_cmd)
        
        output_file = os.path.join(hdr_config.GetTargetDir(), hdr_config.GetPrefix()+hdr_config.GetImageExt())
        enfuse_cmd = ['enfuse', '-o%s' % output_file] + ['tmp%04d.tif'%i for i in range(len(fl))]
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
