# -*- coding: utf-8 -*-

import panorama as pano
def genTempleOfHeaven_1():
    fajl_l = range(6539, 6544)
    fajl_l += range(6546,6555)
    fajl_l += range(6558,6567)    
    fajl_l += range(6570,6579)
    fajl_l += range(6583,6586)    
    fajl_path='/storage/Panorama/Peking_201204/TempleOfHeaven/8bit/IMG_'
    pto = '/storage/Panorama/Peking_201204/TempleOfHeaven8bit_1.pto'
    tp = pano.TeljesPanorama()
    tp.generateTeljes(pto, fajl_path, fajl_l)
    
def genTempleOfHeaven_2():
    fajl_l = range(6501, 6504)
    fajl_l += [6507, 6508, 6512]
    
    fajl_path='/storage/Panorama/Peking_201204/TempleOfHeaven/8bit/IMG_'
    pto = '/storage/Panorama/Peking_201204/TempleOfHeaven8bit_2.pto'
    tp = pano.TeljesPanorama()
    tp.generateTeljes(pto, fajl_path, fajl_l)
    
def genChangPingGou_ToMellol_1():
    fajl_l = [7389, 7390, 7405]   
    fajl_path='/storage/Panorama/SiGuNiang_201204/ChangPingGou_ToMellol_1/8bit/IMG_'
    pto = '/storage/Panorama/SiGuNiang_201204/ChangPingGou_ToMellol_1_8bit.pto'
    tp = pano.TeljesPanorama()
    tp.generateTeljes(pto, fajl_path, fajl_l)
def genChangPingGou_ToMellol_2():
    fajl_l = [7510, 7511, 7501,7502, 7503, 7504, 7507]
    fajl_path='/storage/Panorama/SiGuNiang_201204/ChangPingGou_ToMellol_2/8bit/IMG_'
    pto = '/storage/Panorama/SiGuNiang_201204/ChangPingGou_ToMellol_2_8bit.pto'
    tp = pano.TeljesPanorama()
    tp.epsilon = 5.0 # az egész megdőlt, ezért kell nagyobb epszilon.
    tp.generateTeljes(pto, fajl_path, fajl_l)
    
def genChangPingGou_ToMellol_3():
    fajl_l = [7567, 7556, 7557]
    fajl_path='/storage/Panorama/SiGuNiang_201204/ChangPingGou_ToMellol_3/8bit/IMG_'
    pto = '/storage/Panorama/SiGuNiang_201204/ChangPingGou_ToMellol_3_8bit.pto'
    tp = pano.TeljesPanorama()
    tp.epsilon = 5.0 # az egész megdőlt, ezért kell nagyobb epszilon.
    tp.generateTeljes(pto, fajl_path, fajl_l)

def genTiltottVaros():
    fajl_l = range(6343, 6349) + [6352]
    fajl_path='/storage/Panorama/Peking_201204/TiltottVaros/8bit/IMG_'
    pto = '/storage/Panorama/Peking_201204/TiltottVaros_8bit.pto'
    tp = pano.TeljesPanorama()
    tp.generateTeljes(pto, fajl_path, fajl_l)

def genTienAnMenTer():
    fajl_l = range(6422, 6429) + range(6435, 64378) + range(6438,6446)
    fajl_path='/storage/Panorama/Peking_201204/TienAnMenTer/8bit/IMG_'
    pto = '/storage/Panorama/Peking_201204/TienAnMenTer_8bit.pto'
    tp = pano.TeljesPanorama()
    tp.generateTeljes(pto, fajl_path, fajl_l)

def genGandhrukbol_1():
    fajl_l = range(1730, 1739) + range(1721, 1727) + range(1707, 1714) + range(1694,1701) + range(1689, 1692) + range(1675, 1688) + range(1662, 1675)
    fajl_path='/storage/Panorama/Nepal/Gandhrukbol_1/8bit/IMG_'
    pto = '/storage/Panorama/Nepal/Gandhrukbol_1_8bit.pto'
    tp = pano.TeljesPanorama()
    tp.oszlopok = 13
    tp.sorok = 6
    tp.generateTeljes(pto, fajl_path, fajl_l)
    
