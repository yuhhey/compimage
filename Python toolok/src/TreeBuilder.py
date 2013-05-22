#-*- coding: utf-8 -*-9

import wx
import os
import errno
import CompositeImage
import copy
import threading as TH
import time
import glob
import pickle


class HDRConfigPanel(wx.Panel):
    
    def __init__(self, *args, **kw):
        self.hdr_config = copy.deepcopy(kw['hdr_config'])
        del kw['hdr_config']
        self.path = kw['path']
        del kw['path']
        
        super(HDRConfigPanel, self).__init__(*args, **kw)
        self.InitUI()

    def inputFieldData(self):
        return (("targetDir", "Target directory:", self.onTargetDir, self.hdr_config.GetTargetDir()),
                ("rawExt", "Raw extension:", self.onRawExtension, self.hdr_config.GetRawExt()),
                ("imageExt", "Output image ext:", self.onImageExt, self.hdr_config.GetImageExt()),
                ("prefix", "Output prefix:", self.onPrefix, self.hdr_config.GetPrefix()),
                ("maxdiff", "Maxdiff:", self.onMaxdiff, str(self.hdr_config.GetCheckers()[0].maxdiff)))

    def setConfig(self, hdr_config, path):
        self.hdr_config = copy.deepcopy(hdr_config)
        self.path = path
        for w, l, h, value in self.inputFieldData():
            getattr(self, w).SetValue(value)

    def createInputField(self, parent, label, handler, defValue= u''):
        cimke = wx.StaticText(parent, -1, label)
        input_field = wx.TextCtrl(parent, -1, defValue, style=wx.TE_LEFT | wx.TE_PROCESS_ENTER)
        
        input_field.Bind(wx.EVT_TEXT, handler)
        
        hs = wx.BoxSizer(wx.HORIZONTAL)
        
        hs.Add(cimke, 1, wx.ALIGN_LEFT)
        hs.Add(input_field, 2, wx.ALIGN_CENTER)
        return (input_field, hs)

    def InitUI(self):
        
        sb = wx.StaticBox(self, label='HDR config')
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)
        
        for widget, cimke, handler, default_value in self.inputFieldData():
            input_field, hs = self.createInputField(self, cimke, handler, defValue = default_value)
            sbs.Add(hs, 0, wx.EXPAND)
            setattr(self, widget, input_field)
            
        self.SetSizer(sbs)
                
    def updateHDRConfig(self):
        pass

    def onTargetDir(self, evt):
        value = self.targetDir.GetValue()
        self.hdr_config.SetTargetDir(value)
                
    def onRawExtension(self, evt):
        value = self.rawExt.GetValue()
        self.hdr_config.SetRawExt(value)
    
    def onImageExt(self,evt):
        value = self.imageExt.GetValue()
        self.hdr_config.SetImageExt(value)
    
    def onPrefix(self,evt):
        value = self.prefix.GetValue()
        self.hdr_config.SetPrefix(value)
        
    def onMaxdiff(self, evt):
        value = int(self.maxdiff.GetValue())
        self.hdr_config.GetCheckers()[0].maxdiff = value
        print 'onMaxdiff'


