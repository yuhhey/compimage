# -*- coding: utf-8 -*-


import CompositeImage
import fractions
import datetime
import os.path
import unittest
import mock
import glob
import collections


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


tag_list = ["Exif.Photo.DateTimeOriginal",
            "Exif.Photo.ExposureTime",
            "Exif.Photo.ExposureBiasValue"]

def makehash():
    return collections.defaultdict(makehash)


si_mock_data = makehash()

# using this function assume that Composite.SingleImage object handles attributes properly.
# It is a simple proxy in this context, hence it is not a strong assumption.
def PistisetUpModule():
    for fn in file_list:
        si = CompositeImage.SingleImage(fn)
        for t in tag_list:
            si_mock_data[fn][t] = si[t]
    
    
class SingleImageTest(unittest.TestCase):
    def setUp(self):
 
        self.SI = CompositeImage.SingleImage(file_list[0])
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
        si2 = CompositeImage.SingleImage(file_list[1])
        self.assertFalse(self.SI == si2, "SingleImage for different files")
        
        si3 = CompositeImage.SingleImage(file_list[0])
        self.assertTrue(self.SI == si3, "SingleImage for the same file")


class SingleImage_mock(CompositeImage.SingleImage):
    def __getitem__(self, arg):
        global si_mock_data
        print self._fn, arg, si_mock_data[self._fn][arg]
        return si_mock_data[self._fn][arg]
    
    
class CompositeImageTest(unittest.TestCase):
    def setUp(self):
        self.ci = CompositeImage.CompositeImage()
        CompositeImage.SingleImage = SingleImage_mock
    
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
        
        self.ci.add(CompositeImage.SingleImage(file_list[0]))
        l = len(self.ci)
        self.assertEqual(3, l, 'Expected len=%d, actual len=%d' %(1, l))
        
        self.ci.add(CompositeImage.SingleImage(file_list[0]))
        l = len(self.ci)
        self.assertEqual(3, l, 'adding the same image again. l=%d' % l)
        
    def test_iter(self):
        sis = {}
        for i in range(0,5):
            sis[file_list[i]] = CompositeImage.SingleImage(file_list[i])
            
        for img in self.ci:
            self.assertEquals(self.ci[img], sis[img], 'CompositeImage iterator: %s vs %s' % (img, sis[img].name()))
        

class CompositeImageCollectorTest(unittest.TestCase):
    def setUp(self):
        self.true_chkr =  mock.MagicMock(return_value=True)
        self.false_chkr = mock.MagicMock(return_value=False)
        
    def test_setNextCollector(self):
        self.cic = CompositeImage.CompositeImageCollector(self.true_chkr)
        self.cic.setNextCollector(1)
        self.assertTrue(1 == self.cic._next_collector, 'Failed to set successor')
        
    def test_defaultchecker(self):
        cic = CompositeImage.CompositeImageCollector([self.false_chkr])
        si0 = CompositeImage.SingleImage(file_list[0])
        check_result = cic.check(si0)
        self.assertTrue(check_result, 'default checker does not return True for 1st image')
        self.assertTrue(1 == len(cic.getCompImage()), 'default check function error at 1st image')
        
        si1 = CompositeImage.SingleImage(file_list[3])
        check_result = cic.check(si1)
        self.assertFalse(check_result, 'default checker does not return False for 2nd, nonmatching image')
        self.assertTrue(len(cic.getCompImage()) == 1, 'default checker added the 2nd image')
        
        cic.setCheckers([self.true_chkr])
        check_result = cic.check(si0)
        l = len(cic.getCompImage())
        self.assertTrue(check_result, 'Adding the same image again, return value')
        self.assertEqual(1, l, 'Adding the same image again, amount of images')
    
    def test_emptychecker(self):
        cic = CompositeImage.CompositeImageCollector([])
        si1 = CompositeImage.SingleImage(file_list[0])
        cic.check(si1) # No other way to add image to a checker
        si2 = CompositeImage.SingleImage(file_list[1])
        cic.check(si2)
        n_imgs = len(cic.getCompImage())
        self.assertEqual(2, n_imgs, 'Empty checker case')
     

class SingleImageDict():
    def __init__(self, fl, tg, values):
        global sid
        assert len(values) == len(fl)*len(tg)
        vindex = 0
        for fn in fl:
            for tn in tg: 
                sid[fn+tn] = values[vindex]
                vindex = vindex + 1
    

