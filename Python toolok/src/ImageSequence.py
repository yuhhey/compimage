# -*- coding: utf-8 -*-

import datetime
import os
from math import floor
import pyexiv2
import glob
import Image
import StringIO
import itertools

def readMetadata(filename):
    """ Reads metadata from 'filename' and returns the metadata object ready to be used"""
    metadata = pyexiv2.ImageMetadata(filename)
    metadata.read()
    return metadata

def timestampFromMetadata(metadata):
    """ Returns the original date and time from the image represented by metadata
        as a 'datetime.datetime' object """
    tag_datum=metadata['Exif.Photo.DateTimeOriginal']
    datum = tag_datum.value    
    tag_exposure = metadata['Exif.Photo.ExposureTime']
    return (datum - datetime.timedelta(microseconds = floor(tag_exposure.value * 1000000)) , datum)


def readThumbNailFromCR2(filename):
    md = readMetadata(filename)
    tn = md.exif_thumbnail()
    im = Image.open(StringIO.StringIO(tn.data))
    return im

def SequenceWorkflow(indir, outdir, maxdiff):
    
        fnl = FileNameLogic(indir, outdir)
        CR2_dir = fnl.CR2_dir()
        CR2_seq_dir = fnl.CR2_dir()
        script_prefix = fnl.prefix()
        cr2_imgseq = findSequences(indir, 'CR2', maxdiff)
        symlink_script = SequenceScriptWriter(outdir, fnl.symlinkPrefix())
        symlink_script.createLinkScript(cr2_imgseq, owndir = False)
        symlink_script.save()
        # Itt kell megtörténnie a CR2->TIF converziónak.
        TIF_dir = fnl.TIF_dir()
        tif_imgseq = findSequences(TIF_dir, 'TIF', maxdiff) # '.TIF' is a default parameter
        separate_sets_script = SequenceScriptWriter(outdir, fnl.setSeparationPrefix())
        separate_sets_script.createLinkScript(tif_imgseq, owndir = True)
        separate_sets_script.save()
        
        gen_HDR_script = SequenceScriptWriter(outdir, fnl.HDRGenPrefix()) # '.TIF is a default parameter
        gen_HDR_script.createHDRGenScript(cr2_imgseq)
        gen_HDR_script.save()
        
class FileNameLogic:
    def __init__(self, in_dir, out_dir):
        self.in_dir = in_dir
        self.out_dir = out_dir
        
    def _dirCranch(self, postfix):
        d = self.out_dir + '/' + os.path.basename(self.in_dir) + postfix
        if not os.path.exists(d):
            os.mkdir(d)
        return d

    def CR2_dir(self):
        return self._dirCranch('_CR2')
    
    def TIF_dir(self):
        return self._dirCranch('_TIF')
    
    def prefix(self):
        return os.path.basename(self.in_dir)
    
    def symlinkPrefix(self):
        return self.prefix()+"_symlink"
    
    def symlinkScript(self):
        return self.symlinkPrefix() + '.sh'
    
    def setSeparationPrefix(self):
        return self.prefix()+"_sets"

    def setSeparationScript(self):
        return self.setSeparationPrefix() + '.sh'
    
    def HDRGenPrefix(self):
        return self.prefix()+"_HDRGen"
    
    def HDRGenScript(self):
        return self.HDRGenPrefix() + '.sh'

class TimeStampChecker:
    def __init__(self, maxdiff):
        self.maxdiff = maxdiff
    def __call__(self, adict, new_metadata):
        """ Checks if the images represented by their metadata in 'adict' where all taken within
            'maxtimediff=45sec'. Returns True if yes, false otherwise. """
        maxtimediff = datetime.timedelta(seconds=self.maxdiff)
        datum_pair = timestampFromMetadata(new_metadata)
        datumshot = datum_pair[0]
        for i in adict.keys():
            datum_from_seq = adict[i][Sequence.TIMESTAMP]
            datum_from_seq_saved = datum_from_seq[1]
            if (abs(datumshot - datum_from_seq_saved) < maxtimediff):
                return True
        return len(adict) == 0
    
