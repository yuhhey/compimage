#-*- coding: utf-8 -*-

import TreeBuilder
import unittest
import mock
import os


class TreeBuildTest(unittest.TestCase):
    
    def countSubdirs(self, path):
        """Counts the amount of subdirs in 'path'""" 
        count = 0
        for i in os.listdir(path):
            if os.path.isdir(os.path.join(path,i)):
                count = count + 1
                
        return count
        
    
    def test_directory(self):
        directory = '/storage'
        
        treectrl = mock.MagicMock()
        
        tb = TreeBuilder.DirectoryExpander(treectrl, directory)
        
        treectrl.AddRoot.assert_any_call(directory)
        self.assertTrue(treectrl.SetPyData.called, "SetPyData not called")
        
        tb.expand()
        #treectrl.AppendItem.call_args()
        
        self.assertTrue(treectrl.AppendItem.called, "AppendItem not called")
        
        cc = treectrl.AppendItem.call_count
        exp_cc = self.countSubdirs(directory)
        self.assertEqual(cc, exp_cc, "AppendItem call count is %d instead of %d" % (cc, exp_cc))
        
        
        # Expand added all the subdirs again and again during subsequent expand operations.
        tb.expand()
        
        cc = treectrl.AppendItem.call_count
        self.assertEqual(cc, exp_cc, "AppendItem call count is %d instead of %d" % (cc, exp_cc))
        
    
    def test_HDRconfig(self):
        hdr_conf_param = {'prefix': 'hdr',
                          'ext': 'CR2',
                          'target_dir': '/tmp'}
        import sys
        module = sys.modules[__name__]
        for name, value in hdr_conf_param.iteritems():
            setattr(module, name, value)
            
        hdr_gen = mock.MagicMock(_target_dir=target_dir,_prefix=prefix,_ext=ext) # HDRGenerator object
        treectrl = mock.MagicMock()
        itemID = mock.MagicMock()
        
        hdrcb = TreeBuilder.HDRConfigExpander(treectrl, itemID, hdr_gen)
            
        hdrcb.expand()
        
        cc = treectrl.AppendItem.call_count
        self.assertTrue(cc > 0, 'HDR config expander shall add branch and leaves to the treectrl')
        
        call_args = treectrl.AppendItem.call_args_list
        print call_args
        
        self.assertEqual(call_args[0], ((itemID, 'HDR sequence parameters'),))
        for i in range(1,4):
            args, kwargs = call_args[i]
            print args, hdr_conf_param.keys()
            self.assertEqual(args[1], hdr_conf_param[hdr_conf_param.keys()[i-1]])
            
        self.assertEqual(call_args[1][0][1], prefix)
        

class TreeDictTest(unittest.TestCase):
    
    
    def __init__(self, *args, **kwrds):
        
        super(TreeDictTest, self).__init__(*args, **kwrds)
        self.d = {'/': 1,
                  '/home/grof':2,
                  '/usr/local/bin':3}
        
        self.test_keys = {'/bin/': self.d['/'],
                          '/home': self.d['/'],
                          '/home/grof/src': self.d['/home/grof'],
                          '/usr/local': self.d['/']}
    
    def checkResult(self, CUT, d):
        for k in d.keys():
            er = d[k]
            r = CUT[k]
            self.assertEqual(er, r, 'er=%s, r=%s' % (k, str(d[k])))
    
    def test_lookup(self):
        
        
        CUT = TreeBuilder.TreeDict()
        for k in self.d.keys():
            CUT[k] = self.d[k]
        self.checkResult(CUT, self.d)
            

        self.checkResult(CUT, self.test_keys)
        
        # Check the case when there is no entry for root neither for the index
        del CUT['/']
        self.assertRaises(KeyError, CUT.__getitem__, '/pisti')
        