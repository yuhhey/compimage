# -*- coding: utf-8 -*-

import datetime
import os
from math import floor
import pyexiv2

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

def timestampChecker(adict, new_metadata, maxdiff = 30):
    """ Checks if the images represented by their metadata in 'adict' where all taken within
        'maxtimediff=45sec'. Returns True if yes, false otherwise. """
    maxtimediff = datetime.timedelta(seconds=maxdiff)
    datum_pair = timestampFromMetadata(new_metadata)
    datumshot = datum_pair[0]
    for i in adict.keys():
        datum = adict[i][Sequence.TIMESTAMP]
        datumsaved = datum[1]
        if (abs(datumshot - datumsaved) < maxtimediff):
            return True
    return False

def AEBBracketValueChecker(adict, new_metadata):
    AEBBV_l=list()
    for key in adict.keys():
        AEBBV_l.append(float(adict[key][Sequence.METADATA]['Exif.Photo.ExposureBiasValue'].value))
    AEBBV_new=float(new_metadata['Exif.Photo.ExposureBiasValue'].value)
    if AEBBV_new in AEBBV_l:
        return False # egy sorozatban 2x ugyanaz a exposure bias nem lehet.
    #if and 
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

        if 0 == len(self.seq_data):
            return True # Any image is part of an empty HDR sequence
        
        
        if (filename in self.seq_data):
            return True

        metadata = readMetadata(filename)  
        for func in self.checkers:
            if not func(self.seq_data, metadata):
                return False

        return True  

    def filelist(self):
        return self.seq_data.keys()

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

class Parser:
    tif_ext = ['.TIF', '.TIFF', '.tif', '.tiff']
    CR2_ext = ['.CR2', '.cr2'] 
    def __init__(self):
        self.file_l=list()
        self.hdr_l=list()
            
    def readDir(self, path, filetype = '.TIF'):
        if not os.path.isdir(path):
            raise(TypeError)
        
        if filetype in self.tif_ext:
            ext_list = self.tif_ext
        elif filetype in self.CR2_ext:
            ext_list = self.CR2_ext
        else:
            raise(TypeError)
        
        for fn in os.listdir(path):
            full_path=os.path.join(path, fn)
            if os.path.splitext(full_path)[1] in ext_list:
                self.file_l.append(full_path)
        
        self.file_l = sorted(self.file_l, key = lambda x: x[1])
                
    def __getitem__(self, key):
        return self.hdr_l[key]
                
    def __len__(self):
        return len(self.hdr_l)

    def searchHDRs(self):
        seq=Sequence()
        seq.checkers.append(timestampChecker)

        for f in self.file_l:
            # print len(seq), f
            if seq.check(f):
                seq.add(f)
            else:
                if len(seq) > 1:
                    self.hdr_l.append(seq)
                    seq=Sequence()
                    seq.checkers.append(timestampChecker)
                    
                else:
                    seq.seq_data.clear()
                seq.add(f)
                
        if len(seq) > 1:   # Ha éppen HDR sequence-re végződik a fájllista, akkor azt nem adja hozzá a ciklusban a hdr listához.
            self.hdr_l.append(seq)
        return

def createOutputFName(fname):
    return os.path.split(fname)[1]

def findSequences(inputDir, filetype = '.TIF'):
    """ Parses inputDir for image sequences of filetype""" 
    assert os.path.isdir(inputDir), "inputDir=%s not a directory" % inputDir
    imgseq = Parser()
    imgseq.readDir(inputDir, filetype)
    imgseq.searchHDRs()
    return imgseq

def moveScriptCommands(HDRs, scriptWriter, konyvtar, useSubfolders = True):
       
    if useSubfolders:
        scriptWriter.addCommand('mkdir ' + konyvtar)
        scriptWriter.addCommand('cd ' + konyvtar)
    for f in HDRs.filelist():
        scriptWriter.addCommand('ln -s ' + f) #+ ' ' + outputDir + '/' + createOutputFName(f))
    
    if useSubfolders:
        scriptWriter.addCommand('cd ..')
      
def hdrFilename(prefix, index):
    fn = prefix + '.tif'
    return fn
    


class ScriptWriter(ShellScriptWriter):
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
        # Ezek mind mennek a ScriptWriter osztályba
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
        
        for fn in seq.filelist():
            self.addCommand('ln -s %s' % fn)
        if owndir:
            self.addCommand('cd ..')
    
    def createLinkScript(self, img_seq_list, owndir):
        
        for i in range(len(img_seq_list)):
            self.dumpLinkSeq(img_seq_list[i], i, owndir)
            
    def save(self):
        ShellScriptWriter.saveScript(self, self.fullprefix + '.sh')