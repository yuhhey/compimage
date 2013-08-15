# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-


import unittest
import inspect
import hsi
import panorama
import random
import mock

class hsiPanoramaMock(mock.MagicMock):
    def readData(self, ifs):
        pass
    
    def getNrOfImages(self):
        pass
        
    def getImage(self, pic_idx):
        pass
    
class hsiSrcPanoImageMock(mock.MagicMock):
    def setRoll(self):
        pass
    def setPitch(self):
        pass
    def setYaw(self):
        pass

class kiegFunkTeszt(unittest.TestCase):
    def addSuffixTest(self):
        fullpath="/storage/Panorama/Lugu/Lugu_Hegye_3_8bit.pto"
        suffix="_teljes"
        result = panorama.addSuffix(fullpath, suffix)
        e_result="/storage/Panorama/Lugu/Lugu_Hegye_3_8bit_teljes.pto"
        self.assertEqual(result,
                         e_result,
                         "Fullpath test")

        rejtett_fajl=".pistike"
        result = panorama.addSuffix(rejtett_fajl, suffix)
        e_result = ".pistike_teljes"
        self.assertEqual(result,
                         e_result,
                         "dot file test")

    def listKeysTest(self):
        e_result=range(1,12)
        adict = {11:2, 8:1, 9:123, 1:1, 5:5, 2:2, 10:1, 7:3, 3:3, 6:2, 4:4}

        result = panorama.listKeys(adict)
        self.assertEqual(result, e_result, 'range(1,12)')
        adict[13]=1
        result = panorama.listKeys(adict)
        self.assertNotEqual(result, e_result, 'Extra 13')
        
class TeljesPanoramaTest(unittest.TestCase):
    def setUp(self):
        self.tp = panorama.TeljesPanorama()
        self.tp.readPTO('../test_input/MarinaBay_esoben.pto')

    def tearDown(self):
        del self.tp
        
    def test_guessExt(self):
        e_result = '.TIF'
        result = self.tp.guessExt()
        self.assertEqual(result,
                         e_result,
                         'guessExtTest: %s vs %s' % (result, e_result))

    def test_updateSize(self):
        self.tp.AnalyzePanorama()
        
        sorok_ptobol = 10
        oszlopok_ptobol = 19

        self.tp.updateSize(0, 0)
        self.assertEqual(self.tp.sorok, sorok_ptobol, 'sorok - %d vs %d' % (self.tp.sorok, sorok_ptobol))
        self.assertEqual(self.tp.oszlopok, oszlopok_ptobol, 'oszlopok - %d vs %d' % (self.tp.oszlopok, oszlopok_ptobol))

        ext_sorok = 12
        self.tp.updateSize(ext_sorok, 0)
        self.assertEqual(self.tp.sorok, ext_sorok, 'sorok - %d vs %d' % (self.tp.sorok, ext_sorok))
        self.assertEqual(self.tp.oszlopok, 5, 'oszlopok - %d vs %d' % (self.tp.oszlopok, 5))


        ext_oszlopok = 21
        self.tp.updateSize(0,ext_oszlopok)
        self.assertEqual(self.tp.sorok, sorok_ptobol, 'sorok - %d vs %d' % (self.tp.sorok, sorok_ptobol))
        self.assertEqual(self.tp.oszlopok, ext_oszlopok, 'oszlopok - %d vs %d' % (self.tp.oszlopok, ext_oszlopok))
        
        ext_sorok_kicsi = 8
        self.tp.updateSize(ext_sorok_kicsi, 0)

    def test_fillBucket(self):
        self.tp.fillBuckets()
        e_yawBucket = {-11.2607813519595: [1, 6], -5.47152753193876: [2, 7], 0.382195302610455: [3, 8], 11.9874309160965: [0, 5, 10], 6.1456880562248: [4, 9]}
        e_pitchBucket = {0.112122265335545: [1, 2, 3, 4, 5], 3.9245062696787: [0], -3.54509678790692: [6, 7, 8, 9, 10]}

        self.assertEqual(e_yawBucket, self.tp.yawBucket, 'yaw')
        self.assertEqual(e_pitchBucket, self.tp.pitchBucket, 'pitch')
        
        
    @unittest.skip("Not implemented")
    def test_GetImageXY(self):
        self.tp.fillBuckets()
        
        xmax = self.tp.oszlopok
        ymax = self.tp.sorok
        
        valid_idx = (1,1)
        outsidey_idx = (1,-1)
        outsidex_idx = (-1, 1)
        missing_idx = (x, y)
        
        img_valid = self.tp.GetImageXY(valid_idx)
    
    @unittest.skip("Not implemented")
    def test_removeFilesInPanorama(self):
        in_fajl_lst = range(12)
        
        out_fajl_lst.self.tp.removeFilesInPanorama(in_fajl_lst)

