# -*- coding: utf-8 -*-

import unittest
import inspect
import panorama
import random
import mock
import hsi
import raw_data


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
        self.assertEqual(self.tp.sorok, sorok_ptobol,
                         'sorok - %d vs %d' % (self.tp.sorok, sorok_ptobol))
        self.assertEqual(self.tp.oszlopok, oszlopok_ptobol,
                         'oszlopok - %d vs %d' % (self.tp.oszlopok,
                                                  oszlopok_ptobol))

        ext_sorok = 12
        self.tp.updateSize(ext_sorok, 0)
        self.assertEqual(self.tp.sorok, ext_sorok,
                         'sorok - %d vs %d' % (self.tp.sorok, ext_sorok))
        self.assertEqual(self.tp.oszlopok, 5,
                         'oszlopok - %d vs %d' % (self.tp.oszlopok, 5))


        ext_oszlopok = 21
        self.tp.updateSize(0,ext_oszlopok)
        self.assertEqual(self.tp.sorok, sorok_ptobol,
                         'sorok - %d vs %d' % (self.tp.sorok, sorok_ptobol))
        self.assertEqual(self.tp.oszlopok, ext_oszlopok,
                         'oszlopok - %d vs %d' % (self.tp.oszlopok,
                                                  ext_oszlopok))
        
        ext_sorok_kicsi = 8
        self.tp.updateSize(ext_sorok_kicsi, 0)

    def test_fillBucket(self):
        self.tp.fillBuckets()
        e_yawBucket = {-11.2607813519595: [1, 6],
                       -5.47152753193876: [2, 7],
                       0.382195302610455: [3, 8],
                       11.9874309160965: [0, 5, 10],
                       6.1456880562248: [4, 9]}
        e_pitchBucket = {0.112122265335545: [1, 2, 3, 4, 5],
                         3.9245062696787: [0],
                         -3.54509678790692: [6, 7, 8, 9, 10]}

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
        self.assertEqual(e_res, res,
                         cimke + ('e_res: %d, res: %d\n' % (e_res, res)))
        
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
            self.assertEqual(t, e_res_vector[i],
                             cimke + ('t = (%d, %d), e_res = (%d, %d)' % t1))
            i += 1
    def test_iterator(self):
        print ''


def getPitch(img):
    return img.getPitch()

def getYaw(img):
    return img.getYaw()

def getNrOfImages(pano):
    return len(raw_data.Wandafele_ejszaka_8bit)

def getImage(pano, index):
    return raw_data.Wandafele_ejszaka_8bit[index]

class Wandafele_ejszaka_8bit(unittest.TestCase):
    
    def setUp(self):
        self.fn = "../test_input/2011_06_23_Wandafele_ejszaka_8bit.pto"
        
    @mock.patch.object(hsi.SrcPanoImage, 'getPitch')
    @mock.patch.object(hsi.SrcPanoImage, 'getYaw')
    @mock.patch.object(hsi.Panorama, 'getImage', getImage)
    @mock.patch.object(hsi.Panorama, 'getNrOfImages', getNrOfImages)
    def test_WandaPlaza(self, mock_y, mock_p):
        mock_y.side_effect = raw_data.Wandafele_ejszaka_8bit_yaw_side_effect        
        mock_p.side_effect = raw_data.Wandafele_ejszaka_8bit_pitch_side_effect
        
        tp = panorama.TeljesPanorama()
        tp.readPTO(self.fn)
        tp.AnalyzePanorama()
        
        self.assertEqual(4, len(tp.pitchBucket), "Not 4 rows")
        self.assertEqual(19, len(tp.yawBucket), "Not 19 columns")
        
    def test_getGrid(self):
        
        tp = panorama.TeljesPanorama()
        tp.readPTO(self.fn)
        tp.AnalyzePanorama()
        
        g = tp.GetGrid()
        for sor in g:
            for k in sor:
                if type(k) is int:
                    print tp.p.getSrcImage(k).getFilename()
                else:
                    print "Nincs kep"
            print
            
        print len(g)
        
class ListGrids(object):
    def process(self, fn):
        tp = panorama.TeljesPanorama()
        tp.readPTO(fn)
        tp.AnalyzePanorama()
        
        g = tp.GetGrid()
        
        print fn
        
        for s in g:
            sor = ""
            for e in s:
                sor = sor + "%4d" % e 
            
            print sor
            
