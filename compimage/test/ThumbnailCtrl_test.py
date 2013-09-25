#-*- coding: utf-8 -*-

import unittest
import ThumbnailCtrl as TC
import wx

class  TCTest(unittest.TestCase, wx.Frame):
    jpg_full_path = '/storage/Kepek/kepek_eredeti/IXUS970IS'
    cr2_full_path = '/storage/Kepek/kepek_eredeti/CR2/2009_12_13'
    
    def __init__(self, parent, id=-1, title="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)
        
    
    def setUp(self):
        self.seqTC = TC.ThumbnailCtrl(self)
        
    
    def test_ShowDir(self):
        self.seqTC.ShowDir(self.jpg_full_path)
        
    
    def test_ShowGlob(self):
        self.seqTC.ShowGlob(self.jpg_full_path+'/2009_06_04/*')
        self.seqTC.ShowGlob(self.cr2_full_path+'/*')
    
        


if __name__ == "__main__":
    
    app = wx.PySimpleApp()
    frame = TCTest(None, -1, "ThumbnailCtrl UT ;-)")
    frame.setUp()
    frame.test_ShowGlob()
    frame.CenterOnScreen()
    frame.Show()

    app.MainLoop()