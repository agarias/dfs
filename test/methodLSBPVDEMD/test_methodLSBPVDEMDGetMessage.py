from PIL import Image,ImageFilter
import importlib.util as import_utils
import random
import numpy as np
import unittest

spec = import_utils.spec_from_file_location("utils", "dfstego/utilities/myutils.py")
utils = import_utils.module_from_spec(spec)
spec.loader.exec_module(utils)
myconstants = utils.import_module("myconstants", "dfstego/utilities/myconstants.py")


class MethodLSBPVDEMDGetMessageTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('In setUpClass() MethodLSBPVDEMDGetMessage')
        cls.merge = utils.import_module("merge", "dfstego/methods/MethodLSBPVDEMD.py")

    @classmethod
    def tearDownClass(cls):
        print('In tearDownClass() MethodLSBPVDEMDGetMessage')
        del cls.merge
    

    def setUp(self):
        super().setUp()           
        self.pix = np.zeros((4,4,3),np.uint8)
        self.pix[0,0] = [103,26,122]
        self.pix[0,1] = [139,23,123]
        self.pix[1,0] = [142,24,123]
        self.pix[1,1] = [168,25,123]
        self.pix[0,2] = [152,27,122]
        self.pix[0,3] = [153,23,122]
        self.pix[1,2] = [154,25,122]
        self.pix[1,3] = [155,24,122] 
        self.pix[2,0] = [154,27,122]

    def tearDown(self):
        del self.pix
        super().tearDown()


    def test_get_message_correct(self):
        output='0b'
        resultCorrect ='0b1001110001011011'
        result = self.merge.get_message(self.pix,3,3,output)
        self.assertEqual(result,resultCorrect)


    def test_get_message_no_message(self):
        self.pix[0,0] = [154,22,122]
        output='0b'
        result = self.merge.get_message(self.pix,3,3,output)
        self.assertEqual(result,output)


if __name__ == '__main__':
    unittest.main()


