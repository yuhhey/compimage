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