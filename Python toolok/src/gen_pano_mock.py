import panorama
import sys
import os
import random

tp = panorama.TeljesPanorama()
tp.readPTO(sys.argv[1])

pto_nev = os.path.splitext(os.path.basename(sys.argv[1]))[0]

NrOfImages = tp.p.getNrOfImages()

print pto_nev,'= ['

img_idxs = range(NrOfImages)

random.shuffle(img_idxs)

for i in img_idxs:
    img = tp.p.getImage(i)
    y = img.getYaw()
    p = img.getPitch()
    r = img.getRoll()
    fn = img.getFilename()
    
    print "ImageData(", '%10f,\t%10f,\t%10f,\t\"%s\"),' %(y, p, r, fn)
    
    
print ']'
    
    