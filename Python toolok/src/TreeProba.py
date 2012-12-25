# -*- coding: utf-8 -*-

import wx
import os.path, dircache
import glob
import CompositeImage as CI
import threading as TH

# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()

def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)

class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

# Thread class that executes processing
class WorkerThread(TH.Thread):
    """Worker Thread Class."""
    def __init__(self, notify_window, tree, itemID):
        """Init Worker Thread Class."""
        TH.Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        self.tree = tree
        self.itemID = itemID
        
        # Imagelist for progress icons on HDR nodes 
        self.il = wx.ImageList(16,16)
        self.tree.AssignImageList(self.il)
        self.questionidx = self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_QUESTION, wx.ART_OTHER, (16,16)))
        self.readyidx = self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK, wx.ART_OTHER, (16,16)))
        self.abortidx = self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK, wx.ART_OTHER, (16,16)))
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):
        """Run Worker Thread."""
        self.processItem(self.itemID)
    
    def processItem(self, itemID):
        """Recursive processing of HDR sets"""
        data = self.tree.GetPyData(itemID)[0]
        if isinstance(data, CI.CompositeImageCollector):
            parentID = self.tree.GetItemParent(itemID)
            self.tree.SetItemImage(itemID, self.questionidx,wx.TreeItemIcon_Normal)
            path = self.tree.GetPyData(parentID)[0]
            hdr_gen = CI.HDRGenerator()
            hdr_gen.setParams(os.path.dirname(path), '.tiff', self.tree.GetItemText(itemID))
            ci = data.getCompImage()
            self._notify_window.button.Enable()
            hdr_gen(ci)
            self.tree.SetItemImage(itemID, self.readyidx,wx.TreeItemIcon_Normal)
        else:
            # Egyelőre feltesszük, hogy direktori
            (child, cookie) = self.tree.GetFirstChild(itemID)
            while child.IsOk():
                if self._want_abort:
                    self.tree.SetItemImage(child, self.abortidx,wx.TreeItemIcon_Normal)
                else:
                    self.processItem(child)
                (child, cookie) = self.tree.GetNextChild(itemID, cookie)

        # Here's where the result would be returned (this is an
        # example fixed result of the number 10, but it could be
        # any Python object)
        if self._want_abort:
            # Use a result of None to acknowledge the abort (of
            # course you can use whatever you'd like or even
            # a separate event type)
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return
        
        wx.PostEvent(self._notify_window, ResultEvent(10))

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = 1


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # this is just setup boilerplate
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        # our tree object, self.tree
        self.tree = wx.TreeCtrl(self, -1, style=wx.TR_DEFAULT_STYLE|wx.TR_EDIT_LABELS|wx.TR_LINES_AT_ROOT, size = wx.Size(200, 500))
        self.button = wx.Button(self, -1, label = 'Abort')

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tree, 1, wx.EXPAND, 0)
        sizer.Add(self.button, 0, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        sizer.Fit(self)
        sizer.SetSizeHints(self)
        self.Layout()
        self.button.Disable()
        # register the self.onExpand function to be called
        wx.EVT_TREE_ITEM_EXPANDING(self.tree, self.tree.GetId(), self.onExpand)
        wx.EVT_TREE_ITEM_RIGHT_CLICK(self.tree, self.tree.GetId(), self.onRightClick)
        self.button.Bind(wx.EVT_BUTTON, self.onAbortPress)
        
        # Set up event handler for any worker thread results
        EVT_RESULT(self,self.onResult)
        # initialize the tree
        self.buildTree('/home/smb')
        
        # store the worker thread later here.
        self.worker = None
                
                
    def onRightClick(self, event):
        itemID = event.GetItem()
        if not itemID.IsOk():
            itemID = self.tree.GetSelection()
        
        self.worker = WorkerThread(self, self.tree, itemID)
        

    def onExpand(self, event):
        '''onExpand is called when the user expands a node on the tree
        object. It checks whether the node has been previously expanded. If
        not, the extendTree function is called to build out the node, which
        is then marked as expanded.'''

        # get the wxID of the entry to expand and check it's validity
        itemID = event.GetItem()
        if not itemID.IsOk():
            itemID = self.tree.GetSelection()

        # only build that tree if not previously expanded
        old_pydata = self.tree.GetPyData(itemID)
        if old_pydata[1] == False:
            # clean the subtree and rebuild it
            self.tree.DeleteChildren(itemID)
            self.extendTree(itemID)
            self.tree.SetPyData(itemID,(old_pydata[0], True))


    def onResult(self, event):
        self.button.Disable()
        self.button.SetLabel('Abort')
        
    
    def onAbortPress(self, event):
        self.worker.abort()
        self.button.SetLabel('Aborting...')

    def buildTree(self, rootdir):
        '''Add a new root element and then its children'''
        self.rootID = self.tree.AddRoot(rootdir)
        self.tree.SetPyData(self.rootID, (rootdir,1))
        self.extendTree(self.rootID)
        self.tree.Expand(self.rootID)


    def extendTree(self, parentID):
        '''extendTree is a semi-lazy directory tree builder. It takes
        the ID of a tree entry and fills in the tree with its child
        subdirectories and their children - updating 2 layers of the
        tree. This function is called by buildTree and onExpand methods'''

        # This is something to work around, because Windows will list
        # this directory but throw a WindowsError exception if you
        # try to use the listdir() command on it. I need a better workaround
        # for this...this is a temporary kludge.
        excludeDirs=["c:\\System Volume Information","/System Volume Information"]

        # retrieve the associated absolute path of the parent
        parentDir = self.tree.GetPyData(parentID)[0]


        subdirs = dircache.listdir(parentDir)
        subdirs.sort()
        for child in subdirs:
            child_path = os.path.join(parentDir,child)
            if os.path.isdir(child_path) and not os.path.islink(child):
                if child_path in excludeDirs or '.' == child[0]:
                    continue
                # add the child to the parent
                childID = self.tree.AppendItem(parentID, child)
                # associate the full child path with its tree entry
                self.tree.SetPyData(childID, (child_path, False))
                
                cr2_p = os.path.join(child_path, '*.tiff')
                CR2s = glob.glob(cr2_p)
        
                for img in CR2s:
                    CR2_ID = self.tree.AppendItem(childID, os.path.basename(img))
                    self.tree.SetPyData(CR2_ID, (img, True))
                    
                
                # Now the child entry will show up, but it current has no
                # known children of its own and will not have a '+' showing
                # that it can be expanded to step further down the tree.
                # Solution is to go ahead and register the child's children,
                # meaning the grandchildren of the original parent
                newParent = child
                newParentID = childID
                newParentPath = child_path
                newsubdirs = dircache.listdir(newParentPath)
                newsubdirs.sort()
                for grandchild in newsubdirs:
                    grandchild_path = os.path.join(newParentPath,grandchild)
                    if os.path.isdir(grandchild_path) and not os.path.islink(grandchild_path):
                        grandchildID = self.tree.AppendItem(newParentID, grandchild)
                        self.tree.SetPyData(grandchildID, (grandchild_path,False))

        cr2_p = os.path.join(parentDir, '*.tiff')
        CR2s = glob.glob(cr2_p)
        hdrcollector = CI.CollectHDRStrategy()
        hdrs, sic = hdrcollector.parseFileList(CR2s)
        
        for i, hdr in enumerate(hdrs):
            HDR_ID = self.tree.AppendItem(parentID, 'hdr%02d' % i)
            self.tree.SetPyData(HDR_ID, (hdr, True))
            for img in hdr.getCompImage():
                img_ID = self.tree.AppendItem(HDR_ID, os.path.basename(img))
                self.tree.SetPyData(img_ID,(img, False))
                

if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame = MyFrame(None, -1, "", size=wx.Size(450, 350))
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()