class AEBChecker:
    def __init__(self):
        self.ebvs = list()
        pass
    
    def __call__(self, imgsec, new_metadata):
        
        ebv = new_metadata['Exif.Photo.ExposureBiasValue'].value
        if len(self.ebvs) != 0:
            #ebv = imgsec[key][Sequence.METADATA]['Exif.Photo.ExposureBiasValue'].value
            if ebv in self.ebvs:
                return False
        
        self.ebvs.append(ebv)
        return True


class Sequence:
    """ Identifies and stores a sequence of images for the same HDR image."""
    TIMESTAMP = 0
    METADATA = 1

    def __init__(self):
        self.seq_data=dict() # metadata read by pyexiv2. Filename is the index
        self.checkers=list() # functions to check f(seq_data_dict, metadata)

    
    def __len__(self):
        return len(self.seq_data)


    def __delitem__(self, key):
        del self.seq_data[key]


    def __getitem__(self, key):
        return self.seq_data[key]

    def add(self, filename):
        metadata = readMetadata(filename)
        timestamp = timestampFromMetadata(metadata)
        self.seq_data[filename] = (timestamp, metadata)
        return

    def check(self, filename):
        # Check if there is any checker first to avoid misterious first picture added, then nothing
        # works type of errors.

        if 0 == len(self.checkers):
            return False # Nothing is an HDR without checkers

        if (filename in self.seq_data):
            return True

        metadata = readMetadata(filename)  
        for checker in self.checkers:
            if not checker(self.seq_data, metadata):
                return False

        return True  

    def filelist(self):
        return self.seq_data.keys()

class Parser:
    tif_ext = ['TIF', 'TIFF', 'tif', 'tiff']
    jpg_ext = ['jpg', 'JPG', 'jpeg', 'JPEG']
    CR2_ext = ['CR2', 'cr2'] 
    def __init__(self):
        self.file_l=list()
        self.hdr_l=list()
            
    def readPattern(self, pattern, fileExt = 'TIF'):
        """ Volt egy pillanat, amikor a kiterjesztést feleslegesnek éreztem, de a teljes directory
            lista esetében még mindig hasznos. Főleg linuxon kisbetű/nagybetű megkülönböztetés miatt"""
        if os.path.isdir(pattern):
            pattern += '/*'
        
        if fileExt in self.tif_ext: ext_list = self.tif_ext
        elif fileExt in self.CR2_ext: ext_list = self.CR2_ext
        else: raise(TypeError)
        self.file_l = [os.path.normcase(f) for f in glob.glob(pattern)]               
        self.file_l = [f for f in self.file_l \
                       if os.path.splitext(f)[1][1:] in ext_list]                          
        self.file_l.sort()

    def __getitem__(self, key):
        return self.hdr_l[key]
                
    def __len__(self):
        return len(self.hdr_l)
    
    

    def __delFilesFromSeq(self, seq):
        """Before deleting the sequence itself, we have to delete the files that belong to the sequence from the 
           filelist of the parser"""
        for key_fn in seq.filelist():
            for i, fn in enumerate(self.file_l):
                if fn == key_fn:
                    del self.file_l[i]
                    break

    def __delitem__(self, item):
        if isinstance(item, slice):
             
            for i in xrange(*item.indices(len(self.hdr_l))):
                
                self.__delFilesFromSeq(self.hdr_l[i])
                del self.hdr_l[i]
                
        else:
            self.__delFilesFromSeq(self.hdr_l[item])
            del self.hdr_l[item]
            
        


    def searchSeq(self, maxdiff):
        def addCheckers(seq, tsc, ebvc):
            seq.checkers.append(tsc)
            seq.checkers.append(ebvc)
            
        
        if self.hdr_l > 0:
            self.hdr_l = []
        seq=Sequence()
        tsc = TimeStampChecker(maxdiff)
        ebvc = AEBChecker()
        addCheckers(seq, tsc, ebvc)
        for f in self.file_l:

            if seq.check(f):

                seq.add(f)
            else:
                
                if len(seq) > 1:
                
                    self.hdr_l.append(seq)
                    seq=Sequence()
                    del ebvc.ebvs[:] # Ez itt ronda, csak a gyors tesztelés végett került ide.
                    addCheckers(seq, tsc, ebvc)
                    
                else:
                    
                    seq.seq_data.clear()
                    
                seq.add(f)
                
        if len(seq) > 1:   # Ha éppen HDR sequence-re végződik a fájllista, akkor azt nem adja hozzá a ciklusban a hdr listához.
            self.hdr_l.append(seq)
        return
    
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

