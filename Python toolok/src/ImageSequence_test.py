#-*- coding: utf-8 -*-

import ImageSequence
import unittest
import os
import datetime
import shutil
import itertools

run_all = False

class testData:
    CR2_sourcepath_non_trailing_slash = '/storage/Kepek/HDR2'
    CR2_sourcepath = CR2_sourcepath_non_trailing_slash + '/'
    CR2_sourcepath_massive='/storage/Kepek/HDR1/'
    glob_sourcepath='/storage/Kepek/HDR1/IMG_00[23]?.CR2'
    CR2fl_1=('IMG_0536.CR2', 'IMG_0537.CR2', 'IMG_0537.CR2')
    NonImage=('A', 'B', 'C')
    outdir='/tmp/_test/'
    rawExt = 'CR2'
    
class errorMsg:
    NOFILE = 'No files found'
    NOIMGSEQ = 'No image sequence identified.'
    NONZEROLEN = 'Length of empty object is not 0'


class TimeStampCheckerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metadata=list()
        for fn in testData.CR2fl_1:
            cls.metadata.append(ImageSequence.readMetadata(os.path.join(testData.CR2_sourcepath, fn)))
        cls.tsc = ImageSequence.TimeStampChecker(maxdiff = 5)
        cls.ebc = ImageSequence.AEBChecker()
            
    def test_emptyTimeStampChecker(self):
        adict = dict()
        self.assertTrue(self.tsc(adict, self.metadata[0]), 'TimeStampChecker does not return True for an empty sequence')
    
    def test_emptyEBVChecker(self):
        adict = dict()
        self.assertTrue(self.ebc(adict, self.metadata[0]), 'AEBChecker does not return True for an empty sequence')
# The rest of the operation is tested by other classes
            

class ParserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.mkdir(testData.outdir)
        for fn in testData.CR2fl_1:
            shutil.copy(os.path.join(testData.CR2_sourcepath,fn), testData.outdir)
        for fn in testData.NonImage:
            open(os.path.join(testData.outdir, fn), 'w').close() # touch a'la python
        
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(testData.outdir)

    def test_creation(self):
        """ Make sure the constructor added the full path of all the image filenames
            and excluded all the non image files """
        imgsec_list = ImageSequence.findSequences(testData.CR2_sourcepath, testData.rawExt, 1)
        self.assertTrue(len(imgsec_list.file_l)>0, errorMsg.NOFILE)
        for f in testData.CR2fl_1:
            exp_res = os.path.join(testData.CR2_sourcepath, f)
            error_msg='%s was not found. %s, %s' % (f, exp_res, imgsec_list.file_l)
            self.assertIn(exp_res, imgsec_list.file_l, error_msg)

        for f in testData.NonImage:
            error_msg='%s was found' % f
            self.assertNotIn(os.path.join(testData.CR2_sourcepath, f), imgsec_list.file_l, error_msg)
    
    def test_len(self):
        """ Check whether the Parser.len()"""
        imgseq = ImageSequence.Parser()
        self.assertTrue(len(imgseq) == 0, errorMsg.NONZEROLEN)
        imgseq = ImageSequence.findSequences(testData.CR2_sourcepath, testData.rawExt, 1)
        self.assertTrue(len(imgseq) == 2, errorMsg.NOIMGSEQ)

    def test_filelist(self):
        hdr_list = ImageSequence.findSequences(testData.CR2_sourcepath, testData.rawExt, 1)
        self.assertTrue(len(hdr_list) > 0, errorMsg.NOIMGSEQ)
        fl=hdr_list[0].filelist()
        self.assertTrue(3, len(fl))
    
    def test_filelistWithGlob(self):
        img_seqs = ImageSequence.findSequences(testData.glob_sourcepath, testData.rawExt, 1)
        self.assertTrue(len(img_seqs) > 0, errorMsg.NOIMGSEQ)
        
    @unittest.skipIf(run_all == False, 'Massive')
    def test_analysis_massive(self):
        """ Check the analyzer with a huge set of real data """
        img_seq_list=ImageSequence.findSequences(testData.CR2_sourcepath_massive, testData.rawExt, maxdiff = 1)
        hibauzenet='Found %d HDR sequences' % len(img_seq_list)
        summa = 0
        for i in range(len(img_seq_list)):
            summa += len(img_seq_list[i])
            print i, len(img_seq_list[i]), sorted(img_seq_list[i].filelist())
        print "Sum = %d" % summa
            
        self.assertEqual(len(img_seq_list), 260, hibauzenet)
    
    @unittest.skipIf(run_all == False, 'To keep the test execution fast')
    def test_maxdiff_tune(self):
        maxdiff_list = [1, 5, 15]
        exp_result = [260, 259, 253]
        for md, r in itertools.izip(maxdiff_list, exp_result):
            img_seq_list = ImageSequence.findSequences(testData.CR2_sourcepath_massive, testData.rawExt, md)
            hibauzenet='Found %d HDR sequences in md=%d. run.' % (len(img_seq_list), md)
            self.assertEqual(len(img_seq_list), r, hibauzenet)
    
    def test_readPattern(self):
        img_seqs = ImageSequence.findSequences(testData.CR2_sourcepath_non_trailing_slash, testData.rawExt, 1)
        self.assertTrue(len(img_seqs) > 0, 'test_readPatter: no image sequence identified')
        
         
    def test_removeSequence(self):
        """ Sequences can be removed from Parser objects."""
        img_seqs = ImageSequence.findSequences(testData.glob_sourcepath, testData.rawExt, 1)
        initial_len = len(img_seqs)
        del img_seqs[0]
        next_len = len(img_seqs)
        self.assertTrue((initial_len - next_len) == 1,
                        "del img_seqs[0] does not work. initial len=%d, next len=%d" %(initial_len, next_len) )
        
        img_seqs.readPattern(testData.glob_sourcepath, testData.rawExt)
        img_seqs.searchSeq(maxdiff=1) # To rebuild the complete list
        self.assertTrue(initial_len==len(img_seqs), "Rebuilding of sequence information failed")
        del img_seqs[-1]
        self.assertTrue((initial_len-1)==len(img_seqs), "Error with removing the last sequence")
        
        img_seqs = ImageSequence.findSequences(testData.glob_sourcepath, testData.rawExt, 1)
        del img_seqs[1:-1]
        self.assertTrue(2==len(img_seqs), "Error with removing range")
        
        img_seqs.readPattern(testData.glob_sourcepath, testData.rawExt)
        img_seqs.searchSeq(maxdiff=1)
        self.assertTrue(initial_len==len(img_seqs), "Rebuilding of sequence after slice delete failed")
        
    def test_searchSeq(self):
        img_seqs = ImageSequence.Parser()
        img_seqs.readPattern(testData.glob_sourcepath, 'CR2')
        img_seqs.searchSeq(maxdiff=1)
        nseqs = len(img_seqs)
        self.assertTrue(nseqs>0, "Could not find sequences")
        img_seqs.searchSeq(maxdiff=1)
        nseqs_2nd = len(img_seqs)
        self.assertTrue(nseqs==nseqs_2nd,
                        "2nd searchSeq error: nseqs=%d, nseqs_2nd=%d" %(nseqs, nseqs_2nd))
        

