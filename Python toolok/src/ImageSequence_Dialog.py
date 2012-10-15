#!/usr/bin/python
# -*- coding: utf-8 -*-
# simpledialog.py

import wx
import HDRList
import os

class MyFrame(wx.Frame):
    """ Main window of the application"""
        
    def dirInputData(self):
        return (('indirinput', "Input directory: ", self.OnIndirShowCustomDialog),
                ('outdirinput', "Output directory: ", self.OnOutdirShowCustomDialog))

    def createDirInput(self, parent, label, handler, defValue= u'', buttonLabel = '...'):
        cimke = wx.StaticText(parent, -1, label)
        dirinput = wx.TextCtrl(parent, -1, defValue, style=wx.TE_LEFT)
        button = wx.Button(parent, -1, buttonLabel)
        self.Bind(wx.EVT_BUTTON, handler, button)
        
        hs = wx.BoxSizer(wx.HORIZONTAL)
        
        hs.Add(cimke, 0, wx.ALIGN_LEFT)
        hs.Add(dirinput, 1, wx.ALIGN_CENTER)
        hs.Add(button,0)
        return (dirinput, hs)

    def __init__(self, parent, ID, title):
        wx.Frame.__init__(self, parent, ID, title)
        
        vs = wx.BoxSizer(wx.VERTICAL)
        for eachInput, eachLabel, eachHandler in self.dirInputData():
            textcontrol, hs = self.createDirInput(self, eachLabel, eachHandler)
            setattr(self, eachInput, textcontrol)
            vs.Add(hs, 0, wx.EXPAND)
            
        self.prefixinput = wx.TextCtrl(self, -1, u'',style = wx.TE_LEFT)
        startbutton = wx.Button(self, 3, "Indulhat a mandula!")
        
        vs.Add(self.prefixinput, 0, wx.EXPAND)
        vs.Add(startbutton, 0, wx.ALIGN_CENTER)
        
        self.SetSizer(vs)
        self.Bind(wx.EVT_BUTTON, self.OnStartButtonPress, id=3)


    def ShowCustomDialog(self, dirinput):
        dlg = wx.DirDialog(self, "Choose a directory", style=wx.DD_DEFAULT_STYLE)
        if wx.ID_OK == dlg.ShowModal():
            dirinput.SetValue(dlg.GetPath())
        dlg.Destroy()

    def OnIndirShowCustomDialog(self, event):
        print "indir event"
        self.ShowCustomDialog(self.indirinput)
        
    def OnOutdirShowCustomDialog(self, event):
        print "outdir event"
        self.ShowCustomDialog(self.outdirinput)
        
    def OnStartButtonPress(self, event):
        
        indir = self.indirinput.GetValue()
        outdir = self.outdirinput.GetValue()
        prefix = self.prefixinput.GetValue()
        
        if '' == prefix:
            prefix = 'Set' + os.path.basename(indir)
        
        HDRList.generateMoveScript(indir,
                                   outdir,
                                   prefix)
        HDRList.generateHDRScript(indir,
                                  outdir,
                                  prefix)
        

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, 'customdialog2.py')
        frame.Show(True)
        frame.Centre()
        return True

app = MyApp(0)
app.MainLoop()