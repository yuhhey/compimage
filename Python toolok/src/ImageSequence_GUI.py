#!/usr/bin/python
# -*- coding: utf-8 -*-
# simpledialog.py

import wx
import ImageSequence
import os

class Thumb:

    def __init__(self, parent, path, caption="", size=0, lastmod=0):
        """ Default Class Constructor. """
        
        self._path = path
        self.SetCaption(caption)
        self._id = 0
        self._dir = dir
        self._filesize = size
        self._lastmod = lastmod
        self._parent = parent
        self._captionbreaks = []
        self._bitmap = wx.EmptyBitmap(-1, -1)
        self._image = wx.EmptyImage(-1, -1)
        self._rotation = 0


    def SetCaption(self, caption=""):
        """ Sets Thumb Caption. """
        
        self._caption = caption
        self._captionbreaks = []
    

    def GetImage(self):
        """ Gets Thumb Image. """
        
        return self._image

    
    def SetImage(self, image):
        """ Sets Thumb Image. """
        
        self._image = image        


    def SetBitmap(self, bmp):
        """ Sets Thumb Bitmap. """
        
        self._bitmap = bmp
        

    def GetFileName(self):
        """ Gets Thumb File Name. """
        
        return self._filename


    def SetFileName(self, filename):
        """ Sets Thumb File Name. """
        
        self._filename = filename
        self._bitmap = wx.EmptyBitmap(-1, -1)
        

    def GetId(self):
        """ Returns Thumb Id. """
        
        return self._id


    def SetId(self, id=-1):
        """ Sets Thumb Id. """

        self._id = id
        

    def SetRotatedImage(self, image):
        """ Sets The Image As Rotated (Faster). """
        
        self._rotatedimage = image


    def GetRotatedImage(self):
        """ Gets A Rotated Image. """
        
        return self._rotatedimage
    

    def GetBitmap(self, width, height):
        """ Returns The Bitmap Associated To A Thumb. """
        
        if self.GetRotation() % (2*pi) < 1e-6:
            if not self._bitmap.Ok():
                if not hasattr(self, "_threadedimage"):
                    img = GetMondrianImage()
                else:
                    img = self._threadedimage
                
            else:
                
                img = self._threadedimage
                
        else:

            img = self.GetRotatedImage()

        if hasattr(self, "_originalsize"):
            imgwidth, imgheight = self._originalsize
        else:
            imgwidth, imgheight = (img.GetWidth(), img.GetHeight())
            
        if width < imgwidth or height < imgheight:
            scale = float(width)/imgwidth

            if scale > float(height)/imgheight:
                scale = float(height)/imgheight

            img = img.Scale(int(imgwidth*scale), int(imgheight*scale))
            
        bmp = img.ConvertToBitmap()
                        
        self._image = img

        return bmp

                
    def GetCaption(self, line):
        """ Gets The Caption Associated To A Thumb. """
        
        if line + 1 >= len(self._captionbreaks):
            return ""
        
        strs = self._caption

        return strs        


    def GetFileSize(self):
        """ Returns The File Size Associated To A Thumb. """
        
        return self._filesize


    def GetCreationDate(self):
        """ Returns The File Last Modification Date Associated To A Thumb. """
        
        return self._lastmod        


    def GetCaptionLinesCount(self, width):
        """ Returns The Number Of Lines For The Caption. """
        
        self.BreakCaption(width)
        return len(self._captionbreaks) - 1


    def BreakCaption(self, width):
        """ Breaks The Caption Into Several Lines Of Text. """
        
        if len(self._captionbreaks) > 0 or  width < 16:
            return
        
        self._captionbreaks.append(0)

        if len(self._caption) == 0:
            return

        pos = width/16
        beg = 0
        end = 0

        dc = wx.MemoryDC()
        bmp = wx.EmptyBitmap(10,10)
        dc.SelectObject(bmp)
        
        while 1:
  
            if pos >= len(self._caption):

                self._captionbreaks.append(len(self._caption))
                break

            sw, sh = dc.GetTextExtent(self._caption[beg:pos-beg])
            
            if  sw > width:

                if end > 0:
              
                    self._captionbreaks.append(end)
                    beg = end
              
                else:
                    self._captionbreaks.append(pos)
                    beg = pos
                pos = beg + width/16
                end = 0
            if pos < len(self._caption) and self._caption[pos] in [" ", "-", ",", ".", "_"]:
                end = pos + 1
            pos = pos + 1
        dc.SelectObject(wx.NullBitmap)
        

    def SetRotation(self, angle=0):
        """ Sets Thumb Rotation. """
        self._rotation = angle


    def GetRotation(self):
        """ Gets Thumb Rotation. """
        return self._rotation
    

