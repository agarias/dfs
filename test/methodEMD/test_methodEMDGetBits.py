from PIL import Image,ImageFilter
import importlib.util as import_utils
import random
import numpy as np
import unittest

spec = import_utils.spec_from_file_location("utils", "dfstego/utilities/myutils.py")
utils = import_utils.module_from_spec(spec)
spec.loader.exec_module(utils)
myconstants = utils.import_module("myconstants", "dfstego/utilities/myconstants.py")


class MethodEMDGetbitsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('In setUpClass() MethodEMDGetbits')
        cls.emd = utils.import_module("emd", "dfstego/methods/methodEMD.py")

    @classmethod
    def tearDownClass(cls):
        print('In tearDownClass() MethodEMDGetbits')
        del cls.emd
    

    def setUp(self):
        super().setUp()           
        self.pix = np.zeros((4,4,3),np.uint8)
        self.pix[0,0] = [152,22,122]
        self.pix[0,1] = [153,23,122]
        self.pix[1,0] = [154,24,122]
        self.pix[1,1] = [155,25,122]
        self.pix[0,2] = [152,22,122]
        self.pix[0,3] = [153,23,122]
        self.pix[1,2] = [154,25,123]
        self.pix[1,3] = [155,24,123] 
        

    def tearDown(self):
        del self.pix
        super().tearDown()


    def test_get_bits_pixel_two_bits(self):
        output='0b'
        resultCorrect ='0b01'
        result = self.emd.get_bits_pixel(self.pix,0,1,output,True)
        self.assertTrue(result[0])
        self.assertEqual(result[1],resultCorrect)


    def test_get_bits_pixel_one_bit(self):
        output='0b'
        resultCorrect ='0b0'
        result = self.emd.get_bits_pixel(self.pix,1,2,output,True)
        self.assertFalse(result[0])
        self.assertEqual(result[1],resultCorrect)


    def test_get_bits_pixel_no_bits(self):
        output='0b'
        result = self.emd.get_bits_pixel(self.pix,1,3,output,True)
        self.assertFalse(result[0])
        self.assertEqual(result[1],output)


    def test_get_bits_block_all_pixels_and_continue(self):
        output='0b'
        resultCorrect ='0b011011'
        result = self.emd.get_bits_block(self.pix,0,0,output,True)
        self.assertTrue(result[0])
        self.assertEqual(result[1],resultCorrect)


    def test_get_bits_block_all_pixels_and_not_continue(self):
        self.pix[1,2] = [154,24,122]
        self.pix[1,3] = [155,25,123] 
        output='0b'
        resultCorrect ='0b01101'
        result = self.emd.get_bits_block(self.pix,0,2,output,True)
        self.assertFalse(result[0])
        self.assertEqual(result[1],resultCorrect)

    def test_get_bits_block_not_all_pixels_and_not_continue(self):
        output='0b'
        resultCorrect ='0b010'
        result = self.emd.get_bits_block(self.pix,0,2,output,True)
        self.assertFalse(result[0])
        self.assertEqual(result[1],resultCorrect)

    def test_get_message_emd_correct(self):
        output='0b'
        resultCorrect ='0b011011010'
        result = self.emd.get_message_emb(self.pix,4,4,output)
        self.assertEqual(result,resultCorrect)


    def test_get_message_emd_no_message(self):
        self.pix[0,0] = [153,22,122]
        output='0b'
        result = self.emd.get_message_emb(self.pix,4,4,output)
        self.assertEqual(result,output)


if __name__ == '__main__':
    unittest.main()


