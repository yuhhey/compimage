# -*- coding: utf-8 -*-

import CompositeImage as CI
import fractions
import datetime
import os.path
import unittest
import mock
import glob
import shutil

file_list = ["/home/smb/git/fotoworkflow/Python toolok/src/test_images/IMG_3025.CR2",
             "/home/smb/git/fotoworkflow/Python toolok/src/test_images/IMG_3026.CR2", 
             "/home/smb/git/fotoworkflow/Python toolok/src/test_images/IMG_3027.CR2", 
             "/home/smb/git/fotoworkflow/Python toolok/src/test_images/IMG_3031.CR2", 
             "/home/smb/git/fotoworkflow/Python toolok/src/test_images/IMG_1776.CR2",
             "/home/smb/git/fotoworkflow/Python toolok/src/test_images/IMG_3024.CR2",
             "/home/smb/git/fotoworkflow/Python toolok/src/test_images/IMG_1771.CR2",
             "/home/smb/git/fotoworkflow/Python toolok/src/test_images/IMG_3030.CR2",
             "/home/smb/git/fotoworkflow/Python toolok/src/test_images/IMG_3033.CR2",
             "/home/smb/git/fotoworkflow/Python toolok/src/test_images/IMG_1777.CR2",
             "/home/smb/git/fotoworkflow/Python toolok/src/test_images/IMG_1775.CR2",
             "/home/smb/git/fotoworkflow/Python toolok/src/test_images/IMG_1772.CR2",
             "/home/smb/git/fotoworkflow/Python toolok/src/test_images/IMG_3029.CR2",
             "/home/smb/git/fotoworkflow/Python toolok/src/test_images/IMG_3032.CR2",
             "/home/smb/git/fotoworkflow/Python toolok/src/test_images/IMG_1774.CR2",
             "/home/smb/git/fotoworkflow/Python toolok/src/test_images/IMG_1773.CR2",
             "/home/smb/git/fotoworkflow/Python toolok/src/test_images/IMG_3028.CR2"]


class SingleImageTest(unittest.TestCase):
    def setUp(self):
        self.SI =  CI.SingleImage(file_list[0])
        self.CUTname = self.__class__.__name__
    
    def test_name(self):
        exp_res = file_list[0]
        name = self.SI.name()
        
        self.assertEqual(exp_res, name, "%s.name() fullpath test" % self.CUTname)
        
        name = self.SI.name(basename=True)
        exp_res = os.path.basename(file_list[0])
        self.assertEqual(exp_res, name, "%s.name() basename test" % self.CUTname)
        
    def test_metadata(self):
        exposure_time = self.SI['Exif.Photo.ExposureTime']
        exp_res = fractions.Fraction(1,100)
        self.assertEqual(exp_res, exposure_time,)
        
        shot_date = self.SI['Exif.Photo.DateTimeOriginal']
        exp_res = datetime.datetime(2012,11,4,10,58,19)
        self.assertEqual(exp_res, shot_date, "exp_res=%s, shot_date=%s" %(exp_res, shot_date))
        
    def test_equality(self):
        si2 = CI.SingleImage(file_list[1])
        self.assertFalse(self.SI == si2, "SingleImage for different files")
        
        si3 = CI.SingleImage(file_list[0])
        self.assertTrue(self.SI == si3, "SingleImage for the same fiel")
        
        
class CompositeImageTest(unittest.TestCase):
    def setUp(self):
        self.ci = CI.CompositeImage() 
    
    def test_addAndlen(self):
        self.ci[1] = 1
        l = len(self.ci)
        self.assertEqual(1, l, 'Expected len=%d, actual len=%d' %(1, l))
        
        self.ci[1] = 2
        l = len(self.ci)
        self.assertEqual(1, l, 'Expected len=%d, actual len=%d' %(1, l))
        
        self.ci[2] = 3
        l = len(self.ci)
        self.assertEqual(2, l, 'Expected len=%d, actual len=%d' %(1, l))
        
        self.ci.add(CI.SingleImage(file_list[0]))
        l = len(self.ci)
        self.assertEqual(3, l, 'Expected len=%d, actual len=%d' %(1, l))
        
        self.ci.add(CI.SingleImage(file_list[0]))
        l = len(self.ci)
        self.assertEqual(3, l, 'adding the same image again. l=%d' % l)
        
    def test_iter(self):
        sis = {}
        for i in range(0,5):
            sis[file_list[i]] = CI.SingleImage(file_list[i])
            
        for img in self.ci:
            self.assertEquals(self.ci[img], sis[img], 'CompositeImage iterator: %s vs %s' % (img, sis[img].name()))
        