# TODO ../test_input/MarinaBayKeletiCsucsok_2_8bit_kicsi.pto
#   -1  -1  -1  -1   0   1  -1  -1  -1  -1   2   3
#    4  -1  -1  -1   5   6  -1  -1   7   8   9  10
#   -1  12  13  14  -1  -1  -1  -1  -1  20  -1  -1
#   11  -1  -1  -1  15  16  17  18  19  -1  21  22
#   23  24  25  26  27  28  29  30  31  32  33  34
        
        
# TODO ../test_input/2011_07_08_Hatalmas_8bit.pto
#   -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 402  -1  -1  -1  -1  -1  -1 388  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 375  -1  -1  -1  -1  -1 362  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 106  -1  -1  -1  93  -1  -1  -1 363  -1  -1  -1 209  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 376  -1  -1  -1 105 102  -1 210  92  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 390  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1
#  403  -1  -1  -1 416  -1  -1  -1  75  -1  -1  -1  -1 415  -1  -1  76  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 401  -1  -1  -1  -1  -1  -1  -1 387  -1  -1  -1  -1  -1  -1  -1 374  -1  -1  -1  -1  -1  -1  -1 361  -1  -1 348  -1  -1 349  -1  -1  -1  -1  -1 104 107  -1  94  -1  -1  -1  -1  -1  -1 208 350  -1  -1 115  -1  -1  -1 124  -1  -1  -1 204  -1  -1  -1 364  -1  -1  -1  -1 123 114  -1 205 377  -1  -1  91  -1  -1  -1  -1 391  -1  -1  -1  -1  -1  -1 211  -1 404  -1  -1  -1  74  -1  -1  -1  -1  -1  -1  -1  -1  -1
#   -1  -1  -1  -1  -1  -1  -1  57  -1  -1  -1  -1  58  -1  -1  -1  -1  -1  -1  -1  -1 414  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 336  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 337  -1  -1  -1  -1 203  -1  -1  -1  -1  -1 351  -1  -1  -1 300  -1  -1  -1  -1  -1  -1 132  -1 291  -1  -1  -1  -1  -1 281  -1  -1  -1  -1  -1  73  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  56  -1  -1  -1  -1  -1
#   -1  -1  -1 465  -1  -1  39  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  77  -1  -1  -1  -1  -1 413  -1  -1  -1  -1  -1 400  -1  -1  -1 386  -1  -1  -1  -1 373  -1  -1  -1  -1 360  -1  -1  -1  -1 347  -1  -1 335  -1  -1  -1  -1  -1  -1 108  95  -1  -1  -1 117  -1  -1  -1  -1  -1  -1 125 134  -1  -1  -1 338 101  -1 133 151  -1  -1  -1 198 192  -1  -1 329  -1 141 290 193 321  -1  90 378 313  -1  -1 200 392  -1  -1 271  -1  -1 201 261  55  -1 418 207  -1  -1  -1 454  -1  -1 417  -1  -1  38 460  -1  -1
#   -1  -1  -1  -1  -1  21 469  -1  -1  -1  -1  40  -1  -1  -1  -1  -1  -1  59  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 399  -1  -1 385  -1  -1 372  -1  -1  -1 359  -1  -1  -1  -1  -1  -1  -1 334  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 126  -1  -1 144  -1  -1  -1  -1 152  -1  -1  -1  -1 191  -1 339  -1  -1  -1  -1  -1  -1 328  -1 227  -1 320  -1  -1 312 379  -1 194  72  -1  -1 260  -1 195  -1  -1  -1  -1  -1 446  -1  -1 202  -1  -1  -1  -1  -1  -1  -1  -1  -1 466  -1 461
#   -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  22  -1  -1  -1  23  41  -1  -1  -1  -1  -1  60  -1  78  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 346  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 160  -1  -1  -1  -1 186  -1 226  -1  -1  -1 187  -1  -1  -1  -1  -1  -1  -1 393  -1  -1  54 406  -1  -1  36  -1  -1  -1  -1  -1  -1  -1  -1  19  -1  -1  -1 455  -1  -1  20  -1  -1
#  462 470  -1  -1 474   3  -1  -1 473   4  -1  -1  -1  -1  -1  -1  -1  -1  -1  42  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 412  -1  -1  -1  -1 398  -1  -1 384  -1 371  -1  -1 358  -1  -1  -1  -1  -1  -1  -1 333  -1  -1  -1  -1  -1  -1  -1 109  -1  96  -1 118  -1 127  -1 145 136  -1 154  -1  -1 153 162  -1  -1  -1 161  -1 170  -1 185 169  -1  -1  -1 340 178 168  -1 353 222 289 179 232 279 269 380 259  -1 252 219  -1 229 430  -1  -1  -1 250 419 240  -1 439  -1  -1  -1 241  -1  -1   1  -1 467  -1 456 471   2  -1
#   -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1   5  -1  -1   6  -1  24  -1  -1  -1  43  -1  61  -1  -1  79  -1  -1  -1  -1  -1  -1  -1 411  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 345  -1  -1 332  -1  -1  -1  -1  -1  -1  -1  -1  -1 110  97  -1 128  -1 146 137  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 212  -1  -1  -1 225  -1  -1 258  -1  -1  -1  -1  -1 394 181  -1 422 407  -1  -1  -1 272 431  -1  -1  -1   0  -1  -1  -1  -1  -1 448  -1  -1  -1  -1  -1  -1  -1
#  475 463  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 410  -1 397  -1  -1 383 370  -1 357  -1  -1 344  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 155  -1 164  -1  -1 163 172  -1 171  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 341 213  -1  -1 288 224 257 368  -1 243 317  -1 395 248  -1 408 249 182 273 420 283  -1  -1 282  -1 432 292 220 440 301 468  -1 221 472 449  -1 476 457  -1
#   -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1   7  -1  25  -1  44  -1  -1  62  -1  -1  80  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 331  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 111  98 129 120  -1 138 156  -1  -1  -1  -1  -1 173  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 342  -1 267 355  -1  -1 265 256  -1 325 264 316  -1  -1  -1 421  -1  -1  -1  -1 424 293  -1  -1  -1  -1  -1  -1  -1 441  -1  -1  -1  -1  -1  -1  -1
#   -1  -1 464  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1   8  26  -1  -1  45  -1  63  -1  -1  81  -1  -1  -1  -1  -1  -1 409 396  -1  -1 382 369  -1 356  -1 343  -1 330  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 112  -1 121 139 157  -1  -1  -1 165  -1 174  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 214  -1 266  -1  -1 234 244 308 237 254 307  -1 324 306 274  -1 323 314 322 294  -1  -1  -1 425  -1 433  -1  -1  -1  -1 442  -1 450  -1  -1 458
#  459  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1   9  27  -1  -1  -1  46  64  -1  -1  82  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 113 131  -1 122 140  -1  -1 166  -1 175  -1  -1  -1 183  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 215  -1  -1  -1 235 236 245  -1  -1  -1  -1  -1 275  -1  -1  -1  -1 295  -1  -1 303  -1  -1  -1 426  -1  -1 434  -1  -1  -1 443 451  -1  -1
#   -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  10  28  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 100  -1  -1  -1  -1 167  -1 176  -1  -1 184  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 304  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 435  -1  -1  -1  -1  -1
#   -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  47  -1  65  -1  83  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 216  -1  -1  -1  -1  -1  -1  -1  -1  -1 276  -1  -1  -1  -1 296 305  -1  -1  -1  -1  -1  -1  -1  -1  -1 427  -1  -1 436 444  -1 452  -1
#   -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  11  -1  29  -1  -1  -1  66  -1  84  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 217  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1
#  453  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 297  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 428  -1  -1 437  -1 445  -1
#   -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  12  -1  30  48  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1
#   -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  67  85  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 218  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1 429  -1  -1  -1  -1  -1
#   -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  13  31  -1  49  -1  -1  -1  86  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1
#   -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  68  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1
#   -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  14  32  -1  50  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1
#   -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  87  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1
#   -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  15  33  51  -1  69  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1
#   -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  88  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1
#   -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  16  34  -1  52  70  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1
#   -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  89  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1
#   -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  17  35  53  -1  71  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1  -1
        
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
    lg = ListGrids()
    result = inspect.getmembers(raw_data)
    for m in result:
        if (-1 == m[0].find("side_effect")) and (m[0].find("pto_") == 0):
            fn = "../test_input/"+m[0][4:]+".pto"
            lg.process(fn)
    
    
    #rd = RealDataTeszt()
    #rd.test_WandaPlaza()
#     runner = unittest.TextTestRunner(verbosity=2)
#     test_suite=suite(testKiegFunk = True,
#                      testTeljesPanorama = True)
#     
#     runner.run(test_suite)
