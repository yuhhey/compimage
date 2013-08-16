# -*- coding: utf-8 -*-

import unittest
import inspect
import panorama
import random
import mock
import hsi

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
        
@unittest.skip("Sokat szemetel a consolre")
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

class ImageData(object):
    def __init__(self, yaw, pitch, roll, fn):
        
        self.__yaw = yaw
        self.__pitch = pitch
        self.__roll = roll
        self.__fn = fn
        
    def getYaw(self):
        return self.__yaw
    
    def getPitch(self):
        return self.__pitch
    
    def getRoll(self):
        return self.__roll
    
    def getFilename(self):
        return self.__fn

Wandafele_ejszaka_8bit = [
ImageData(  -0.139998,     -2.473094,     -0.014117,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0169.TIF"),
ImageData(  -3.544796,     -4.429023,     -0.024607,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0149.TIF"),
ImageData( -24.293692,     -0.572447,      0.025070,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0181.TIF"),
ImageData(  10.251049,     -0.464287,      0.016425,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0191.TIF"),
ImageData(  17.210039,     -0.442005,      0.014827,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0193.TIF"),
ImageData(  13.729056,     -4.349158,      0.003992,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0154.TIF"),
ImageData( -31.117706,     -2.496060,      0.036679,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0160.TIF"),
ImageData(   6.780103,     -6.253309,     -0.037561,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0133.TIF"),
ImageData(  31.073329,     -6.130340,      0.014264,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0140.TIF"),
ImageData(  24.144788,     -0.391376,      0.025262,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0195.TIF"),
ImageData(  -3.542304,     -6.309135,     -0.033563,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0130.TIF"),
ImageData(  24.143109,     -6.148399,     -0.022981,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0138.TIF"),
ImageData(  10.256283,     -6.235661,     -0.008376,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0134.TIF"),
ImageData( -24.289881,     -4.463217,     -0.002218,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0143.TIF"),
ImageData(  10.252908,     -2.414761,      0.004706,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0172.TIF"),
ImageData(  27.614342,     -4.266298,      0.002571,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0158.TIF"),
ImageData( -10.491441,     -6.319399,     -0.046559,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0128.TIF"),
ImageData( -20.865664,     -2.515701,      0.002485,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0163.TIF"),
ImageData(  -7.017981,     -0.548934,      0.000485,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0186.TIF"),
ImageData( -24.287542,     -6.340275,      0.001909,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0124.TIF"),
ImageData( -13.902046,     -4.447806,     -0.010937,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0146.TIF"),
ImageData(  31.074217,     -2.317782,      0.030811,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0178.TIF"),
ImageData(  10.254946,     -4.368124,     -0.016072,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0153.TIF"),
ImageData(  -7.012104,     -4.439715,     -0.005508,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0148.TIF"),
ImageData( -20.862597,     -6.339211,     -0.012916,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0125.TIF"),
ImageData(  13.729205,     -2.394338,      0.010996,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0173.TIF"),
ImageData( -27.702427,     -2.510390,      0.014820,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0161.TIF"),
ImageData( -27.699991,     -4.458229,      0.004478,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0142.TIF"),
ImageData(   3.297643,     -4.403498,     -0.010600,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0151.TIF"),
ImageData(  -3.551576,     -0.530303,     -0.005068,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0187.TIF"),
ImageData( -31.112720,     -4.440637,      0.003652,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0141.TIF"),
ImageData( -10.497616,     -2.499445,      0.010605,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0166.TIF"),
ImageData( -20.864595,     -4.464410,     -0.003212,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0144.TIF"),
ImageData( -13.906430,     -0.560192,      0.036281,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0184.TIF"),
ImageData( -31.119242,     -0.550702,      0.073160,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0179.TIF"),
ImageData(   3.301373,     -6.272905,     -0.013656,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0132.TIF"),
ImageData( -13.904565,     -2.501049,      0.031299,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0165.TIF"),
ImageData( -27.702802,     -0.568048,      0.032726,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0180.TIF"),
ImageData(  27.614416,     -2.314229,      0.025179,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0177.TIF"),
ImageData(  17.213048,     -4.334997,     -0.013811,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0155.TIF"),
ImageData(  31.072474,     -4.266159,      0.016403,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0159.TIF"),
ImageData(  20.651816,     -2.360090,      0.005962,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0175.TIF"),
ImageData(  -0.136654,     -4.433293,     -0.001518,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0150.TIF"),
ImageData(  13.730079,     -6.215967,     -0.017739,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0135.TIF"),
ImageData(  -7.008342,     -6.320150,     -0.021048,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0129.TIF"),
ImageData( -17.401887,     -0.573909,      0.037449,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0183.TIF"),
ImageData(  -7.014756,     -2.493016,     -0.005594,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0167.TIF"),
ImageData(  27.619949,     -6.143259,     -0.006377,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0139.TIF"),
ImageData(  20.647666,     -0.414115,      0.022867,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0194.TIF"),
ImageData(  17.219403,     -6.209586,     -0.019043,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0136.TIF"),
ImageData(   6.771208,     -0.480370,     -0.003490,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0190.TIF"),
ImageData(  20.654370,     -6.178864,     -0.029101,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0137.TIF"),
ImageData(  31.073629,     -0.370727,      0.027926,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0197.TIF"),
ImageData( -17.399434,     -2.513188,      0.017607,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0164.TIF"),
ImageData( -31.114372,     -6.327434,     -0.027663,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0122.TIF"),
ImageData(   6.772884,     -2.433939,      0.000958,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0171.TIF"),
ImageData(  24.144259,     -2.332145,      0.011716,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0176.TIF"),
ImageData( -13.897208,     -6.323557,     -0.027310,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0127.TIF"),
ImageData( -30.998680,     -6.323782,     -0.023901,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0121.TIF"),
ImageData( -10.499360,     -0.558394,      0.012832,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0185.TIF"),
ImageData(  -0.143663,     -0.524373,      0.007231,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0188.TIF"),
ImageData( -17.394920,     -6.334057,     -0.020151,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0126.TIF"),
ImageData( -10.495433,     -4.439554,     -0.021614,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0147.TIF"),
ImageData(   3.288697,     -0.497365,      0.005145,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0189.TIF"),
ImageData( -24.291490,     -2.512379,      0.007746,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0162.TIF"),
ImageData(  -3.548739,     -2.473268,     -0.010371,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0168.TIF"),
ImageData(  27.616244,     -0.371152,      0.033991,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0196.TIF"),
ImageData( -17.398327,     -4.461295,     -0.007466,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0145.TIF"),
ImageData( -20.867384,     -0.573387,      0.020695,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0182.TIF"),
ImageData(  -0.134861,     -6.301773,     -0.043633,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0131.TIF"),
ImageData(  13.726187,     -0.449999,      0.031663,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0192.TIF"),
ImageData(   6.778229,     -4.385763,     -0.042429,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0152.TIF"),
ImageData(  20.648328,     -4.302587,     -0.011143,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0156.TIF"),
ImageData(  17.215773,     -2.391160,      0.002845,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0174.TIF"),
ImageData(  24.142259,     -4.279651,     -0.006358,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0157.TIF"),
ImageData( -27.695125,     -6.336321,     -0.020067,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0123.TIF"),
ImageData(   3.295696,     -2.448434,     -0.005127,    "2011_06_23/Wandafele_ejszaka/8bit/IMG_0170.TIF"),
]

def getPitch(img):
    return img.getPitch()

def getYaw(img):
    return img.getYaw()

def getNrOfImages(pano):
    return len(Wandafele_ejszaka_8bit)

def getImage(pano, index):
    return Wandafele_ejszaka_8bit[index]

class RealDataTeszt(unittest.TestCase):
    
    @mock.patch.object(hsi.SrcPanoImage, 'getPitch')
    @mock.patch.object(hsi.SrcPanoImage, 'getYaw')
    @mock.patch.object(hsi.Panorama, 'getImage', getImage)
    @mock.patch.object(hsi.Panorama, 'getNrOfImages', getNrOfImages)
    def test_WandaPlaza(self, mock_y, mock_p):
        
        mock_y.side_effect = [-0.139998,
                              -3.544796,
                              -24.293692,
                              10.251049,
                              17.210039,
                              13.729056,
                              -31.117706,
                              6.780103,
                              31.073329,
                              24.144788,
                              -3.542304,
                              24.143109,
                              10.256283,
                              -24.289881,
                              10.252908,
                              27.614342,
                              -10.491441,
                              -20.865664,
                              -7.017981,
                              -24.287542,
                              -13.902046,
                              31.074217,
                              10.254946,
                              -7.012104,
                              -20.862597,
                              13.729205,
                              -27.702427,
                              -27.699991,
                              3.297643,
                              -3.551576,
                              -31.112720,
                              -10.497616,
                              -20.864595,
                              -13.906430,
                              -31.119242,
                              3.301373,
                              -13.904565,
                              -27.702802,
                              27.614416,
                              17.213048,
                              31.072474,
                              20.651816,
                              -0.136654,
                              13.730079,
                              -7.008342,
                              -17.401887,
                              -7.014756,
                              27.619949,
                              20.647666,
                              17.219403,
                              6.771208,
                              20.654370,
                              31.073629,
                              -17.399434,
                              -31.114372,
                              6.772884,
                              24.144259,
                              -13.897208,
                              -30.998680,
                              -10.499360,
                              -0.143663,
                              -17.394920,
                              -10.495433,
                              3.288697,
                              -24.291490,
                              -3.548739,
                              27.616244,
                              -17.398327,
                              -20.867384,
                              -0.134861,
                              13.726187,
                              6.778229,
                              20.648328,
                              17.215773,
                              24.142259,
                              -27.695125,
                              3.295696,]
        
        mock_p.side_effect = [-2.473094,
-4.429023,
-0.572447,
-0.464287,
-0.442005,
-4.349158,
-2.496060,
-6.253309,
-6.130340,
-0.391376,
-6.309135,
-6.148399,
-6.235661,
-4.463217,
-2.414761,
-4.266298,
-6.319399,
-2.515701,
-0.548934,
-6.340275,
-4.447806,
-2.317782,
-4.368124,
-4.439715,
-6.339211,
-2.394338,
-2.510390,
-4.458229,
-4.403498,
-0.530303,
-4.440637,
-2.499445,
-4.464410,
-0.560192,
-0.550702,
-6.272905,
-2.501049,
-0.568048,
-2.314229,
-4.334997,
-4.266159,
-2.360090,
-4.433293,
-6.215967,
-6.320150,
-0.573909,
-2.493016,
-6.143259,
-0.414115,
-6.209586,
-0.480370,
-6.178864,
-0.370727,
-2.513188,
-6.327434,
-2.433939,
-2.332145,
-6.323557,
-6.323782,
-0.558394,
-0.524373,
-6.334057,
-4.439554,
-0.497365,
-2.512379,
-2.473268,
-0.371152,
-4.461295,
-0.573387,
-6.301773,
-0.449999,
-4.385763,
-4.302587,
-2.391160,
-4.279651,
-6.336321,
-2.448434,]
        
        tp = panorama.TeljesPanorama()
        
        tp.readPTO('../test_input/2011_06_23_WandaPlaza_8bit.pto')
        tp.AnalyzePanorama()
        tp.calculateHianyzo(3, 5)
        print tp.yawBucket
        print tp.yawValues
        print tp.pitchBucket
        print tp.pitchValues
        

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