class ImageSequenceTest(unittest.TestCase):

    def __search_sequence(self, hdr_seq, path, filelist):
        for f in filelist:
            full_path=os.path.join(path, f)
            if hdr_seq.check(full_path):
                hdr_seq.add(full_path)

    def __prepare_seq_search(self):
        tsc = ImageSequence.TimeStampChecker(maxdiff = 5)
        self.hdr_seq.checkers.append(tsc)
        self.path = testData.CR2_sourcepath_massive
        self.filelist = ['IMG_0020.CR2',
                         'IMG_0021.CR2',
                         'IMG_0022.CR2',
                         'IMG_0031.CR2',
                         'IMG_0032.CR2',
                         'IMG_0033.CR2']
        
    def setUp(self):
        self.hdr_seq=ImageSequence.Sequence()
        self.hdrfn_1=os.path.join(testData.CR2_sourcepath, testData.CR2fl_1[0])
        self.hdrfn_2=os.path.join(testData.CR2_sourcepath, testData.CR2fl_1[1])
        self.non_hdrfn='/storage/Kepek/kepek_eredeti/CR2/2010_01_08/IMG_4620.CR2'
        
    def test_checkWithTimeStampChecker(self):
        self.assertFalse(self.hdr_seq.check(self.hdrfn_1), 'Empty checkerlist case wrong')

        tsc = ImageSequence.TimeStampChecker(maxdiff = 5)
        self.hdr_seq.checkers.append(tsc)
        self.assertTrue(self.hdr_seq.check(self.hdrfn_1),
                        'Something wrong with checkers')
        self.assertTrue(self.hdr_seq.check(self.hdrfn_2),
                        'Failed to identify the 2nd image of the sequence')
        # Checking file against an empty Parser is always successful, so we add one file
        self.hdr_seq.add(self.hdrfn_1) 
        self.assertFalse(self.hdr_seq.check(self.non_hdrfn),
                         'Failed to ignore an image which is not in the sequence')
        
    def test_checkWithAEBChecker(self):
        ebvc = ImageSequence.AEBChecker()
        self.hdr_seq.checkers.append(ebvc)
        self.hdr_seq.check(self.hdrfn_1)
        # It is important to call all the checkers even if the image sequence is empty, because the checkers can object
        # which might collect data from the images. Just like exposure bracket value checker doesn.
        self.assertTrue(len(ebvc.ebvs) == 1, 'ImageSequence.checker does not call all the checker if it is empty')

    def test_add(self):
        self.hdr_seq.add(self.hdrfn_1)
        self.assertTrue(1==len(self.hdr_seq), 'Adding the initial image failed')

        self.hdr_seq.add(self.hdrfn_2)
        self.assertTrue(2==len(self.hdr_seq), 'Adding more image failed')

    def test_delete(self):
        self.__prepare_seq_search()
        self.__search_sequence(self.hdr_seq, self.path, self.filelist)
        
        orig_len = len(self.hdr_seq)
        fl = self.hdr_seq.filelist()
        del self.hdr_seq[fl[0]]
        self.assertTrue((orig_len-len(self.hdr_seq)) == 1, 'ImageSequence delete failed')

    def test_timeStampSequenceIdentification(self):
        self.__prepare_seq_search()
        self.runtest(self.hdr_seq, self.path, self.filelist)

    def runtest(self, hdrseq, path, filelist):
        self.__search_sequence(hdrseq, path, filelist)
        self.assertEqual(len(hdrseq), 3, 'Sequential - Could not identify an existingHDR sequence')
        
        filelist[2] , filelist[3] = filelist[3] , filelist[2]
        hdrseq.seq_data.clear()
        self.__search_sequence(hdrseq, path, filelist)
        self.assertEqual(len(hdrseq), 3, 'Non sequential - Could not identify an existingHDR sequence')

    def test_keys(self):
        self.__prepare_seq_search()
        self.__search_sequence(self.hdr_seq, self.path, self.filelist)
        n = len(self.hdr_seq)
        self.assertEqual(n, 3, 'error with keys: len(keys)=%d' % n)
        
    @unittest.skip('Future development')
    def test_AEBBracketValueSequenceIdentification(self, param=0):
        AEBC = ImageSequence.AEBChecker()
        self.hdr_seq.checkers.append(AEBC)
        path = testData.CR2_sourcepath_massive
        filelist = ['IMG_6219.CR2',
                    'IMG_6220.CR2',
                    'IMG_6221.CR2',
                    'IMG_6228.CR2',
                    'IMG_6229.CR2',
                    'IMG_6230.CR2']
        
        self.runtest(self.hdr_seq, path, filelist)
        