class HDRConfigDialog(wx.Dialog):
    def __init__(self, *args, **kw):
        self.hdr_config = kw['hdr_config']
        del kw['hdr_config']
        super(HDRConfigDialog, self).__init__(*args, **kw)
        
        hdr_config_work = copy.deepcopy(self.hdr_config)
        self.panel = HDRConfigPanel(parent = self, hdr_config = hdr_config_work)
        self.InitUI(self.panel)

    def InitUI(self, panel):
        
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, label='Ok')
        cancelButton = wx.Button(self, label='Cancel')
        hbox2.Add(okButton)
        hbox2.Add(cancelButton, flag=wx.LEFT, border=5)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(panel, proportion=1, 
                 flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(hbox2, 
                 flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        self.SetSizer(vbox)
        
        okButton.Bind(wx.EVT_BUTTON, self.onOk)
        cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)
            
    def onOk(self,evt):
        self.hdr_config.SetTargetDir(self.panel.targetDir.GetValue())
        self.hdr_config.SetRawExt(self.panel.rawExt.GetValue())
        self.hdr_config.SetImageExt(self.panel.imageExt.GetValue())
        self.hdr_config.SetPrefix(self.panel.prefix.GetValue())
        
        self.onCancel(evt)
                
    def onCancel(self, evt):
        self.Destroy()


class Command:
    def __init__(self):
        self._want_abort = 0
        
    def abort(self):    
        self._want_abort = 1
        
    def abortWanted(self):
        return self._want_abort != 0
    
    def __call__(self):
        print "Command object default operation: sleep for 5 sec"
        time.sleep(5)
        

class SeqParserCommand(Command):
    def __init__(self, path):
        Command.__init__(self)
        self.path = path
        
    def __call__(self):
        hdr_config = seq_config_dict[self.path]
        try: 
            hdrs, single_images = CompositeImage.CollectSeqStrategy().parseDir(self.path, hdr_config)
            # TODO: Még a HDR-eket nem vizsgálja
            panos, single_images = CompositeImage.CollectSeqStrategy().parseIMGList(single_images, CompositeImage.PanoWeakConfig(hdr_config.GetTargetDir(), 25))
            return (hdrs, panos, single_images)
        except IOError:  # handling the case when there are no raw files
            print "No RAW input to parse in %s" % self.path    


class SeqGenCommand(Command):
    def __init__(self, seq, target_path, gen):
        Command.__init__(self)
        self.seq = seq
        self.gen = gen
        self.target_path = target_path
        
    def __call__(self):
        config = seq_config_dict[self.target_path]
        return self.gen(self.seq, config)


wxEVT_COMMAND_UPDATE = wx.NewEventType()
EVT_COMMAND_UPDATE = wx.PyEventBinder(wxEVT_COMMAND_UPDATE, 1)


class CommandUpdate(wx.PyCommandEvent):
    def __init__(self, callback):
        super(CommandUpdate, self).__init__(wxEVT_COMMAND_UPDATE, 0)
        # Attributes
        self.value = None
        self.callback = callback
        self.result = 'Failed'
        self.task_id = None
        
    def SetValue(self, value):
        self.value = value
        
    def GetValue(self):
        return self.value

    def SetTaskID(self, task_id):
        self.task_id = task_id
        
    def GetTaskID(self):
        return self.task_id

    def SetThreadID(self, th_id):
        self.th_id = th_id
        
    def GetThreadID(self):
        return self.th_id


class WorkerThread(TH.Thread):
    """Worker Thread Class."""
    def __init__(self, cmd, task_id, notify_window, callback):
        """Init Worker Thread Class."""
        TH.Thread.__init__(self)
        self._cmd = cmd
        self.task_id = task_id
        self._notify_window = notify_window
        self.callback = callback
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):
        """Run Worker Thread."""
        event = CommandUpdate(self.callback)
        result = self._cmd()
        if result != None:
            event.result = 'Ok'
        event.SetValue(result)
        event.SetTaskID(self.task_id)
        event.SetThreadID(self)
        wx.PostEvent(self._notify_window, event)
        
    def abort(self):
        self._cmd.abort()


class ExpanderPopup(wx.Menu):
    def __init__(self):
        wx.Menu.__init__(self)

    def AddItem(self, label, callback):
        item = wx.MenuItem(self, wx.NewId(), label)
        self.AppendItem(item)
        self.Bind(wx.EVT_MENU, callback, item)
        return item
    
    def AddMenuItems(self, items):
        for l, c in items: 
            self.AddItem(l, c)    

    
class Expander(object):
    # TODO: menu item kezelés az ImageSequenceExpanderPopup-ból.
    def __init__(self, tree, itemID):
        
        self.tree = tree
        self.itemID = itemID
        self.tree.SetPyData(itemID, self)
        
    def isExpanded(self):
        raise NotImplementedError
                            
    def expand(self, *arsg, **kwargs):
        pass
        #raise NotImplementedError
    
    def GetPopupMenu(self, *args, **kwargs):
        raise NotImplementedError
    
    # TODO: megfontolandó, hogy ez különálló függvény legyen - e egy plusz tree paraméterrel

    def handleClick(self):
        raise NotImplementedError
    
    def itemHasChildOfType(self, item, t):
        (child, cookie) = self.tree.GetFirstChild(item)
        while child.IsOk():
            pydata = self.tree.GetPyData(child)
            if isinstance(pydata, t):
                return pydata
            (child, cookie) = self.tree.GetNextChild(self.itemID, cookie)
        
        return None
    
    def hasChildWithType(self, t):
        """ Checks if a child with the given type 't' exists"""
        return self.itemHasChildOfType(self.itemID, t)
    
    # TODO: megfontolandó, hogy ez különálló függvény legyen - e egy plusz tree paraméterrel

    def findType(self, item, t):
        if item.IsOk():
            pt = self.itemHasChildOfType(item, t)
            if pt == None:
                return self.findType(self.tree.GetItemParent(item), t)
            return pt
        else:
            return None
        
    def findTypeAbove(self, t):
        """Checks if a child in higher level in the tree of type 't' exists"""
        p = self.tree.GetItemParent(self.itemID)
        return self.findType(p, t)
        
    def executeGen(self, dummyarg):
        pass

    def getPath(self):
        return self.path
    
    def ConfigKey(self):
        raise NotImplementedError

        
