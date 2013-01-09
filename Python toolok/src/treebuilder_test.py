#-*- coding: utf-8 -*-

import TreeBuilder
import unittest
import mock

class TreeBuildTest(unittest.TestCase):
    
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
        
        self.assertEqual(cc, 17, "AppendItem call count is %d instead of 13" % cc)