class CollectHDRStrategyTest(unittest.TestCase):

    def setUp(self):
        self.collect_HDR_strategy = CompositeImage.CollectHDRStrategy()
        
    def test_timestamp(self):
        value = [(2012, 10, 05, 12, 23, 34, 0.01)]

        si = mock.MagicMock()
        si.__getitem__.side_effect = SingleImageSideEffect(value)
        (kezdo, veg) = CompositeImage.timestampFromMetadata(si)
        exp_res = datetime.timedelta(seconds=0.01)
        self.assertEqual(veg-kezdo, exp_res, 'Timedelta: %s instead of %s' %(veg-kezdo, exp_res))

    @mock.patch("CompositeImage.SingleImage", SingleImage_mock)
    def test_findHDR(self):

        

        #SingleImageDict(file_list, tag_list, si_mock_values)
       
        hdrs, sic = self.collect_HDR_strategy.parseFileList(file_list)
        
        
        self.assertFalse(0 == len(hdrs),
                         'No HDR sequence found #sic=%d' % len(sic.getCompImage()))       
        self.assertEqual(4, len(hdrs),
                         'Not all HDRs were found. #hdrs found=%d, single images=%d' % (len(hdrs), len(sic.getCompImage())))        
       
        
        hdr_len_list = [ len(h.getCompImage()) for h in hdrs]
        self.assertEqual(16, sum(hdr_len_list), 'Not all images that belong to an hdr sequence are found')
        self.assertEqual(1, len(sic.getCompImage()), 'Number of single images=%d'%len(sic.getCompImage()))

    @unittest.skip('skip till mocking is complete')
    def test_64076506falsePositive(self):
        hdrs, sic = self.collect_HDR_strategy.parseFileList(glob.glob("/home/smb/tmp/IMG_640[6789].CR2"))
        
        self.assertEqual(0, len(hdrs), 'False positive')
        
    def test_Nepal17425865FalsePositive(self):
        """ 2 különböző géppel egyidőben keszülő, de más exposure bias beállítással készített képek"""
        hdrs, sic = self.collect_HDR_strategy.parseFileList(["/media/MM/Filmek/Nepal/CR2/2012_03_26/IMG_1742.CR2",
                                                            "/media/MM/Filmek/Nepal/CR2/2012_03_26/IMG_5865.CR2"])
        self.assertEqual(0, len(hdrs), 'Nepal False positive')
     
    
class GeneratorTest(unittest.TestCase):
    """ UT of symlink and HDR generators"""
    def setUp(self):
        self.short_fl = file_list[0:5]
        self.CI =CompositeImage.CompositeImage()
        self.CI.getFilelist = mock.MagicMock(name="getFileList")
        self.CI.getFilelist.return_value = self.short_fl
             
    def _runSymlinkGen(self, tdir):
        symlinkgen = CompositeImage.SymlinkGenerator()
        hdr_config = CompositeImage.HDRConfig(tdir)
        symlinkgen(self.CI, hdr_config)
        
    def test_SymlinkGenNoDirExists(self):
        tdir = '/tmp/a/b'
        m =  mock.MagicMock()
        with mock.patch('CompositeImage.os', m):
            self._runSymlinkGen(tdir)
        
        print m.method_calls
        
        self.assertTrue(self.CI.getFilelist.called, 'symlink gen did not call CI.getFilelist')
            
        #Itt nem kell, hogy exception-t dobjon a már létező symlinkek miatt
        m = mock.MagicMock()
        with mock.patch('CompositeImage.os', m):
            self._runSymlinkGen(tdir)

        print m.call_args_list

    def test_HDRGenerator(self):
        self.HDRgen = CompositeImage.HDRGenerator()
        
        hdr_conf= CompositeImage.HDRConfig('/tmp', prefix='HDRTest')
        
        m =mock.MagicMock()
        with mock.patch('CompositeImage.subprocess.call', m):
            self.HDRgen(self.CI, hdr_conf)
        
 #       self.assertTrue(self.CI.getFilelist.called, 'HDRgen did not call CI getFilelist')
        tif_list = [os.path.splitext(os.path.basename(img))[0]+'.TIF' for img in self.short_fl]
        cmds = []
        cmds.append(['align_image_stack', '-atmp', '-p/tmp/HDRTest.pto'] + ['/tmp/TIF/%s'%t for t in tif_list])
        cmds.append(['enfuse', '-o/tmp/HDRTest.TIF'] + ['tmp%04d.tif'%i for i,t in enumerate(tif_list)])
        
        for i, method_call in enumerate(m.method_calls):
            expected = mock.call.call(cmds[i]).call_list()
            l = len(expected)
            self.assertEqual(l, 1, "len(expected)=%d, should be 1" % l)
            self.assertEqual(method_call, expected[0],
                             "call args list:\n%s\nexpected:\n%s" % (method_call, expected))
        

class HDRConfigTest(unittest.TestCase):
    """UT of HDRConfig object. Calls all set and get methods to check if the set value is preserved"""
    def test_SetGet(self):
        hdrc = CompositeImage.HDRConfig('/tmp')
        print dir(hdrc)
    

@unittest.skip('Archaic remain.')        
class ParseTest(unittest.TestCase):
    
    def setUp(self):
         self.checker_head = CompositeImage.CompositeImageCollector()