def genGandhrukbol_2():
# A sorrend szerintem nem jó
    fajl_l = range(1809, 1818) + [1798] + range(1800, 1805) + range(1787, 1792) + range(1766, 1769) + range(1772, 1779) + range(1753, 1766) + range(1740, 1753)
    fajl_path='/storage/Panorama/Nepal/Gandhrukbol_2/8bit/IMG_'
    pto = '/storage/Panorama/Nepal/Gandhrukbol_2_8bit.pto'
    tp = pano.TeljesPanorama()
    tp.oszlopok = 13
    tp.sorok = 6
    tp.generateTeljes(pto, fajl_path, fajl_l)
    
def genGandhrukbol_3():
    fajl_l = range(1899, 1903) + range(1886, 1890) + range(1860, 1862) + range(1846, 1851) + range(1825, 1828) + range(1830, 1838)
    fajl_path='/storage/Panorama/Nepal/Gandhrukbol_3/8bit/IMG_'
    pto = '/storage/Panorama/Nepal/Gandhrukbol_3_8bit.pto'
    tp = pano.TeljesPanorama()
    tp.oszlopok = 13
    tp.sorok = 6
    tp.generateTeljes(pto, fajl_path, fajl_l)
    
def genDanba_fele_2():
    fajl_l = [8627] + range(8617, 8619) + range(8607, 8615)
    fajl_path='/storage/Panorama/SiGuNiang_201204/Danba_fele_2/8bit/IMG_'
    pto = '/storage/Panorama/SiGuNiang_201204/Danba_fele_2_8bit.pto'
    tp = pano.TeljesPanorama()
    tp.generateTeljes(pto, fajl_path, fajl_l)
    
def genChangPingGou_Felutrol_1():
    fajl_l = range(7887, 7890) + range(7858, 7866) + range(7877, 7879) + range(7834, 7843) + range(7852, 7858)
    fajl_path='/storage/Panorama/SiGuNiang_201204/ChangPingGou_Felutrol_1/8bit/IMG_'
    pto = '/storage/Panorama/SiGuNiang_201204/ChangPingGou_Felutrol_1_8bit.pto'
    tp = pano.TeljesPanorama()
    tp.generateTeljes(pto, fajl_path, fajl_l)
    
def genChangPingGou_Bejarat_1():
    fajl_l = [8005, 8017, 8018]
    fajl_path='/storage/Panorama/SiGuNiang_201204/ChangPingGou_Bejarat_1/8bit/IMG_'
    pto = '/storage/Panorama/SiGuNiang_201204/ChangPingGou_Bejarat_1_8bit.pto'
    tp = pano.TeljesPanorama()
    tp.generateTeljes(pto, fajl_path, fajl_l)

def genShuangQiao_vegen():
    fajl_l = range(8244, 8249) + range(8254, 8264)
    fajl_path='/storage/Panorama/SiGuNiang_201204/ShuangQiao_vegen/8bit/IMG_'
    pto = '/storage/Panorama/SiGuNiang_201204/ShuangQiao_vegen_8bit.pto'
    tp = pano.TeljesPanorama()
    tp.generateTeljes(pto, fajl_path, fajl_l)
    
def genBorneo_MtKinabaluSzallasrol_setup():
    fajl_l =range(6295,6298)
    fajl_l += [6304,6305]
    fajl_l += range(6284,6295)
    fajl_l += range(6273,6284)
    fajl_l += range(6262,6273)
    fajl_l += range(6251,6262)
    fajl_path = "/storage/Panorama/Borneo/MtKinabaluSzallasrol/8bit/IMG_"
    pto = '/storage/Panorama/Borneo/Borneo_MtKinabaluSzallasrol_8bit.pto'
    tp = pano.TeljesPanorama()
    tp.generateTeljes(pto, fajl_path, fajl_l, sorok=9)