class DirectoryExpanderPopup(ExpanderPopup):
    def __init__(self, d_expander):
        ExpanderPopup.__init__(self)
        self.dir_expander = d_expander
        
        menu_items = [("HDR config", self.onHDRConf),
                      ("Panorama config", self.onPanoramaConf),
                      ("Symlinks", self.onSymlinks),
                      ("Generate recursively", self.onGen)]
        
        self.AddMenuItems(menu_items)
        
    def onHDRConf(self, evt):
        print evt, type(evt)
        raise NotImplementedError  
        
    def onPanoramaConf(self, evt):
        raise NotImplementedError

    def onSymlinks(self, evt):
        self.dir_expander.genSymlink()
        
    def onGen(self,evt):
        self.dir_expander.generate()


def GlobStarFilter(path):
    return [os.path.basename(d) for d in glob.glob(os.path.join(path, '*'))]


class DirectoryExpander(Expander):
    def __init__(self, tree, path, itemID):
        #FIXME: turn it to assert
        if not os.path.isdir(path):
            raise OSError(errno.ENOENT, os.strerror(errno.ENOENT))
        self.path = path
        
        tree.SetItemHasChildren(itemID)
        self.expanded = False
        Expander.__init__(self,tree, itemID)
        
    def isExpanded(self):
        return self.expanded
 
    def addSubdirsToTree(self, l):
        for fn in sorted(l):
            fullpath = os.path.join(self.path, fn)
            if os.path.isdir(fullpath):
                child = self.tree.AppendItem(self.itemID, fn)
                DirectoryExpander(self.tree, fullpath, child)
                      

    def UpdateItemText(self, text):
        item_text = self.tree.GetItemText(self.itemID)
        item_text = item_text + text
        self.tree.SetItemText(self.itemID, item_text)


    def AddSeqsItems(self, seqs, seq_config, seq_expander_cls):
        if len(seqs) == 0:
            return
        # Itt kihasznaljuk, hogy az osszes seq egy konyvtarbol van.
        prefix = seq_config.ExpandPrefix(seqs[0].getFilelist()[0])
        seq_path = seq_config.GetTargetDir()
        for fn, seq in enumerate(reversed(seqs)):
            actual_prefix = prefix + "_%d" % fn #seq_config.GetIndex()
            target_path = os.path.join(seq_path, actual_prefix)
            child = self.tree.AppendItem(self.itemID, target_path)
            seq_expander = seq_expander_cls(self.tree, self.path, target_path, child, seq)
            seq_config_per_image = copy.deepcopy(seq_config)
            seq_config_per_image.SetPrefix(actual_prefix)
            seq_config_dict[seq_expander.ConfigKey()] = seq_config_per_image

    def SeqParsedCallback(self, (hdrs, panos, single_images)):
        self.tree.clearState(self.itemID)
        
        n_hdrs = len(hdrs)
        
        n_panos = len(panos)
         
        text = "(%d hdrs, %d panos)" % (n_hdrs, n_panos)
        self.UpdateItemText(text)
        
        #if n_hdrs == 0:
        #    return
        
        hdr_config = seq_config_dict[self.path]
        
        self.AddSeqsItems(hdrs, hdr_config, HDRExpander)
        pano_config = copy.deepcopy(hdr_config)
        pano_config.SetPrefix("PANO")
        pano_config.ResetIndex()
        self.AddSeqsItems(panos, pano_config, PanoExpander)

    def expand(self, filter=GlobStarFilter):

        if self.isExpanded():   
            return
        
        self.task_id = self.tree.processingStarted(self.itemID)
        
        l = filter(self.path)
        self.addSubdirsToTree(l)
        cmd = SeqParserCommand(self.path)
        WorkerThread(cmd, self.task_id, self.tree, self.SeqParsedCallback)        
        self.expanded = True
        return self.task_id
 
    def GetPopupMenu(self):
        return DirectoryExpanderPopup(self)

    def ConfigKey(self):
        return self.path
    
    def handleClick(self):
        pass

    def executeGen(self,gen):
        return self.expand(gen=None)

    def genSymlink(self):
        self.tree.executeGen(CompositeImage.SymlinkGenerator(), self.itemID)

    def generate(self):
        self.tree.executeGen(None, self.itemID)
        

