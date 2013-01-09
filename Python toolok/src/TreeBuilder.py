#-*- coding: utf-8 -*-

import wx
import os
import errno

class Expander(object):
    def __init__(self,treectrl, itemID):
        
        self.tree = treectrl
        self.itemID = itemID
        self.tree.SetPyData(itemID, self)
        
    def isExpanded(self):
        raise NotImplementedError
                            
    def expand(self, *ars, **kwargs):
        raise NotImplementedError
    
    
class DirectoryExpander(Expander):
    def __init__(self, treectrl, path, itemID = None):
        if not os.path.isdir(path):
            raise OSError(errno.ENOENT, os.strerror(errno.ENOENT))
        self.path = path
        if itemID == None:
            itemID = treectrl.AddRoot(path)
        
        treectrl.SetItemHasChildren(itemID)
        self.expanded = False
        Expander.__init__(self,treectrl, itemID)
        
    def isExpanded(self):
        return self.expanded
        
    def expand(self):

        if self.isExpanded():
            return
        
        for i in os.listdir(self.path):
            fullpath = os.path.join(self.path, i)
            if os.path.isdir(fullpath):
                child = self.tree.AppendItem(self.itemID, i)
                DirectoryExpander(self.tree, fullpath, child)
        self.expanded = True
                
class TreeCtrlFrame(wx.Frame):
    def __init__(self, parent, id, title, rootdir):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(450, 350))
        panel = wx.Panel(self, -1)
        self.tree = wx. TreeCtrl(panel, 1, wx.DefaultPosition, (-1,-1), wx.TR_HAS_BUTTONS)
        expander = DirectoryExpander(self.tree, '/')
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tree, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        sizer.Fit(self)
        self.Layout()
        
        self.tree.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.onItemExpand, id=1)
        
    def onItemExpand(self, event):
        item = event.GetItem()
        data = self.tree.GetPyData(item)
        if not data.isExpanded():
            data.expand()


class TestExpandersApp(wx.App):
    def OnInit(self):
        frame = TreeCtrlFrame(None, -1, 'Test expanders', '/')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True


if __name__ == "__main__":
    app = TestExpandersApp()
    app.MainLoop()

