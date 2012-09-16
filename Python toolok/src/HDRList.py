# -*- coding: utf-8 -*-

import shutil
import datetime
import os
import math
import pyexiv2

def readMetadata(filename):
    """ Reads metadata from 'filename' and returns the metadata object ready to be used"""
    metadata = pyexiv2.ImageMetadata(filename)
    metadata.read()
    return metadata

def datumFromMetadata(metadata):
    """ Returns the original date and time from the image represented by metadata
        as a 'datetime.datetime' object """
    tag_datum=metadata['Exif.Photo.DateTimeOriginal']
    datum = tag_datum.value
    if 'Canon EOS 5D Mark II' == metadata['Exif.Image.Model'].value:
        tag_szazadmp=metadata['Exif.Photo.SubSecTimeOriginal']
        szazadmp=int(tag_szazadmp.value)*10000
        datum=datum+datetime.timedelta(microseconds=szazadmp)
    return datum

def timestampChecker(adict, new_metadata):
    """ Checks if the images represented by their metadata in 'adict' where all taken within
        'maxtimediff=1sec'. Returns True if yes, false otherwise. """
    maxtimediff = datetime.timedelta(seconds=1)
    new_datum = datumFromMetadata(new_metadata)
    for i in adict.keys():
        datum = datumFromMetadata(adict[i])
        if (abs(new_datum - datum) > maxtimediff):
            return False
    return True

def AEBBracketValueChecker(adict, new_metadata):
    AEBBV_l=list()
    for key in adict.keys():
        AEBBV_l.append(float(adict[key]['Exif.Photo.ExposureBiasValue'].value))
    print AEBBV_l
    AEBBV_new=float(new_metadata['Exif.Photo.ExposureBiasValue'].value)
    if AEBBV_new in AEBBV_l:
        return False # egy sorozatban 2x ugyanaz a exposure bias nem lehet.
    #if and 
    return True

class HDRSequence:
    """ Identifies and stores a sequence of images for the same HDR image."""
    def __init__(self):
        self.seq_data=dict() # metadata read by pyexiv2. Filename is the index
        self.checkers=list() # functions to check f(seq_data_dict, metadata)

    def __len__(self):
        return len(self.seq_data)

    def __getitem__(self, key):
        return self.seq_data[key]

    def add(self, filename):
        metadata=readMetadata(filename)
        self.seq_data[filename] = metadata
        return

    def check(self, filename):
        # Check if there is any checker first to avoid misterious first picture added, then nothing
        # works type of errors.

        if 0 == len(self.checkers):
            return False # Nothing is an HDR without checkers

        if 0 == len(self.seq_data):
            return True # Any image is part of an empty HDR sequence

        if (filename not in self.seq_data):
            metadata=readMetadata(filename)
        else:
            return True

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

    def startCondition(self, cond):
        self.buf += "if [ " + cond + " ] ; then\n"
        self.indent += '    '

class HDRList:

    def __init__(self, path):
        if not os.path.isdir(path):
            raise(TypeError)
        self.file_l=list()
        self.hdr_l=list()
        for fn in os.listdir(path):
            full_path=os.path.join(path, fn)
            if '.CR2' == os.path.splitext(full_path)[1]:
                self.file_l.append(full_path)
    def __getitem__(self, key):
        return self.hdr_l[key]
                
    def __len__(self):
        return len(self.hdr_l)

    #def dumpHDR(self, i):
        # output file neve kell
        #self.scriptWriter.condition(seq, i) 
        #self.scriptWriter.write_align_image_stack_command(seq, i)
        #self.scriptWriter.write_enfuse_command(seq, i)
        #self.scriptWriter.write_end_condition(seq, i)
            

    def createScript(self, outputDir):
        self.scriptWriter=ShellScriptWriter(outputDir)
        # Ezek mind mennek a ScriptWriter osztályba
        #os.mkdir(outputDir)
        #script = outputDir + '/' + os.path.basename(outputDir) + '.sh'
        # self.script_file = open(script, 'w')

        for i in range(len(self)):
            self.dumpHDR(i)
            
        #script_file.close()
        
        
        
            
    def searchHDRs(self):
        seq=HDRSequence()
        seq.checkers.append(timestampChecker)

        for f in self.file_l:
            # print len(seq), f
            if seq.check(f):
                seq.add(f)
            else:
                if len(seq) > 1:
                    self.hdr_l.append(seq)
                    seq=HDRSequence()
                    seq.checkers.append(timestampChecker)
                    
                else:
                    seq.seq_data.clear()
                seq.add(f)
        if len(seq) > 1:   # Ha éppen HDR sequence-re végződik a fájllista, akkor azt nem adja hozzá a ciklusban a hdr listához.
            self.hdr_l.append(seq)
        return

def AlignImageStackCommand(seq, ptoFn, prefix):
    
    command = 'align_image_stack -p ' + ptoFn + ' -a ' + str(prefix)
    for i in range(len(seq)):
        # Itt ez nem jó, mivel a TIFeket másik direktoriba teszem mint a CR2-ket
        command += ' ' + os.path.splitext(seq[i])[0] + '.TIF'
    return command

def enfuseCommand(outputFn, prefix, numFiles):
    command = 'enfuse -o ' + outputFn
    for i in range(numFiles):
        command += ' ' + ('%s%04d.tif' % (str(prefix), i))
    return command

def createOutputFName(fname):
    return os.path.split(fname)[1]

def generateMoveScript(inputDir, outputDir, prefix):

    hl = HDRList(inputDir)
    hl.searchHDRs()
    scw = ShellScriptWriter()
    
    if 0 == len(hl) : # no point creating the script of an empty list
        return
        
    for i in range(len(hl)):
        for f in hl[i].filelist():
            scw.addCommand('ln -s ' + f + ' ' + outputDir + '/' + createOutputFName(f))

    fout = open(outputDir + '/' + prefix + '.sh', 'w')
    fout.write(str(scw))
    fout.close()
    
def generateHDRScript(inputDir, outputDir, hdr_prefix):

    
    hl = HDRList(inputDir)
    hl.searchHDRs()
    scw = ShellScriptWriter()

    for i in range(len(hl)):
        hdrFn = outputDir + hdrFilename(hdr_prefix, i)
        ptoFn = hdrFn + '.pto'
        scw.startCondition('! -f ' + hdrFn)
        scw.addCommand(AlignImageStackCommand(hl[i].filelist(), ptoFn, i))
        scw.addCommand(enfuseCommand(hdrFn, i, len(hl[i])))
        scw.endCondition()

    fout = open(outputDir + '/' + hdr_prefix + '.sh', 'w')
    fout.write(str(scw))
    fout.close()

def hdrFilename(prefix, index):
    fn = prefix
    fn += str(index) + '.tif'
    return fn
    
def pathWalkWrapper(params, dirname, fnames):
    '''Can be passed to os.path.walk to produce whole directory tree.
    It processes on the directory in dirname'''
    
    print params, dirname
    generateMoveScript(dirname, params[0], params[1] + os.path.basename(dirname))
