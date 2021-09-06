from PIL import Image,ImageFilter
import importlib.util as import_utils
import random
import numpy as np
import unittest

spec = import_utils.spec_from_file_location("utils", "dfstego/utilities/myutils.py")
utils = import_utils.module_from_spec(spec)
spec.loader.exec_module(utils)
myconstants = utils.import_module("myconstants", "dfstego/utilities/myconstants.py")


class MethodLSBChangeBitTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('In setUpClass() MethodLSBChangeBitTest')
        cls.elias = utils.import_module("elias", "dfstego/methods/methodLSB.py")

    @classmethod
    def tearDownClass(cls):
        print('In tearDownClass() MethodLSBChangeBitTest')
        del cls.elias
    

    def setUp(self):
        super().setUp()           
        self.pix = np.zeros((2,2,3),np.uint8)
        for x in range(1):
            for y in range(1):
                self.pix[x,y] = [121,120,123] 
       

    def tearDown(self):
        del self.pix
        super().tearDown()


    def test_change_bit_element_one_pixel_odd(self):
        pix_aux = self.pix[0,0][2]
        self.elias.change_bit(self.pix,0,0,2,'1')
        self.assertEqual(self.pix[0,0][2],pix_aux)


    def test_change_bit_element_one_pixel_pair(self):
        pix_aux =  self.pix[0,0][1]
        self.elias.change_bit(self.pix,0,0,1,'1')
        self.assertNotEqual( self.pix[0,0][1],pix_aux)


    def test_change_bit_element_zero_pixel_pair(self):
        pix_aux = self.pix[0,0][1]
        self.elias.change_bit(self.pix,0,0,1,'0')
        self.assertEqual(self.pix[0,0][1],pix_aux)


    def test_change_bit_element_zero_pixel_odd(self):
        pix_aux = self.pix[0,0][2]
        self.elias.change_bit(self.pix,0,0,2,'0')
        self.assertNotEqual(self.pix[0,0][2],pix_aux)


if __name__ == '__main__':
    unittest.main()

