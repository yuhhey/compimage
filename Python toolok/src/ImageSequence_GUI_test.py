#-*- coding: utf-8 -*-

import unittest
import ImageSequence as IS
import ImageSequence_GUI as ISG

class testSequenceThumbs(unittest.TestCase):
    def test_setSeq(self):


""" Testcase-ek, amelyeket a GUI-val való játszadozás közben találtam:
1. Ha a maxdiff változás miatt nem talál seqeunce-t, akkor
    - törölni kell a self.seqTC-t
    - 'No sequence found' to the combobox
2. Ha több mint 10 sequence-et találtunk, akkor a ComboBoxban kiválasztva egy >9 sorszámút
    - a megfelelő sequence-nek kell megjelennie, az eslő számjegyű helyett.
3. Thumbnails in the filelistview is not updated 
   Setup
   1. Input dir kiválaszt
   2. maxdiff spinner set to new value
   Symptom
   The image sequence view is update as should, but the filelist view is not updated until the 'Indulhat a Mandula!' button
   is not pressed
    """ 

""" ThumbNailCtrl bug:
1. Rotation keypresses work only after a mouse click. So to rotate 270 deg using 'd'
   click 'd' click 'd' click 'd' sequence is needed.
2. Nem vagyok benne biztos, hogy ez hiba vagy jó funkció: thumbnail tips nem mozog thumbnailről thumbnailre az egérrel, amíg
   a scrolled windowban maradok.
3. Görgetéskor a tipwindow tartalma nem változik annak ellenére, hogy másik kép kerül az egér alá.
"""