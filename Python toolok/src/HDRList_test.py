# -*- coding: utf-8 -*-

import HDRList
import unittest
import os
import datetime
import shutil

class HDRListErrorsTest(unittest.TestCase):
    def test_wrongPath(self):
        """ Test HDR identification """
        path='/Path/Does/Not/Exist'
        with self.assertRaises(TypeError) as e:
            HDRList(path)
        the_exception = e.exception
                

class HDRListTest(unittest.TestCase):
    CR2_sourcepath='/storage/Panorama/HDR1/'
    CR2fl_1=('IMG_0020.CR2', 'IMG_0021.CR2', 'IMG_0022.CR2')
    NonImage=('A', 'B', 'C')
    testdir='/tmp/_test/'
    def setUp(self):
        os.mkdir(self.testdir)

        for fn in self.CR2fl_1:
            shutil.copy(os.path.join(self.CR2_sourcepath,fn), self.testdir)

        for fn in self.NonImage:
            open(os.path.join(self.testdir, fn), 'w').close() # touch a'la python
        
    def tearDown(self):
        shutil.rmtree(self.testdir)

    def test_creation(self):
        """ Make sure the constructor added the full path of all the image filenames
            and excluded all the non image files """
        hdr_list=HDRList.HDRList(self.testdir)
        self.assertTrue(len(hdr_list.file_l)>0, 'No files found')
        for f in self.CR2fl_1:
            error_msg='%s was not found' % f
            self.assertIn(self.testdir+f, hdr_list.file_l, error_msg)

        for f in self.NonImage:
            error_msg='%s was found' % f
            self.assertNotIn(self.testdir+f, hdr_list.file_l, error_msg)

    def test_analysis(self):
        """ Check whether the analyzer found all the HDRs """
        hdr_list=HDRList.HDRList(self.testdir)
        hdr_list.searchHDRs()
        self.assertTrue(len(hdr_list)>0, 'No HDR sequences identified')

    def test_filelist(self):
        hdr_list = HDRList.HDRList(self.testdir)
        hdr_list.searchHDRs()
        fl=hdr_list[0].filelist()
        self.assertTrue(3, len(fl))

    def test_analysis_massive(self):
        """ Check the analyzer with a huge set of real data """
        hdr_list=HDRList.HDRList('/storage/Panorama/HDR1')
        hdr_list.searchHDRs()
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
    #            m = HDRList.readMetadata(i)
    #            datum = HDRList.datumFromMetadata(m)
    #            print i, datum
        self.assertEqual(len(hdr_list), 261, hibauzenet)

    def test_createScript(self):
        outputDir='/tmp/HDRList_createScriptTest'
        shutil.rmtree(outputDir)
        hdr_list = HDRList.HDRList(self.testdir)
        hdr_list.searchHDRs()
        hdr_list.createScript(outputDir)
        
        self.assertTrue(os.path.exists(outputDir))

        expected_script = outputDir+'/'+os.path.basename(outputDir)+'.sh'
        self.assertTrue(os.path.exists(expected_script), expected_script)

        statinfo = os.stat(expected_script)
        self.assertTrue(statinfo.st_size > 0, 'Empty file')
      
        

