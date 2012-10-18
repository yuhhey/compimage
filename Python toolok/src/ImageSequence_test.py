#-*- coding: utf-8 -*-

import ImageSequence
import unittest
import os
import datetime
import shutil

class testData:
    CR2_sourcepath = '/storage/Kepek/HDR2/'
    CR2_sourcepath_massive='/storage/Kepek/HDR1/'
    CR2fl_1=('IMG_0536.CR2', 'IMG_0537.CR2', 'IMG_0537.CR2')
    NonImage=('A', 'B', 'C')
    outdir='/tmp/_test/'
    rawExt = '.CR2'
    
class errorMsg:
    NOFILE = 'No files found'
    NOIMGSEQ = 'No image sequence identified.'
    NONZEROLEN = 'Length of empty object is not 0'

class HDRListErrorsTest(unittest.TestCase):
    def test_wrongPath(self):
        """ Test HDR identification """
        path='/Path/Does/Not/Exist'
        with self.assertRaises(TypeError) as e:
            ImgSeq = ImageSequence.Parser()
            ImgSeq.readDir(path)
        the_exception = e.exception
                
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
        imgsec_list = ImageSequence.findSequences(testData.CR2_sourcepath, testData.rawExt)
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
        imgseq = ImageSequence.findSequences(testData.CR2_sourcepath, testData.rawExt)
        self.assertTrue(len(imgseq) == 2, errorMsg.NOIMGSEQ)

    def test_filelist(self):
        hdr_list = ImageSequence.findSequences(testData.CR2_sourcepath, testData.rawExt)
        self.assertTrue(len(hdr_list) > 0, errorMsg.NOIMGSEQ)
        fl=hdr_list[0].filelist()
        self.assertTrue(3, len(fl))
    
    @unittest.skip('Make UT in eclipse very fast')
    def test_analysis_massive(self):
        """ Check the analyzer with a huge set of real data """
        hdr_list=ImageSequence.findSequences(testData.CR2_sourcepath_massive, testData.rawExt)
        hibauzenet='Found %d HDR sequences' % len(hdr_list)
    #        for hdr_seq in hdr_list.hdr_l:
    #            for hdr in hdr_seq.seq_data:
    #                print "    ",\
    #                      hdr,\
    #                      hdr_seq[hdr]['Exif.Photo.DateTimeOriginal'].value
    #            print
    # Kiírja a HDR sequencehez nem adott fájlokat.
    #        f_l=list(hdr_list.file_l)
    #        for image in hdr_list.file_l:
    #            for hdr_seq in hdr_list.hdr_l:
    #                if image in hdr_seq.seq_data:
    #                    try:
    #                        f_l.remove(image)
    #                    except:
    #                        pass
    #        print
    #        for i in f_l:
    #            m = Parser.readMetadata(i)
    #            datum = Parser.timestampFromMetadata(m)
    #            print i, datum
        self.assertEqual(len(hdr_list), 147, hibauzenet)

class ImageSequenceTest(unittest.TestCase):


    def setUp(self):
        self.hdr_seq=ImageSequence.Sequence()
        self.hdrfn_1=os.path.join(testData.CR2_sourcepath, testData.CR2fl_1[0])
        self.hdrfn_2=os.path.join(testData.CR2_sourcepath, testData.CR2fl_1[1])
        self.non_hdrfn='/storage/Kepek/kepek_eredeti/CR2/2010_01_08/IMG_4620.CR2'
        
    def test_check(self):
        self.assertFalse(self.hdr_seq.check(self.hdrfn_1), 'Empty checkerlist case wrong')

        self.hdr_seq.checkers.append(ImageSequence.timestampChecker)
        self.assertTrue(self.hdr_seq.check(self.hdrfn_1),
                        'Something wrong with checkers')
        self.assertTrue(self.hdr_seq.check(self.hdrfn_2),
                        'Failed to identify the 2nd image of the sequence')
        # Checking file against an empty Parser is always successful, so we add one file
        self.hdr_seq.add(self.hdrfn_1) 
        self.assertFalse(self.hdr_seq.check(self.non_hdrfn),
                         'Failed to ignore an image which is not in the sequence')

    def test_add(self):
        self.hdr_seq.add(self.hdrfn_1)
        self.assertTrue(1==len(self.hdr_seq), 'Adding the initial image failed')

        self.hdr_seq.add(self.hdrfn_2)
        self.assertTrue(2==len(self.hdr_seq), 'Adding more image failed')

    def _search_sequence(self, hdr_seq, path, filelist):
        for f in filelist:
            full_path=os.path.join(path, f)
            if hdr_seq.check(full_path):
                hdr_seq.add(full_path)

    def _populate_sequence(self):
        self.hdr_seq.checkers.append(ImageSequence.timestampChecker)
        self.path = testData.CR2_sourcepath_massive
        self.filelist = ['IMG_0020.CR2',
                         'IMG_0021.CR2',
                         'IMG_0022.CR2',
                         'IMG_0031.CR2',
                         'IMG_0032.CR2',
                         'IMG_0033.CR2']
        
    def test_timeStampSequenceIdentification(self):
        self._populate_sequence()
        self.runtest(self.hdr_seq, self.path, self.filelist)

    def runtest(self, hdrseq, path, filelist):
        self._search_sequence(hdrseq, path, filelist)
        print len(hdrseq)
        self.assertEqual(len(hdrseq), 3, 'Sequential - Could not identify an existingHDR sequence')

        filelist[2] , filelist[3] = filelist[3] , filelist[2]
        hdrseq.seq_data.clear()
        self._search_sequence(hdrseq, path, filelist)
        print len(hdrseq)
        self.assertEqual(len(hdrseq), 3, 'Non sequential - Could not identify an existingHDR sequence')

    def test_keys(self):
        self._populate_sequence()
        self._search_sequence(self.hdr_seq, self.path, self.filelist)
        n = len(self.hdr_seq)
        self.assertEqual(n, 3, 'error with keys: len(keys)=%d' % n)
        
    def test_AEBBracketValueSequenceIdentification(self):
        self.hdr_seq.checkers.append(ImageSequence.AEBBracketValueChecker)
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
        imgseq = ImageSequence.findSequences(testData.CR2_sourcepath, '.CR2')
        self.assertTrue(len(imgseq) > 0, 'ImageSequence.findSequence failed to find existing image sequences')
    
    def test_findSequencesNoSequence(self):
        try:
            ImageSequence.findSequences(testData.CR2_sourcepath, '.pisti')
        except TypeError:
            return
        self.assertTrue(1 == 2, 'ImageSequence.findSequence found sequence that does not exist')
        
    def test_sequenceWorkflow(self):
        CR2_dir = "/storage/Kepek/kepek_eredeti/CR2/2012_10_16"
        CR2_seq_dir = "/storage/Panorama/Chengdu/2012_10_16_CR2"
        cr2_imgseq = ImageSequence.findSequences(CR2_dir, '.CR2')
        symlink_script = ImageSequence.ScriptWriter(CR2_seq_dir, '2012_10_16_symlink')
        symlink_script.createLinkScript(cr2_imgseq, owndir = False)
        symlink_script.save()
        # Itt kell megtörténnie a CR2->TIF converziónak.
        TIF_dir = "/storage/Panorama/Chengdu/2012_10_16_TIF"
        tif_imgseq = ImageSequence.findSequences(TIF_dir) # '.TIF' is a default parameter
        separate_sets_script = ImageSequence.ScriptWriter(TIF_dir, '2012_10_16_separate_sets')
        separate_sets_script.createSeparateSetScript(tif_imgseq)
        separate_sets_script.save()
        
        HDR_dir = "/storage/Panorama/Chengdu"
        gen_HDR_script = ImageSequence.ScriptWriter(HDR_dir) # '.TIF is a default parameter
        gen_HDR_script.createHDRGenScript(HDR_dir)
        gen_HDR_script.save()
                
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


