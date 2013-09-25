import panorama
import sys
import os
import random

tp = panorama.TeljesPanorama()
tp.readPTO(sys.argv[1])

pto_nev = "pto_" + os.path.splitext(os.path.basename(sys.argv[1]))[0]

NrOfImages = tp.p.getNrOfImages()

print pto_nev,'= ['

img_idxs = range(NrOfImages)

random.shuffle(img_idxs)
y_l = []
p_l = []
r_l =[]
for i in img_idxs:
    img = tp.p.getImage(i)
    y = img.getYaw()
    y_l.append(y)
    p = img.getPitch()
    p_l.append(p)
    r = img.getRoll()
    r_l.append(r)
    fn = img.getFilename()
    
    print "ImageData(", '%17.13f,%17.13f,%17.13f, \"%s\"),' %(y, p, r, fn)
    
    
print ']'

def print_list(l, n):
    r =""
    for i in range(len(l)):
        r = r + ('%17.13f,' % l[i])
        if (i%n) == 0:
            r = r + '\n'
    return r
            
print pto_nev+"_yaw_side_effect = [", print_list(y_l, 4), "]"
print pto_nev+"_pitch_side_effect = [", print_list(p_l, 4), "]"
print pto_nev+"_roll_side_effect = [", print_list(r_l, 4), "]"