class RootItemExpanderPopup(DirectoryExpanderPopup):
    def __init__(self, d_expander):
        DirectoryExpanderPopup.__init__(self, d_expander)
        
        root_menu_items = [("Change root", self.onChangeRoot)]
        
        self.AddMenuItems(root_menu_items)
    
    def onChangeRoot(self, evt):
        dlg = wx.DirDialog(parent=None)
        if wx.ID_OK == dlg.ShowModal():
            path = dlg.GetPath()
            tree = self.dir_expander.tree
            tree.DeleteAllItems()
            RootItemExpander(tree, path)
        dlg.Destroy()
        return None
        

class RootItemExpander(DirectoryExpander):
    def __init__(self, tree	, path):
        itemID = tree.AddRoot(path)
        DirectoryExpander.__init__(self, tree, path, itemID)
        
    def GetPopupMenu(self):
        return RootItemExpanderPopup(self)


class ImageExpander(Expander):
    def __init__(self, tree, itemID, image):
        Expander.__init__(self,tree, itemID)
        self.image = image


class ImageSequenceExpanderPopup(ExpanderPopup):
    
    #TODO: Megnézni, hogy nem elég-e az expander.executeGen függvényt átadni paraméterként.
    def __init__(self, expander):
        wx.Menu.__init__(self)
        self.expander = expander
        menu_items = [("Generate", self.onGenerate),
                      ("Symlinks", self.onCreateSymlink)]
        self.AddMenuItems(menu_items)
   
    def onGenerate(self, evt):
        self.expander.executeGen(gen=None)
        
    def onCreateSymlink(self,evt):
        self.expander.executeGen(CompositeImage.SymlinkGenerator())
                      

class ImageSequenceExpander(Expander):
    def __init__(self, tree, source_path, target_path, itemID, img_seq):
        Expander.__init__(self, tree, itemID)
        self.target_path = target_path
        self.source_path = source_path
        self.seq = img_seq
        if len(self.seq) > 0:
            tree.SetItemHasChildren(itemID)
            
        self.expanded = False
     
    def isExpanded(self):
        return self.expanded
    
    def expand(self, filter=None):
        # TODO: Minden egyes alkalommal újra kell számolni
        if self.isExpanded():
            return
        for img in sorted(self.seq):
            child = self.tree.AppendItem(self.itemID, os.path.basename(img))
            ImageExpander(self.tree, child, self.seq[img])
        self.expanded = True

    def handleClick(self):
        pass
        
    def GetPopupMenu(self):
        return ImageSequenceExpanderPopup(self)

    def ExecuteGenCallback(self, result):
        pass
    
    def _execCmd(self, gen):
        cmd = SeqGenCommand(self.seq, self.target_path, gen)
        task_id = self.tree.processingStarted(self.itemID)
        WorkerThread(cmd, task_id, self.tree, None)
        return task_id

    def _ConfigKey(self, s):
        if self.target_path[0] == '/': # os.path.join discards anything if an absolute path appears in the parameter list
            target_path_start = 1
        else:
            target_path_start = 0
        return os.path.join(self.source_path, s, self.target_path[target_path_start:])
    
    def ConfigKey(self):
        raise NotImplementedError
    
    
class HDRExpander(ImageSequenceExpander):
    def executeGen(self, gen):
        if gen == None:
            gen = CompositeImage.HDRGenerator()
            
        task_id = self.__execCmd(gen)
        return task_id

    def ConfigKey(self):
        return self._ConfigKey('HDR')


class PanoExpander(ImageSequenceExpander):
    def executeGen(self, gen):
        print "PanoExpander", type(self)
        if gen == None:
            gen = CompositeImage.PanoGenerator()
            
        task_id = self._execCmd( gen)
        return task_id

    def ConfigKey(self):
        return self._ConfigKey('PANO')
    
    