def genBorneo_MtKinabaluUtMellol_3_setup():
    fajl_l=[6491]
    fajl_l+=range(6476,6486)
    fajl_l+=range(6461,6476)
    fajl_l+=range(6446,6461)
    fajl_l+=range(6431,6446)
    fajl_l+=range(6416,6431)
    fajl_path="/storage/Panorama/Borneo/MtKinabaluUtmellol_3/8bit/IMG_"
    pto = '/storage/Panorama/Borneo/Borneo_MtKinabaluUtmellol_3_8bit.pto'
    tp = pano.TeljesPanorama()
    tp.generateTeljes(pto, fajl_path, fajl_l, sorok=8)

def genMerlionElol_2_setup():
    fajl_l=range(8852,8859)
    fajl_path='/storage/Panorama/Szingapur/2011_10_03/MerlionElol_2/8bit_kicsi/IMG_'
    pto = '/storage/Panorama/Szingapur/2011_10_03/MerlionElol_2_8bit_kicsi.pto'
    tp = pano.TeljesPanorama()
    tp.generateTeljes(pto, fajl_path, fajl_l, sorok=4)    
    
def genMtKinabaluUtmellol_1_setup():
    fajl_l=range(6381,6385)
    fajl_l+=range(6376,6381)
    fajl_l+=range(6371,6376)
    fajl_l+=range(6366, 6371)
    fajl_path='/storage/Panorama/Borneo/MtKinabaluUtmellol_1/8bit/IMG_'
    pto = '/storage/Panorama/Borneo/Borneo_MtKinabaluUtmellol_1_8bit.pto'
    tp = pano.TeljesPanorama()
    tp.generateTeljes(pto, fajl_path, fajl_l, sorok=6)
    
def genSomersetTetejerol():
    fajl_l  = range(1186, 1212)
    fajl_l += range(1212, 1225)
    fajl_l += range(1232, 1239)
    fajl_l.append(1300)
    fajl_l.append(1361)
    fajl_l.append(1387)
    fajl_l += range(1420, 1424)
    fajl_l += range(1446, 1451)
    fajl_l += range(1472, 1477)
    fajl_l += range(1498, 1504)
    fajl_l += range(1524, 1527)
    fajl_l += range(1550, 1553)
    fajl_l += range(1576, 1583) + range(1590, 1592)
    fajl_l += range(1602, 1611) + range(1616, 1618)
    fajl_l += range(1627, 1638) + range(1642, 1645) + range(1647,1654)
    fajl_path='/storage/Panorama/SomersetTetejerol/2011_11_09/8bit_kicsi/IMG_'
    pto = '/storage/Panorama/SomersetTetejerol/SomersetTetejerol_2011_11_09_8bit_kicsi.pto'
    tp = pano.TeljesPanorama()
    tp.generateTeljes(pto, fajl_path, fajl_l, sorok=18)
    
def genLuguHegye4():
    
    fajl_l=range(1111,1119)
    fajl_l+=range(1122,1126)
    fajl_l+=range(1133,1144)
    fajl_path="/storage/Panorama/Lugu/Lugu_Hegye_4/8bit/IMG_"
    pto='/storage/Panorama/Lugu/Lugu_Hegye_4_8bit.pto'
    tp = pano.TeljesPanorama()
    tp.generateTeljes(pto, fajl_path, fajl_l, sorok=10)

def genFelhokarcolokKozott():
    
    fajl_l = [9575, 9576]
    fajl_l += [9419, 9426, 9427, 9432, 9434, 9435]
    fajl_path="/storage/Panorama/Szingapur/2012_05_12/FelhokarcolokKozott/8bit/IMG_"
    pto="/storage/Panorama/Szingapur/2012_05_12/Szingapur_2012_05_12_FelhokarcolokKozott_8bit.pto"
    tp = pano.TeljesPanorama()
    tp.generateTeljes(pto, fajl_path, fajl_l, kiterjesztes='jpg')
    
genFelhokarcolokKozott()
