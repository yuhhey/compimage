# -*- coding: utf-8 -*-

import hsi
import os
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr

def addSuffix(path, suffix):
    t=os.path.splitext(path)
    return t[0] + suffix + t[1]


def LinReg3DEgyutthatok(x, y, z):
        r_x=robjects.FloatVector(x)
        r_y=robjects.FloatVector(y)
        r_z=robjects.FloatVector(z)
        fmla=robjects.Formula('z ~ x + y')
        env=fmla.environment
        env['x']=r_x
        env['y']=r_y
        env['z']=r_z
        stats=importr('stats')
        fit=stats.lm(fmla)
    
        egyutthatok=stats.coef(fit)
        return egyutthatok

def listKeys(adict):
    alist = adict.keys()
    alist.sort()
    return alist
    
IDX={"C":0, "XM":1, "YM":2}
PAR={"Y":1, "X":2, "ROLL":3, "PITCH":4, "YAW":5, "FILENAME":6}

class TeljesPanorama(object):

    def __init__(self):

        self.pto_nev=""
        self.fajl_path = ""
        self.fajl_l = []
        
        self.sorok = 0
        self.oszlopok = 0

        self.epsilon = 2.0 # Erre az értékre érzékeny az eredmény. A teljes panorama automatikus forgatás segíthet talán
        
        self.yawBucket = {}
        self.pitchBucket = {}
        self.yawValues = []
        self.pitchValues = []
        self.x_coord = []
        self.y_coord = []
        self.roll = []
        self.yaw = []
        self.pitch = []
        self.p = hsi.Panorama()
        self.roll_eh = robjects.vectors.FloatVector
        self.yaw_eh = robjects.vectors.FloatVector
        self.pitch_eh = robjects.vectors.FloatVector
        
    def readPTO(self, filename):
        self.pto_nev = filename
        ifs=hsi.ifstream(filename)
        self.p.readData(ifs)
        del ifs

    def fillBucket(self, bucket, getParameter):
        """ Fills the 'bucket' dictionary with parameter values within self.epszilon """
        for pic in range(self.p.getNrOfImages()):
            img=self.p.getImage(pic)
            yaw=getParameter(img)
            found=False

            for i in bucket.keys():
                if (abs(yaw - i) < self.epsilon):
                    bucket[i].append(pic)
                    found=True
                    break

            if False==found :
                bucket[yaw]=list()
                bucket[yaw].append(pic)

    def fillBuckets(self):
        self.fillBucket(self.yawBucket, hsi.SrcPanoImage.getYaw)
        self.fillBucket(self.pitchBucket, hsi.SrcPanoImage.getPitch)

    def addFajlToPTO(self, fajlnev, roll, pitch, yaw,crop_factor):
        #print crop_factor
        uj_kep=hsi.SrcPanoImage(fajlnev)
        uj_kep.setRoll(roll)
        uj_kep.setPitch(pitch)
        uj_kep.setYaw(yaw)
        uj_kep.setExifCropFactor(crop_factor)
        self.p.addImage(uj_kep)
        
    def updateSize(self, sorok, oszlopok):
        """ Updates the amount of rows and columns in the final panorama """
        if (0 != sorok):
            self.sorok=sorok
        if (0 != oszlopok):
            self.oszlopok=oszlopok
        if (0 == self.sorok):
            self.sorok = max(self.y_coord)
        if (0 == self.oszlopok):
            self.oszlopok = max(self.x_coord)
            
    def guessExt(self):
        """ Guess the extension to use to add the extra images"""
        img = self.p.getImage(0)
        return os.path.splitext(img.getFilename())[1]

    def genYawPitchValues(self):
        self.yawValues = listKeys(self.yawBucket)
        self.pitchValues = listKeys(self.pitchBucket)

    def AnalyzePanorama(self):
        #print inspect.stack()[0][3]
        self.fillBuckets()

        self.genYawPitchValues()

        eredmeny=list()

        t=range(self.p.getNrOfImages())
        for x in range(len(self.pitchValues)):
            l2=self.pitchBucket[self.pitchValues[x]]
            for y in range(len(self.yawValues)):
                l1=self.yawBucket[self.yawValues[y]]
                for i in l1:
                    if i in l2:
                        t.remove(i)
                        img=self.p.getImage(i)
                        eredmeny.append([i,
                                        x+1,
                                        y+1,
                                        img.getRoll(),
                                        img.getPitch(),
                                        img.getYaw(),
                                        img.getFilename()])
                        break
        for i in range(len(t)):
            img=self.p.getImage(t[i])
    #        print i, img.getFilename(), img.getPitch(), img.getYaw()
        for i in range(len(eredmeny)):
    ##            print( '%d %d %f %f %f %s' % (eredmeny[i][PAR["Y"]],
    ##                                         eredmeny[i][PAR["X"]],
    ##                                         eredmeny[i][PAR["ROLL"]],
    ##                                         eredmeny[i][PAR["PITCH"]],
    ##                                         eredmeny[i][PAR["YAW"]],
    ##                                         eredmeny[i][PAR["FILENAME"]]))
            self.y_coord.append(eredmeny[i][PAR["Y"]])
            self.x_coord.append(eredmeny[i][PAR["X"]])
            self.roll.append(eredmeny[i][PAR["ROLL"]])
            self.pitch.append(eredmeny[i][PAR["PITCH"]])
            self.yaw.append(eredmeny[i][PAR["YAW"]])
            
    def illeszt(self):
        #print inspect.stack()[0][3]
        self.roll_eh=LinReg3DEgyutthatok(self.x_coord,
                                         self.y_coord,
                                         self.roll)
        self.yaw_eh=LinReg3DEgyutthatok(self.x_coord,
                                        self.y_coord,
                                        self.yaw)
        self.pitch_eh=LinReg3DEgyutthatok(self.x_coord,
                                         self.y_coord,
                                         self.pitch)

    def calculateHianyzo(self, sorok = 0, oszlopok = 0):
        #print inspect.stack()[0][3]
        self.x_hianyzo=[]
        self.y_hianyzo=[]
        self.updateSize(sorok, oszlopok)
        #print self.sorok, self.oszlopok
        index=0
        i=0
        sor=1
        oszlop=0

        while (i + index) < self.sorok*self.oszlopok:
            oszlop += 1
            if ((i >= len(self.x_coord)) or not((self.x_coord[i] == oszlop) and (self.y_coord[i] == sor))):
                index += 1
                self.x_hianyzo.append(oszlop)
                self.y_hianyzo.append(sor)
                
            else:
                i += 1

            oszlop=oszlop%self.oszlopok
            if (0 == oszlop):
                sor += 1

    def kiegeszit(self, fajl_path, fajl_l, kiterjesztes='TIF'):
        #print inspect.stack()[0][3]
        self.fajl_l=fajl_l
        self.fajl_path=fajl_path
        
        crop_factor=self.p.getImage(0).getExifCropFactor()
        # TODO: objective adatokat rámásolni
        
        for i in range(len(self.x_hianyzo)):
            
            roll_szamolt = self.roll_eh[IDX["C"]] \
                         + self.x_hianyzo[i]*self.roll_eh[IDX["XM"]] \
                         + self.y_hianyzo[i]*self.roll_eh[IDX["YM"]]
                         
            pitch_szamolt = self.pitch_eh[IDX["C"]] \
                          + self.x_hianyzo[i]*self.pitch_eh[IDX["XM"]] \
                          + self.y_hianyzo[i]*self.pitch_eh[IDX["YM"]]
                          
            yaw_szamolt = self.yaw_eh[IDX["C"]] \
                        + self.x_hianyzo[i]*self.yaw_eh[IDX["XM"]] \
                        + self.y_hianyzo[i]*self.yaw_eh[IDX["YM"]]
                        
            fajlnev=(self.fajl_path+"%04d.%s") % (self.fajl_l[i], kiterjesztes)
            
            self.addFajlToPTO(fajlnev, roll_szamolt,\
                              pitch_szamolt, yaw_szamolt, crop_factor)
        
    def writePTO(self, fajlnev=""):
        #print inspect.stack()[0][3]
        if ("" == fajlnev):
            fajlnev = self.pto

        ofs=hsi.ofstream(fajlnev)
        self.p.writeData(ofs)
        del ofs

    def generateTeljes(self, fajlnev, fajl_path, fajl_l, sorok=0, oszlopok=0, suffix="_teljes", kiterjesztes='TIF'):
        #print inspect.stack()[0][3]
        self.readPTO(fajlnev)
        self.AnalyzePanorama()
        self.illeszt()
        self.calculateHianyzo(sorok, oszlopok)
        
        self.kiegeszit(fajl_path, fajl_l, kiterjesztes)
        fajlnev=addSuffix(self.pto_nev, suffix)
        self.writePTO(fajlnev)
        print "Kiírva: "

    def GetGrid(self):
        g = ()
        """ külön lista tárolja az egyes értékeket, mert az eredeti dict-ben biztosan nem rendezetten vannak"""
        for p in reversed(self.pitchValues):
            pitchs = set(self.pitchBucket[p])
            sor = ()
            for y in self.yawValues:
                yaws = set(self.yawBucket[y])
                m = yaws&pitchs
                if m:
                    sor = sor +(m.pop(),)
                else:
                    sor = sor + ("nincs kep",)
                
            g = g + (sor,)
        
        return g