class TreeDict:
    """ A dictionary which assumes keys are directory paths. It looks up elements with key up in the path"""
    def __init__(self):
        self.d = {}
                
    def __getitem__(self, key):
        k = os.path.abspath(key)
        if not k in self:
            d = os.path.dirname(k)
            if d == k:
                raise KeyError
            return self.__getitem__(d)
        
        return self.d[k]

    def __setitem__(self, key, value):
        key = os.path.abspath(key)
        self.d[key] = value

    def __delitem__(self, key):
        key = os.path.abspath(key)
        del self.d[key]
                
    def __len__(self):
        return len(self.d)


    def __contains__(self, key):
        return key in self.d.keys()

    def keys(self):
        return self.d.keys()
     

class TreeCtrlWithImages(wx.TreeCtrl):
    def __init__(self, *args, **kwrds):
        
        wx.TreeCtrl.__init__(self, *args, **kwrds)
        # bitmaps for progress indication.
        self.il = wx.ImageList(16,16)
        self.AssignImageList(self.il)
        self.img_null = self.il.Add(wx.NullBitmap)
        self.imgs_wip = [self.il.Add(wx.Bitmap(fn)) for fn in sorted(glob.glob('roller_16-?.png'))]
        self.img_ready = self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK, wx.ART_OTHER, (16,16)))
        self.img_aborted = self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_ERROR, wx.ART_OTHER, (16,16)))
        
        # Init for process accounting
        self.processedItems = {}
        self.process_idx = 0
        
        # Init for progress animation
        self.progressImageIndex = 0
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.updateProgress, self.timer)
        self.iterator = None
        self._cancel_wanted = False

    def processingStarted(self, item):
        if item in self.processedItems:
            raise TypeError # TODO ehelyett value error kellene
        self.process_idx = self.process_idx + 1
        self.processedItems[self.process_idx] = item
        self.SetItemImage(item, self.imgs_wip[0],wx.TreeItemIcon_Normal)
        self.timer.Start(100) #in milliseconds
        return self.process_idx
        
    def updateProgress(self,e):
        self.progressImageIndex = (self.progressImageIndex + 1) % len(self.imgs_wip)
        for k in self.processedItems.keys():
            item = self.processedItems[k]
            self.SetItemImage(item, self.imgs_wip[self.progressImageIndex], wx.TreeItemIcon_Normal)
            
    def processingCompleted(self, task_id):
        self.SetItemImage(self.processedItems[task_id], self.img_ready,wx.TreeItemIcon_Normal)
        del self.processedItems[task_id]
        if self.isItemProcessed():
            return
        self.timer.Stop()
        
    def isItemProcessed(self):
        return not len(self.processedItems) == 0
        
    def processingFailed(self, task_id):
        item = self.processedItems[task_id]
        self.SetItemImage(item, self.img_aborted,wx.TreeItemIcon_Normal)
        del self.processedItems[task_id]
        if not self.isItemProcessed():
            self.timer.Stop()
        
    def clearState(self, item):
        self.SetItemImage(item, self.img_null, wx.TreeItemIcon_Normal)

    def executeGen(self, gen, itemID):
        if self.iterator:
            msg = wx.MessageBox(message='One command is already being executed')
            return
        self.iterator = treeIterator(self, itemID)
        self._cancel_wanted = False
        self.gen = gen
        self.executeNext()

    def executeNext(self):
        if self._cancel_wanted:
            return
        try:
            while TH.activeCount() < 4:
                task_id = None 
                while task_id == None:
                    item = self.iterator.next()
                    expander = self.GetPyData(item)
                    task_id = expander.executeGen(self.gen)
                    print TH.activeCount()
        except StopIteration:
            self.iterator = None
            pass # normal termination of iteration using generator
        
    def StopCommand(self):
        self._cancel_wanted=True
        self.iterator = None