class HDRSequenceTest(unittest.TestCase):


    def setUp(self):
        self.hdr_seq=HDRList.HDRSequence()
        self.hdrfn_1='/storage/Panorama/HDR1/IMG_0020.CR2'
        self.hdrfn_2='/storage/Panorama/HDR1/IMG_0021.CR2'
        self.non_hdrfn='/storage/Kepek/kepek_eredeti/CR2/2010_01_08/IMG_4620.CR2'
        
    def test_check(self):
        self.assertFalse(self.hdr_seq.check(self.hdrfn_1), 'Empty checkerlist case wrong')

        self.hdr_seq.checkers.append(HDRList.timestampChecker)
        self.assertTrue(self.hdr_seq.check(self.hdrfn_1),
                        'Something wrong with checkers')
        self.assertTrue(self.hdr_seq.check(self.hdrfn_2),
                        'Failed to identify the 2nd image of the sequence')
        # Checking file against an empty HDRSequence is always successful, so we add one file
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
        self.hdr_seq.checkers.append(HDRList.timestampChecker)
        self.path='/storage/Panorama/HDR1'
        self.filelist=['IMG_0020.CR2',
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

        keys = self.hdr_seq.keys()
        self.assertEqual(len(keys), 3, 'error with keys: len(keys)=%d' % len(keys))
        
    def test_AEBBracketValueSequenceIdentification(self):
        self.hdr_seq.checkers.append(HDRList.AEBBracketValueChecker)
        path='/storage/Panorama/HDR1'
        filelist=['IMG_6219.CR2',
                  'IMG_6220.CR2',
                  'IMG_6221.CR2',
                  'IMG_6228.CR2',
                  'IMG_6229.CR2',
                  'IMG_6230.CR2']
        
        self.runtest(self.hdr_seq, path, filelist)
        
    def test_list(self):
        hdr_seq = HDRList.HDRSequence()
        self.assertTrue(1==0, 'This is where I shall continue')
        
class HelperFunctionsTest(unittest.TestCase):
    def test_readMetadata(self):
        self.assertTrue(2==2, 'Üres teszt')

    def test_datumFromMetadata(self):
        # 400D CR2
        datum=HDRList.datumFromMetadata(HDRList.readMetadata('/storage/Panorama/HDR1/IMG_0020.CR2'))
        self.assertEqual(datum, datetime.datetime(2010, 11, 6, 7, 50, 16), 'Reading data from /storage/Panorama/HDR1/IMG_0020.CR2')
        # 5DMkII CR2. It measures to the 100th sec accuracy
        metadata = HDRList.readMetadata('/storage/Panorama/Harbin/HDR/IMG_7445.CR2')
        datum = HDRList.datumFromMetadata(metadata)
        self.assertEqual(datum, datetime.datetime(2012, 1, 7, 16, 35, 36, 100000), '5DMkII datum read failed')
    def test_generateHDR(self):
        self.assertEqual(1,2, 'Itt kell folytatni')

    def test_AlignImageStackCommand(self):
        seq = ['IMG_0020.CR2', 'IMG_0021.CR2', 'IMG_0022.CR2']
        result = HDRList.AlignImageStackCommand(seq, 'Vegyes1_HDR0.tif.pto', 0)
        exp_res = "align_image_stack -p Vegyes1_HDR0.tif.pto -a 0 IMG_0020.CR2 IMG_0021.CR2 IMG_0022.CR2"
        self.assertEqual(result, exp_res, '\n' + result + exp_res)

    def test_enfuseCommand(self):

        result = HDRList.enfuseCommand('Vegyes1_HDR0.tif', 0, 3)
        exp_res ='enfuse -o Vegyes1_HDR0.tif 00000.tif 00001.tif 00002.tif'
        self.assertEqual(result, exp_res, '\n' + result + exp_res)
        
class ShellScriptWriterTest(unittest.TestCase):
    def setUp(self):
        self.shellScriptWriter = HDRList.ShellScriptWriter()

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

def suite(testHDRList=False,
          testHDRSequence=False,
          testHelperFunctions=False,
          testShellScriptWriter=False):
    suite=unittest.TestSuite()

    if testHDRList:
        suite.addTest(HDRListTest('test_analysis'))
        suite.addTest(HDRListTest('test_creation'))
        # suite.addTest(HDRListTest('test_analysis_massive'))
        suite.addTest(HDRListTest('test_filelist'))
        suite.addTest(HDRListErrorsTest('test_wrongPath'))
        suite.addTest(HDRListTest('test_createScript'))

    if testHDRSequence:
        suite.addTest(HDRSequenceTest('test_add'))
        suite.addTest(HDRSequenceTest('test_check'))
        suite.addTest(HDRSequenceTest('test_list'))
        suite.addTest(HDRSequenceTest('test_timeStampSequenceIdentification'))
        suite.addTest(HDRSequenceTest('test_AEBBracketValueSequenceIdentification'))
        suite.addTest(HDRSequenceTest('test_keys'))
        
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
        
    return suite

if __name__ == '__main__':
    runner =unittest.TextTestRunner(verbosity=2)
    test_suite = suite(testHDRList=False,
                       testHDRSequence=False,
                       testHelperFunctions=True,
                       testShellScriptWriter=False)
    runner.run(test_suite)
