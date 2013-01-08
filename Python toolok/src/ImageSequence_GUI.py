#!/usr/bin/python
# -*- coding: utf-8 -*-
# simpledialog.py

masszázs heng
import ImageSequence
import ThumbnailCtrl as TC
import os
import re

import echo


class SequenceThumbs:
    def __init__(self):
        pass


class MainWindow(wx.Frame):
    """Window with the sequence strips and controls"""

    

    def setupTC(self, splitter):
        tc = TC.ThumbnailCtrl(splitter)
        tc._scrolled.SetBackgroundColour(wx.Colour(50, 50, 50))
        tc.EnableToolTips(True)
        return tc

    def __init__(self, parent, ID, title):
        wx.Frame.__init__(self, parent, ID, title, size=wx.DefaultSize)
        panel = wx.Panel(self, -1, size=(1200, 300))
        vs = wx.BoxSizer(wx.VERTICAL)
        
        """Menubar"""
        menuBar = self.BuildMenu()
        self.SetMenuBar(menuBar)
        
        for eachInput, eachLabel, eachHandler in self.dirInputData():
            textcontrol, hs = self.createDirInput(panel, eachLabel, eachHandler)
            setattr(self, eachInput, textcontrol)
            vs.Add(hs, 0, wx.EXPAND)
            
            
        self.maxdiffSpinner = wx.SpinCtrl(panel, -1, min=1, max=120, initial=1, name="maxdiff")
        vs.Add(self.maxdiffSpinner, 0)
        self.Bind(wx.EVT_SPINCTRL, self.OnMaxDiffChanged, self.maxdiffSpinner)
        
        
        startbutton = wx.Button(panel, 3, "Indulhat a mandula!")
        vs.Add(startbutton, 0, wx.ALIGN_CENTER)
        self.Bind(wx.EVT_BUTTON, self.OnStartButtonPress, startbutton)
        
        self.seqChoice = wx.ComboBox(panel, -1, style=wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SORT)
        vs.Add(self.seqChoice, 0, wx.EXPAND)
        self.Bind(wx.EVT_COMBOBOX, self.OnSeqChoice, self.seqChoice)
        
        splitter = wx.SplitterWindow(panel, -1, style=wx.CLIP_CHILDREN | wx.SP_3D | wx.WANTS_CHARS)
        
        self.seqTC = self.setupTC(splitter)
        self.dirTC = self.setupTC(splitter)
        splitter.SplitHorizontally(self.seqTC, self.dirTC, 200)
        vs.Add(splitter, 1, wx.EXPAND)
        
        #Itt megeshet, hogy a frame-et kell haszálni
        panel.SetSizer(vs)
        panel.SetAutoLayout(True)
        vs.Fit(panel)
        #self.indirinput.MoveAfterInTabOrder(startbutton)


    
    def BuildMenu(self):
        filemenu = wx.Menu()
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", " ImageSequence GUI information")
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", " Terminate the program")
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        return menuBar

        
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

    
    def ShowCustomDialog(self, dirinput):
        dlg = wx.DirDialog(self, "Choose a directory", style=wx.DD_DEFAULT_STYLE)
        if wx.ID_OK == dlg.ShowModal():
            dirinput.SetValue(dlg.GetPath())
        dlg.Destroy()

            
    def OnAbout(self, e):
        dlg = wx.MessageDialog(self, "Image sequence workflow aid", "About ImageSequenceGUI", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        
    
    def OnExit(self, e):
        self.Close(True)

    
    def OnIndirShowCustomDialog(self, event):
        self.ShowCustomDialog(self.indirinput)
#        self.OnStartButtonPress(event)
        
    def OnOutdirShowCustomDialog(self, event):
        self.ShowCustomDialog(self.outdirinput)
        

    def OnSeqChoice(self, e):
        
        choice = self.seqChoice.GetValue()
        m = re.match("\d+", choice)
        idx = int(choice[m.start():m.end()])
        self.active_seqidx = idx
        self.DisplayActiveSeq()

    def DisplayActiveSeq(self):
        
        if len(self.cr2_imgseqs) == 0:
            return
        indir = self.indirinput.GetValue()
        seq = self.cr2_imgseqs[self.active_seqidx]
        seq_fl = seq.filelist(basenameonly=True)
                        
        self.dirTC._scrolled._selectedarray = []
        
        for i, t in enumerate(self.dirTC._scrolled._items):
            
            tfn = t.GetFileName()
            if tfn in seq_fl:
                
                if not self.dirTC._scrolled._selectedarray:
                    self.dirTC._scrolled._selected = i
                    
                self.dirTC._scrolled._selectedarray.append(i)
                
        self.dirTC._scrolled.ScrollToSelected()
        self.dirTC._scrolled.Refresh()
        self.seqTC.ShowListOfFiles(indir, 1, seq_fl)
        
        
    def FillSeqChoices(self):
        
        if len(self.cr2_imgseqs) > 0:
            
            choices = []
            for i, s in enumerate(self.cr2_imgseqs):
                fl = s.filelist(basenameonly=True)
                fl.sort()
                choice = "%d - %d imgs: %s" % (i, len(fl), fl[0])
                for fn in fl[1:]:
                    choice += ", %s" % fn
                choices.append(choice)
        else:
            choices = ["No sequence found"]
            self.seqTC._scrolled.Clear()
        self.seqChoice.SetItems(choices)
        self.seqChoice.Select(0)
            


    def RecalculateSeqs(self):
        
        indir = self.indirinput.GetValue()
        if not os.path.isdir(indir):
            return None
        
        wx.BeginBusyCursor()
        maxdiff = self.maxdiffSpinner.GetValue()
        self.cr2_imgseqs = ImageSequence.findSequences(indir, 'CR2', maxdiff)
        if len(self.cr2_imgseqs) > 0:
            self.FillSeqChoices()
        print len(self.cr2_imgseqs), maxdiff
        wx.EndBusyCursor()
        return indir


    def ResetSeqDisplay(self):
        self.active_seqidx = 0
        self.DisplayActiveSeq()


    def OnStartButtonPress(self, event):
        indir = self.RecalculateSeqs()           
        self.dirTC.ShowDir(indir, 1)

        self.ResetSeqDisplay()


    def OnMaxDiffChanged(self,e):
       
        print e.GetEventType()
        self.maxdiffSpinner.Enable(False)
        self.RecalculateSeqs()
        self.ResetSeqDisplay()
        self.maxdiffSpinner.Enable(True)
        

echo.echo_class(MainWindow)
#echo.echo_class(TC.ScrolledThumbnail)

class MyApp(wx.App):
    def OnInit(self):
        frame = MainWindow(None, -1, 'Sequence finder')
        frame.Show(True)
        frame.Centre()
        return True

app = MyApp(0)
app.MainLoop()