def createOutputFName(fname):
    return os.path.split(fname)[1]

def findSequences(pattern, filetype, maxdiff):
    """ Parses pattern for image sequences of filetype""" 
    imgseq = Parser()
    imgseq.readPattern(pattern, filetype)
    imgseq.searchSeq(maxdiff)
    return imgseq

      
#def hdrFilename(prefix, index):
#    fn = prefix + '.tif'
#    return fn
    


class SequenceScriptWriter(ShellScriptWriter):
    def __init__(self, output_dir, prefix):
        ShellScriptWriter.__init__(self)
        self.konyvtar = output_dir
        #self.ptoFnPref = os.path.join(output_dir, prefix)
        self.prefix = prefix
        self.fullprefix = os.path.join(output_dir, prefix)
        #self.outputFn = outputFn
        self.tmpprefix = 'tmp'
                
    def addAlignImageStackCommand(self, imgseq, index):
    
        command = 'align_image_stack -p %s' % self.genIndexedFn(self.fullprefix, index, 'pto') + ' -a ' + str(self.tmpprefix)
        for fn in imgseq.filelist():
#            bn = os.path.basename(fn)
            # I have no better idea to avoid double '/' in the pathname.
            command += ' ' + fn
        self.addCommand(command)

    def addEnfuseCommand(self, imgseq, index):
        command = 'enfuse -o %s' % self.genIndexedFn(self.fullprefix, index, 'tif') 
        for i in range(len(imgseq)):
            command += ' ' + ('%s%04d.tif' % (self.tmpprefix, i))
        self.addCommand(command)
    
    def dumpHDRSeq(self, seq, index):
        #output file neve kell
        
        condition = '-f %s' % self.genIndexedFn(self.fullprefix, index, 'tif')
        self.startCondition(condition) 
        self.addAlignImageStackCommand(seq, index)
        self.addEnfuseCommand(seq, index)
        self.endCondition()            

    def createHDRGenScript(self, img_seq_list):
        # Ezek mind mennek a SequenceScriptWriter osztályba
        #os.mkdir(outputDir)
        #script = outputDir + '/' + os.path.basename(outputDir) + '.sh'
        # self.script_file = open(script, 'w')

        for i,v  in enumerate(img_seq_list):
            self.dumpHDRSeq(v, i)
            
    def dumpLinkSeq(self, seq, index, owndir):
        
        self.addCommand('cd %s' % self.konyvtar)
        if owndir:
            indexed_dir = self.genIndexedDn(self.fullprefix, index)
            self.addCommand('mkdir %s' % indexed_dir)
            self.addCommand('cd %s' % indexed_dir)
        
        for fn in sorted(seq.filelist()):
            self.addCommand('ln -s %s' % fn)
        if owndir:
            self.addCommand('cd ..')
    
    def createLinkScript(self, img_seq_list, owndir):
        
        for i in range(len(img_seq_list)):
            self.dumpLinkSeq(img_seq_list[i], i, owndir)
            
    def save(self):
        ShellScriptWriter.saveScript(self, self.fullprefix + '.sh')
        
                