class TreeCtrlFrame(wx.Frame):
    
    def __init__(self, parent, id, title, rootdir):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(450, 350))
        panel = wx.Panel(self, -1)
        self.tree = TreeCtrlWithImages(panel, 1, wx.DefaultPosition, (-1,-1), wx.TR_HAS_BUTTONS)
        
        self.config_key = rootdir
        expander = RootItemExpander(self.tree, rootdir)
        
        self.updatebutton = wx.Button(self, id=wx.ID_REFRESH)
        self.updatebutton.Bind(wx.EVT_BUTTON, self.onUpdate)
        savebutton = wx.Button(self, id=wx.ID_SAVE)
        savebutton.Bind(wx.EVT_BUTTON, self.onSave)
        loadbutton = wx.Button(self, id=wx.ID_OPEN)
        loadbutton.Bind(wx.EVT_BUTTON, self.onLoad)
        self.stopbutton = wx.Button(self, id=wx.ID_STOP)
        self.stopbutton.Bind(wx.EVT_BUTTON, self.onStopCommand)
        self.stopbutton.Disable()
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.updatebutton, 0, wx.EXPAND)
        button_sizer.Add(savebutton, 0, wx.EXPAND)
        button_sizer.Add(loadbutton, 0, wx.EXPAND)
        button_sizer.Add(self.stopbutton, 0, wx.EXPAND)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tree, 1, wx.EXPAND)
        
        panel.SetSizer(sizer)
        
        seq_config_dict[rootdir] = CompositeImage.HDRConfig('/tmp')
        self.hdrconfig_panel = HDRConfigPanel(hdr_config=seq_config_dict[rootdir],
                                              path=rootdir,
                                              parent=self)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(panel, 1, wx.EXPAND)
        hsizer.Add(self.hdrconfig_panel, 1, wx.EXPAND)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(hsizer, 1, wx.EXPAND)
        vsizer.Add(button_sizer, 0, wx.EXPAND)
        self.SetSizer(vsizer)
        #sizer.Fit(self)
        self.Layout()
        
        self.tree.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.onItemExpand, id=1)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.onRightClick, self.tree)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onClickItem, self.tree)
        
        self.Bind(EVT_COMMAND_UPDATE, self.onCommandUpdate)
                    
    def onItemExpand(self, e):

        item = e.GetItem()
        data = self.tree.GetPyData(item)
        if not data.isExpanded():
            data.expand()
        

    def _updateHDRConfigPanel(self):
        hdr_config = seq_config_dict[self.config_key]
        self.hdrconfig_panel.setConfig(hdr_config, self.config_key)

    def onClickItem(self, e):
        item = e.GetItem()
        data = self.tree.GetPyData(item)
        data.handleClick()
        self.config_key = data.ConfigKey()
        self._updateHDRConfigPanel()
                
    def onRightClick(self, e):
        item = e.GetItem()
        data = self.tree.GetPyData(item)
        self.PopupMenu(data.GetPopupMenu(), e.GetPoint())

    def onUpdate(self, e):
        seq_config_dict[self.config_key] = self.hdrconfig_panel.hdr_config

    def onCommandUpdate(self, e):
        
        v = e.GetValue()
        thread = e.GetThreadID()
        thread.join() #Ettl lehet, hogy belassul a GUI.
        task_id = e.GetTaskID()
        if e.result == 'Failed':
            self.tree.processingFailed(task_id)
        else:
            self.tree.processingCompleted(task_id)
            if e.callback:
                e.callback(v)
        
        if self.tree.iterator:
            self.stopbutton.Enable()
            self.tree.executeNext()

    def onStopCommand(self, e):
        self.tree.StopCommand()
        self.stopbutton.Disable()
        

    def ShowCustomDialog(self, fd_style):
        dlg = wx.FileDialog(self, "Choose a file", style=fd_style)
        if wx.ID_OK == dlg.ShowModal():
            return dlg.GetPath()
        dlg.Destroy()
        return None

    def onSave(self, e):
        fn = self.ShowCustomDialog(wx.FD_SAVE)
        if fn:
            fout=open(fn, 'w')
            fout.write(pickle.dumps(seq_config_dict))
            fout.close()
    
    def onLoad(self, e):
        fn = self.ShowCustomDialog(wx.FD_OPEN)
        if fn:
            global seq_config_dict
            f=open(fn, "r")
            seq_config_dict=pickle.loads(f.read())
            f.close()
            self._updateHDRConfigPanel()

    
def treeIterator(tree, item):
    yield item
    child, cookie = tree.GetFirstChild(item)
    while child.IsOk():
        for c in treeIterator(tree, child):
            yield c
        child, cookie = tree.GetNextChild(item, cookie)


class TestExpandersApp(wx.App):
    def OnInit(self):


        frame = TreeCtrlFrame(None, -1, 'Test expanders', '/')


        frame.Show(True)
        self.SetTopWindow(frame)
        return True


seq_config_dict = TreeDict()


if __name__ == "__main__":
    app = TestExpandersApp()
    app.MainLoop()
    print "Finished. # running threads=%d" % TH.active_count()