class ScriptWriterTest(unittest.TestCase):
    fileSequences = [('a'),
                     ('b', 'c'),
                     ('d', 'e', 'g'),
                     ('h', 'i', 'j', 'k')]
    dir = '/tmp'
    prefix = 'ScriptWriterUT'
           
    @classmethod
    def setUpClass(cls):
        cls.imgseqParser = ImageSequence.findSequences(testData.CR2_sourcepath, testData.rawExt)
        assert len(cls.imgseqParser) > 0, 'No image sequences found.'
    
    def setUp(self):
        self.script = ImageSequence.ScriptWriter(self.dir, self.prefix)
    
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
        imgseqParser = ImageSequence.findSequences(testData.CR2_sourcepath, testData.rawExt)
        self.script.createHDRGenScript(imgseqParser)
        self.script.save()
        self._basicScriptCheck()
        

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

#def suite(testHDRList=False,
#          testImageSequence=False,
#          testHelperFunctions=False,
#          testShellScriptWriter=False,
#          testScriptWriter=False):
#    
#    suite=unittest.TestSuite()
#
#    if testHDRList:
#        suite.addTest(ParserTest('test_len'))
#        suite.addTest(ParserTest('test_creation'))
#        # suite.addTest(ParserTest('test_analysis_massive'))
#        suite.addTest(ParserTest('test_filelist'))
#        suite.addTest(HDRListErrorsTest('test_wrongPath'))
#        suite.addTest(ParserTest('test_createHDRGeneScript'))
#
#    if testImageSequence:
#        suite.addTest(ImageSequenceTest('test_add'))
#        suite.addTest(ImageSequenceTest('test_check'))
#        suite.addTest(ImageSequenceTest('test_list'))
#        suite.addTest(ImageSequenceTest('test_timeStampSequenceIdentification'))
#        suite.addTest(ImageSequenceTest('test_AEBBracketValueSequenceIdentification'))
#        suite.addTest(ImageSequenceTest('test_keys'))
#        
#    if testHelperFunctions:
#        suite.addTest(HelperFunctionsTest('test_readMetadata'))
#        suite.addTest(HelperFunctionsTest('test_datumFromMetadata'))
#        suite.addTest(HelperFunctionsTest('test_generateHDR'))
#        suite.addTest(HelperFunctionsTest('test_AlignImageStackCommand'))
#        suite.addTest(HelperFunctionsTest('test_enfuseCommand'))
#        
#    if testShellScriptWriter:
#        suite.addTest(ShellScriptWriterTest('test_startCondition'))
#        suite.addTest(ShellScriptWriterTest('test_endCondition'))
#        suite.addTest(ShellScriptWriterTest('test_addCommand'))
#    
#    if testScriptWriter:
#        suite.addTest(ScriptWriterTest('test_genOutputFn'))
#        suite.addTest(ScriptWriterTest('test_createHDRGeneScript'))
#        
#    return suite
#
#if __name__ == '__main__':
#    runner =unittest.TextTestRunner(verbosity=0)
#    test_suite = suite(testScriptWriter=True)
#    runner.run(test_suite)