# ---------------------------------------------------------------------------- #
# Class ThumbnailCtrl
# Auxiliary Class, All Useful Methods Are Defined On ScrolledThumbnail Class.
# ---------------------------------------------------------------------------- #        



class SequenceThumbs:
    def __init__(self):
        pass

class ScrolledSequenceThumbs(wx.ScrolledWindow):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size = wx.DefaultSize):
        
        wx.ScrolledWindow.__init__(self, parent)#, style=wx.HSCROLL)
        self.SetScrollbars(1,1, 600,10)
        self.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_LISTBOX))
        self.Bind(wx.EVT_SIZE, self.OnResize)
        
    def OnResize(self, e):
        print self.GetClientSize()
        parent = self.GetParent()
        pWidth = parent.GetClientSize().GetWidth()
        self.SetSizeHints(50,50, pWidth-160, 50)
        self.Refresh()

class SequenceStrip(wx.Panel):
    
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size = wx.DefaultSize):
        
        wx.Panel.__init__(self, parent, id, pos, size)
        
        self.fixedChkBox = wx.CheckBox(self, -1, "Fixed")
        self.HDRChkBox = wx.CheckBox(self, -1, "HDR")
        self.PanoChkBox = wx.CheckBox(self, -1, "Panorama")
        self.FStackChkBox = wx.CheckBox(self, -1, "Focus stack")
        self.thumbs = ScrolledSequenceThumbs(self)
        
        vs = wx.BoxSizer(wx.VERTICAL)
        vs.Add(self.HDRChkBox, 0, wx.EXPAND)
        vs.Add(self.PanoChkBox, 0, wx.EXPAND)
        vs.Add(self.FStackChkBox, 0, wx.EXPAND)
        hs = wx.BoxSizer(wx.HORIZONTAL)
        hs.Add(self.fixedChkBox, 0, wx.EXPAND)
        hs.Add(vs, 0, wx.EXPAND)
        hs.Add(self.thumbs, 1, wx.EXPAND)
        self.SetSizer(hs)
        self.SetAutoLayout(True)
        hs.Fit(self)
        
class SequenceStripsFrame(wx.ScrolledWindow):
    def __init__(self):
        pass
        
         
        
        

class MainWindow(wx.Frame):
    """Window with the sequence strips and controls"""
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
        self.Bind(wx.EVT_SPIN, self.OnStartButtonPress_CR2_link)
        vs.Add(self.maxdiffSpinner, 0)
        
        startbutton = wx.Button(panel, 3, "Indulhat a mandula!")
        vs.Add(startbutton, 0, wx.ALIGN_CENTER)
        
        seq_strip = SequenceStrip(panel)
        vs.Add(seq_strip, 0, wx.ALIGN_LEFT)
        
        #Itt megeshet, hogy a frame-et kell haszálni
        panel.SetSizer(vs)
        panel.SetAutoLayout(True)
        vs.Fit(panel)
        self.outdirinput.MoveAfterInTabOrder(self.indirinput)
        self.maxdiffSpinner.MoveAfterInTabOrder(self.outdirinput)
        startbutton.MoveAfterInTabOrder(self.maxdiffSpinner)
        #self.indirinput.MoveAfterInTabOrder(startbutton)
        self.Bind(wx.EVT_BUTTON, self.OnStartButtonPress_CR2_link, id=3)
        self.Bind(wx.EVT_SPINCTRL, self.OnStartButtonPress_CR2_link)

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
        
    def OnOutdirShowCustomDialog(self, event):
        self.ShowCustomDialog(self.outdirinput)
        
    def OnStartButtonPress_CR2_link(self, event):
        print "Event happened"
        indir = self.indirinput.GetValue()
        assert os.path.isdir(indir), indir
        outdir = self.outdirinput.GetValue()
        assert os.path.isdir(outdir)
        #maxdiff = int(self.maxdiff_input.GetValue())
        maxdiff = self.maxdiffSpinner.GetValue()   
        cr2_imgseqs = ImageSequence.findSequences(indir, 'CR2', maxdiff)
        print len(cr2_imgseqs), maxdiff
        file_names = FileNameLogic(indir, outdir)
        CR2_dir = file_names.CR2_dir()
        cr2_link_script = ImageSequence.SequenceScriptWriter(CR2_dir, os.path.basename(CR2_dir))
        cr2_link_script.createLinkScript(cr2_imgseqs, owndir = False)
        cr2_link_script.save() 

class MyApp(wx.App):
    def OnInit(self):
        frame = MainWindow(None, -1, 'CR2 link script')
        frame.Show(True)
        frame.Centre()
        return True

app = MyApp(0)
app.MainLoop()