class HelperFunctionsTest(unittest.TestCase):
    def test_readMetadata(self):
        self.assertTrue(2==2, 'Üres teszt')

    def test_datumFrom400DMetadata(self):
        # 400D CR2
        cr2_file = testData.CR2_sourcepath + testData.CR2fl_1[0]
        datum=ImageSequence.timestampFromMetadata(ImageSequence.readMetadata(cr2_file))
        exp_datum = (datetime.datetime(2010, 11, 6, 13, 45, 21, 998750), datetime.datetime(2010, 11, 6, 13, 45, 22))
        self.assertEqual(datum, exp_datum, 'Reading data from %s, res=%s, exp_datum=%s' % (cr2_file, datum, exp_datum))
        
    def test_findSequences(self):
        imgseq = ImageSequence.findSequences(testData.CR2_sourcepath, testData.rawExt, 1)
        self.assertTrue(len(imgseq) > 0, 'ImageSequence.findSequence failed to find existing image sequences')
    
    def test_findSequencesNoSequence(self):
        try:
            ImageSequence.findSequences(testData.CR2_sourcepath, '.pisti')
        except TypeError:
            return
        self.assertTrue(1 == 2, 'ImageSequence.findSequence found sequence that does not exist')
        
    def _checkScriptExists(self, dir, prefix):
        path = os.path.join(dir, prefix+'.sh')
        return os.path.exists(path)
    
    @unittest.skipIf(run_all == False, 'Massive')
    def test_sequenceWorkflow(self):
        indir = "/storage/Kepek/kepek_eredeti/CR2/2012_10_16"
        outdir = "/storage/Panorama/tmp/"
        ImageSequence.SequenceWorkflow(indir, outdir, 1)
        
        fnl = ImageSequence.FileNameLogic(indir, outdir)
        
        self.assertTrue(self._checkScriptExists(outdir, "2012_10_16_symlink"), 'Symlink script')
#        os.remove(os.path.join(outdir, fnl.symlinkScript()))
        self.assertTrue(self._checkScriptExists(outdir, '2012_10_16_sets'), 'Set separation script')
#        os.remove(os.path.join(outdir, fnl.setSeparationScript()))
        self.assertTrue(self._checkScriptExists(outdir, '2012_10_16_HDRGen'), 'HDR generation script')
#        os.remove(os.path.join(outdir, fnl.HDRGenScript()))
                
class ShellScriptWriterTest(unittest.TestCase):
    def setUp(self):
        self.shellScriptWriter = ImageSequence.ShellScriptWriter()

    def test_startCondition(self):
        cond = "! -f pisti"
        self.shellScriptWriter.startCondition(cond)
        expected_result = "if [ " + cond + " ] ; then\n"

        self.assertTrue(expected_result == self.shellScriptWriter,
                        self.shellScriptWriter)

    def test_endCondition(self):
        self.shellScriptWriter.endCondition()
        expected_result = "fi\n"
        self.assertTrue(expected_result == self.shellScriptWriter,
                        self.shellScriptWriter)

        
    def test_addCommand(self):
        command = "Pisti"
        self.shellScriptWriter.addCommand(command)
        expected_result = command + '\n'

        self.assertEqual(expected_result, self.shellScriptWriter,
                         self.shellScriptWriter)


