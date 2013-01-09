#!/usr/bin/python
# -*- coding: utf-8 -*-


import wx

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(450, 350))

      	splitter = wx.SplitterWindow(self, -1)
		
        panel1 = wx.Panel(splitter, -1)
        panel1.SetBackgroundColour(wx.WHITE)
        panel2 = wx.Panel(splitter, -1)
        panel2.SetBackgroundColour(wx.WHITE)
        splitter.SplitVertically(panel1, panel2)

        self.tree = wx.TreeCtrl(panel1, 1, wx.DefaultPosition, (-1,-1), wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS)
        root = self.tree.AddRoot('Composite images')
        hdr = self.tree.AppendItem(root, 'HDR')
        pano = self.tree.AppendItem(root, 'Panoramas')
        fstacked = self.tree.AppendItem(root, 'Focus stacked')

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.tree, 1, wx.EXPAND)
        panel1.SetSizer(vbox)
        self.Centre()
        
class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, 'treectrl.py')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

app = MyApp(0)
app.MainLoop()