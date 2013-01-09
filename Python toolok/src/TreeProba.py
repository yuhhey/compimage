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


class Command:
    def __init__(self, notify_window):
        self._notify_window = notify_window
        self._want_abort = 0
    
    def Finished(self,data):
        wx.PostEvent(self._notify_window, data)
        
    
    def abort(self):    
        self._want_abort = 1
        
        
    def abortWanted(self):
        return self._want_abort != 0
        
        
class HDRCommand(Command):
    def __init__(self, _notify_window, tree, itemID):
        Command.__init__(self, _notify_window)
        self.tree = tree
        self.itemID = itemID
        self.imgs_processed = 0
        # Imagelist for progress icons on HDR nodes 
        self.il = wx.ImageList(16,16)
        self.tree.AssignImageList(self.il)
        self.questidx = self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_QUESTION, wx.ART_OTHER, (16,16)))
        self.readyidx = self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK, wx.ART_OTHER, (16,16)))
        self.abortidx = self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK, wx.ART_OTHER, (16,16)))
        
    
    def __call__(self):
        self.processItem(self.itemID)    
        
    
    def processItem(self, itemID):
        """Recursive processing of HDR sets"""
        data = self.tree.GetPyData(itemID)[0]
        if isinstance(data, CI.CompositeImageCollector):
            parentID = self.tree.GetItemParent(itemID)
            self.tree.SetItemImage(itemID, self.questidx,wx.TreeItemIcon_Normal)
            path = self.tree.GetPyData(parentID)[0]
            hdr_gen = CI.HDRGenerator()
            hdr_gen.setParams(os.path.dirname(path), '.tiff', self.tree.GetItemText(itemID))
            ci = data.getCompImage()
            self._notify_window.button.Enable()
            hdr_gen(ci)
            self.tree.SetItemImage(itemID, self.readyidx,wx.TreeItemIcon_Normal)
            self.imgs_processed = self.imgs_processed + 1
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
        wx.PostEvent(self._notify_window, ResultEvent(self.imgs_processed))
        
        
class WorkerThread(TH.Thread):
    """Worker Thread Class."""
    def __init__(self, cmd):
        """Init Worker Thread Class."""
        TH.Thread.__init__(self)
        self._cmd = cmd
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()


    def run(self):
        """Run Worker Thread."""
        self._cmd()
        
        
    def abort(self):
        self._cmd.abort()
    
    
class Config(object):
    def __init__(self, name):
        self.maxdiff = 7
        self.CR2_dirs = []
        self.img_dir = ""
        self.name = name
        
    def display(self, tree, parentID):
        
        configItemID = tree.AppendItem(parentID, self.name)
        img_dir = 'Image output dir: %s' % self.img_dir
        tree.AppendItem(configItemID, img_dir)
        maxdiff = 'maxdiff: %d sec' % self.maxdiff
        tree.AppendItem(configItemID, maxdiff)
        CR2_dirID = tree.AppendItem(configItemID, 'CR2 dirs')
        for d in self.CR2_dirs:
            tree.AppendItem(CR2_dirID, d)
        
        


class MyFrame(wx.Frame):
    '''Main policy object of the application'''
    def __init__(self, *args, **kwds):
        # this is just setup boilerplate
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        # our tree object, self.tree
        self.tree = wx.TreeCtrl(self, -1, style=wx.TR_HAS_BUTTONS|wx.TR_EDIT_LABELS|wx.TR_LINES_AT_ROOT, size = wx.Size(200,500))
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
        wx.EVT_TREE_END_LABEL_EDIT(self.tree, self.tree.GetId(), self.onLabelEdited)
        self.button.Bind(wx.EVT_BUTTON, self.onAbortPress)
        
        # Set up event handler for any worker thread results
        EVT_RESULT(self,self.onResult)
        # initialize the tree
        self.buildTree('/home/smb')
        
        # store the worker thread later here.
        self.worker = None
                

    def GetCheckedItem(self, event):
        itemID = event.GetItem()
        if not itemID.IsOk():
            itemID = self.tree.GetSelection()
        return itemID


    def onLabelEdited(self,event):
        print event
        itemID = self.GetCheckedItem(event)
        rootID = self.tree.GetRootItem()
        
        if itemID == rootID:
            path = event.GetLabel()
            if os.path.isdir(path):
                wx.CallAfter(self.rebuildTree, path)
            else:
                event.Veto()
      

    def onRightClick(self, event):
        itemID = self.GetCheckedItem(event)
        
        self.worker = WorkerThread(HDRCommand(self, self.tree, itemID))
        

    def onExpand(self, event):
        '''onExpand is called when the user expands a node on the tree
        object. It checks whether the node has been previously expanded. If
        not, the extendTree function is called to build out the node, which
        is then marked as expanded.'''

        # get the wxID of the entry to expand and check it's validity
        itemID = self.GetCheckedItem(event)

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
        print '%d images processed' % event.data
        
    
    def onAbortPress(self, event):
        self.worker.abort()
        self.button.SetLabel('Aborting...')
        
        
    def rebuildTree(self, rootdir):
        self.tree.DeleteAllItems()
        self.buildTree(rootdir)


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
        d = self.tree.GetPyData(parentID)
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
                
                cr2_p = os.path.join(child_path, '*.CR2')
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
                try:
                    newsubdirs = dircache.listdir(newParentPath)
                except OSError, msg:
                    print '%s: raised exception:%s' %(newParentPath, msg)
                newsubdirs.sort()
                for grandchild in newsubdirs:
                    grandchild_path = os.path.join(newParentPath,grandchild)
                    if os.path.isdir(grandchild_path) and not os.path.islink(grandchild_path):
                        grandchildID = self.tree.AppendItem(newParentID, grandchild)
                        self.tree.SetPyData(grandchildID, (grandchild_path,False))

        cr2_p = os.path.join(parentDir, '*.CR2')
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
    frame = MyFrame(None, -1, "Composite Image GUI", size=wx.Size(450, 350))
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()