@unittest.skip("Szomszed testing skipped")
class SzomszedTeszt(unittest.TestCase):
    def setUp(self):
        self.sz = Szomszed()
        x_max = 10
        y_max = 8
        self.sz.setSize(x_max, y_max)
        
        self.o =[('Belső: ', 5, 5)
                 ('Bal alsó: ', 1, 1),
                 ('Bal felső: ', 1, y_max),
                 ('Jobb felső: ', x_max, y_max),
                 ('Jobb alsó: ', x_max, 1),
                 ('Bal oldal: ', 1, y_max - 1),
                 ('Jobb oldal: ', x_max, y_max - 1),
                 ('Alsó oldal: ',x_max - 1, 1),
                 ('Felső oldal: ',x_max - 1, y_max)]
        
    def checkLen(self, cimke, e_res):
        res = len(self.sz)
        self.assertEqual(e_res, res, cimke + ('e_res: %d, res: %d\n' % (e_res, res)))
        
    def test_len(self):
        
        e_res_vector = [8, 3, 3, 3, 3, 5, 5, 5, 5]
        
        i = 0
        for t in self.o:
            self.sz.setOrigo(t[1], t[2])
            self.checkLen(t[0], e_res_vector[i])
            i += 1    
            
    def check_iterator(self, cimke, e_res_vector):
        
        i = 0
        for t in self.sz:
            t1 = t + e_res_vector[i]
            self.assertEqual(t, e_res_vector[i], cimke + ('t = (%d, %d), e_res = (%d, %d)' % t1))
            i += 1
    def test_iterator(self):
        
        print ''


class RealDataTeszt(unittest.TestCase):
    @mock.patch('hsi.Panorama')
    @mock.patch('hsi.SrcPanoImage', spec=hsi.SrcPanoImage)
    def test_WandaPlaza(self, hSrcImgMock, hpanoMock):
        tp = panorama.TeljesPanorama()
        
        tp.readPTO('../test_input/2011_06_23_WandaPlaza_8bit.pto')
        tp.AnalyzePanorama()
        
        tp.calculateHianyzo(3, 5)
        self.assertTrue(tp.p.readData.called)

    def test_getGrid(self):
        
        tp = panorama.TeljesPanorama()
        tp.readPTO('../test_input/2011_06_23_WandaPlaza_8bit.pto')
        tp.AnalyzePanorama()
        
        g = tp.GetGrid()
        for sor in g:
            for k in sor:
                if type(k) is int:
                    print tp.p.getSrcImage(k).getFilename()
                else:
                    print "Nincs kep"
            print
        
        
def suite(testKiegFunk=False, testTeljesPanorama=False):

    suite = unittest.TestSuite()
    
    if testKiegFunk:
        suite.addTest(kiegFunkTeszt('addSuffixTest'))
        suite.addTest(kiegFunkTeszt('listKeysTest'))

    if testTeljesPanorama:
        suite.addTest(TeljesPanoramaTest('guessExtTest'))
        suite.addTest(TeljesPanoramaTest('updateSizeTest'))
        suite.addTest(TeljesPanoramaTest('fillBucketTest'))
    return suite


if __name__ == '__main__':
    rd = RealDataTeszt()
    rd.test_WandaPlaza()
#     runner = unittest.TextTestRunner(verbosity=2)
#     test_suite=suite(testKiegFunk = True,
#                      testTeljesPanorama = True)
#     
#     runner.run(test_suite)