class CompositeImageCollectorTest(unittest.TestCase):
    def setUp(self):
        self.true_chkr =  mock.MagicMock(return_value=True)
        self.false_chkr = mock.MagicMock(return_value=False)
        
    def test_setNextCollector(self):
        self.cic = CI.CompositeImageCollector(self.true_chkr)
        self.cic.setNextCollector(1)
        self.assertTrue(1 == self.cic._next_collector, 'Failed to set successor')
        
    def test_defaultchecker(self):
        cic = CI.CompositeImageCollector([self.false_chkr])
        si0 = CI.SingleImage(file_list[0])
        check_result = cic.check(si0)
        self.assertTrue(check_result, 'default checker does not return True for 1st image')
        self.assertTrue(1 == len(cic.getCompImage()), 'default check function error at 1st image')
        
        si1 = CI.SingleImage(file_list[3])
        check_result = cic.check(si1)
        self.assertFalse(check_result, 'default checker does not return False for 2nd, nonmatching image')
        self.assertTrue(len(cic.getCompImage()) == 1, 'default checker added the 2nd image')
        
        cic.setCheckers([self.true_chkr])
        check_result = cic.check(si0)
        l = len(cic.getCompImage())
        self.assertTrue(check_result, 'Adding the same image again, return value')
        self.assertEqual(1, l, 'Adding the same image again, amount of images')
    
    def test_emptychecker(self):
        cic = CI.CompositeImageCollector([])
        si1 = CI.SingleImage(file_list[0])
        cic.check(si1) # No other way to add image to a checker
        si2 = CI.SingleImage(file_list[1])
        cic.check(si2)
        n_imgs = len(cic.getCompImage())
        self.assertEqual(2, n_imgs, 'Empty checker case')
     
        
class CollectHDRStrategyTest(unittest.TestCase):

    def setUp(self):
        self.collect_HDR_strategy = CI.CollectHDRStrategy()
        
    def test_timestamp(self):
        fl = sorted(file_list)
        for fn in fl:
            si = CI.SingleImage(fn)
            CI.timestampFromMetadata(si)


    def test_findHDR(self):
        hdrs, sic = self.collect_HDR_strategy.parseFileList(file_list)
        
        self.assertFalse(0 == len(hdrs),
                         'No HDR sequence found #sic=%d' % len(sic.getCompImage()))       
        self.assertEqual(4, len(hdrs),
                         'Not all HDRs were found. #hdrs found=%d, single images=%d' % (len(hdrs), len(sic.getCompImage())))        
       
        
        hdr_len_list = [ len(h.getCompImage()) for h in hdrs]
        self.assertEqual(16, sum(hdr_len_list), 'Not all images that belong to an hdr sequence are found')
        self.assertEqual(1, len(sic.getCompImage()), 'Number of single images=%d'%len(sic.getCompImage()))


    def test_64076506falsePositive(self):
        hdrs, sic = self.collect_HDR_strategy.parseFileList(glob.glob("/home/smb/tmp/IMG_640[6789].CR2"))
        
        self.assertEqual(0, len(hdrs), 'False positive')
        
    def test_findHDRinDirectory(self):
        fl = glob.glob('/home/smb/git/fotoworkflow/Python toolok/src/test_images/*.CR2')
        self.test_findHDR()
     
    
class GeneratorTest(unittest.TestCase):
    def setUp(self):
        self.short_fl = file_list[0:5]
        self.CI =CI.CompositeImage()
        self.CI.getFilelist = mock.MagicMock(name="getFileList")
        self.CI.getFilelist.return_value = self.short_fl
        
        

    def _runSymlinkGen(self, tdir):
        self.symlinkgen = CI.SymlinkGenerator()
        self.symlinkgen.setTargetDir(tdir)
        self.symlinkgen(self.CI)
        
    def test_SymlinkGenNoDirExists(self):
        tdir = '/tmp/a/b'
        self._runSymlinkGen(tdir)
    
        self.assertTrue(self.CI.getFilelist.called, 'symlink gen did not call CI.getFilelist')
        for f in self.short_fl:
            self.assertTrue(os.path.exists(os.path.basename(f)),
                            '%s does not exist, pwd=%s' % (f, os.getcwd()))
            
        #Itt nem kell, hogy exception-t dobjon a már létező symlinkek miatt
        self._runSymlinkGen(tdir)

        shutil.rmtree(tdir)

    def test_HDRGenerator(self):
        self.HDRgen = CI.HDRGenerator()
        self.HDRgen.setParams('/tmp', '.TIF', 'HDRTest')
        
        m = mock.MagicMock()
        with mock.patch('subprocess.call', m):
            self.HDRgen(self.CI)
            
        
 #       self.assertTrue(self.CI.getFilelist.called, 'HDRgen did not call CI getFilelist')
        tif_list = [os.path.splitext(os.path.basename(img))[0]+'.TIF' for img in self.short_fl]
        cmd1 = ['align_image_stack', '-a tmp', '-p HDRTest.pto'] + ['/tmp/TIF/%s'%t for t in tif_list]
        cmd2 = 'enfuse -o HDRTest.TIF' + ' tmp' + ' tmp'.join([str(i)+'.tif' for i in range(len(tif_list))])
        expected = [mock.call(cmd1), mock.call(cmd2)]
        
        for i in range(2):
            self.assertEqual(m.call_args_list[i], expected[i],
                         "call args list:\n%s\nexpected:\n%s" % (m.call_args_list[i], expected[i]))
        
@unittest.skip('Archaic remain.')        
class ParseTest(unittest.TestCase):
    
    def setUp(self):
         self.checker_head = CI.CompositeImageCollector()