class SequenceScriptWriterTest(unittest.TestCase):
    fileSequences = [('a'),
                     ('b', 'c'),
                     ('d', 'e', 'g'),
                     ('h', 'i', 'j', 'k')]
    dir = '/tmp'
    prefix = 'ScriptWriterUT'
           
    @classmethod
    def setUpClass(cls):
        cls.imgseqParser = ImageSequence.findSequences(testData.CR2_sourcepath, testData.rawExt, 1)
        assert len(cls.imgseqParser) > 0, 'No image sequences found.'
    
    def setUp(self):
        self.script = ImageSequence.SequenceScriptWriter(self.dir, self.prefix)
    
    def tearDown(self):
        try: # More than one test_ function creates script, but not all.
            os.remove(self.expScriptName())
        except OSError:
            print '%s does not exist.' % self.expScriptName()
            pass
                
    def test_genIndexedFn(self):
        fn = self.script.genIndexedFn(self.script.fullprefix, 11, 'tif')
        exp_fn = '/tmp/ScriptWriterUT_0011.tif'
        msg = 'fn, expected_fn = \n%sIttAVege\n%sIttAVege' % (fn, exp_fn)
        self.assertEqual(fn, exp_fn, msg)
    
    def expScriptName(self):
        return os.path.join(self.dir, self.prefix) + '.sh'

    def _basicScriptCheck(self):
        self.assertTrue(os.path.exists(self.dir))
        expected_script = self.expScriptName()
        self.assertTrue(os.path.exists(expected_script), expected_script)
        statinfo = os.stat(expected_script)
        self.assertTrue(statinfo.st_size > 0, 'Empty file')

    def test_createHDRGeneScript(self):
        imgseqParser = ImageSequence.findSequences(testData.CR2_sourcepath, testData.rawExt, 1)
        self.script.createHDRGenScript(imgseqParser)
        self.script.save()
        self._basicScriptCheck()
        self.assertTrue(False, "Az HDR scriptben a CR2 Pathtol veszi a fájlneveket, de TIF kiterjesztéssel")
        

    def test_dumpLinkSeqNoOwnDir(self):
        self.script.dumpLinkSeq(self.imgseqParser[0], 0, owndir = False)
        self.script.save()
        self._basicScriptCheck()
        
    def test_dumpLinkSeqOwnDir(self):
        self.script.dumpLinkSeq(self.imgseqParser[0], 0, owndir = True)
        self.script.save()
        self._basicScriptCheck()        
    
    def test_createLinkScript(self):
        self.script.createLinkScript(self.imgseqParser, owndir = False)
        self.script.save()
        self._basicScriptCheck()

def suite(testHDRList=False,
          testImageSequence=False,
          testHelperFunctions=False,
          testShellScriptWriter=False,
          testScriptWriter=False):
    
    suite=unittest.TestSuite()

    if testHDRList:
        suite.addTest(ParserTest('test_len'))
        suite.addTest(ParserTest('test_creation'))
        # suite.addTest(ParserTest('test_analysis_massive'))
        suite.addTest(ParserTest('test_filelist'))
        suite.addTest(ParserTest('test_createHDRGeneScript'))

    if testImageSequence:
        suite.addTest(ImageSequenceTest('test_add'))
        suite.addTest(ImageSequenceTest('test_checkWithTimeStampCheck'))
        suite.addTest(ImageSequenceTest('test_list'))
        suite.addTest(ImageSequenceTest('test_timeStampSequenceIdentification'))
        suite.addTest(ImageSequenceTest('test_AEBBracketValueSequenceIdentification'))
        suite.addTest(ImageSequenceTest('test_keys'))
        
    if testHelperFunctions:
        suite.addTest(HelperFunctionsTest('test_readMetadata'))
        suite.addTest(HelperFunctionsTest('test_datumFromMetadata'))
        suite.addTest(HelperFunctionsTest('test_generateHDR'))
        suite.addTest(HelperFunctionsTest('test_AlignImageStackCommand'))
        suite.addTest(HelperFunctionsTest('test_enfuseCommand'))
        
    if testShellScriptWriter:
        suite.addTest(ShellScriptWriterTest('test_startCondition'))
        suite.addTest(ShellScriptWriterTest('test_endCondition'))
        suite.addTest(ShellScriptWriterTest('test_addCommand'))
    
    if testScriptWriter:
        suite.addTest(SequenceScriptWriterTest('test_createHDRGeneScript'))
        
    suite.addTest(TimeStampCheckerTest('test_emptyTimeStampChecker'))
    return suite

if __name__ == '__main__':
    runner =unittest.TextTestRunner(verbosity=0)
    test_suite = suite(testScriptWriter=True)
    runner.run(test_suite)
