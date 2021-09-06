from PIL import Image,ImageFilter
import importlib.util as import_utils
import random
import numpy as np
import unittest

spec = import_utils.spec_from_file_location("utils", "dfstego/utilities/myutils.py")
utils = import_utils.module_from_spec(spec)
spec.loader.exec_module(utils)
myconstants = utils.import_module("myconstants", "dfstego/utilities/myconstants.py")


class MethodLSBDecodeEliasMessageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print('In setUpClass() MethodLSBDecodeEliasMessageTest')
        cls.elias = utils.import_module("elias", "dfstego/methods/methodLSB.py")


    @classmethod
    def tearDownClass(cls):
        print('In tearDownClass() MethodLSBDecodeEliasMessageTest')
        del cls.elias
    

    def setUp(self):
        super().setUp()
        self.pix = np.zeros((5,5,3),np.uint8)
       

    def tearDown(self):
        del self.pix
        super().tearDown()


    def test_decode_elias_message_matrix_code_message(self):
        check_result = 97
        size = 4*4*3
        maximun = 4-1 
        self.pix[0,0] = [120,122,124]
        self.pix[0,1] = [120,121,124] 
        self.pix[0,2] = [120,122,125]
        self.pix[0,3] = [121,122,124]
        self.pix[1,0] = [120,122,125]       
        self.assertEqual(self.elias.decode_elias_message(self.pix,maximun,size),check_result)


    def test_decode_elias_message_matrix_number_return_no_code(self):
        check_result = 0
        size = 4*4*3
        maximun = 4-1 
        self.pix[0,0] = [120,122,125]
        self.pix[0,1] = [120,122,125] 
        self.pix[0,2] = [120,122,125]
        self.pix[0,3] = [120,122,125]
        self.pix[1,0] = [120,122,125]       
        self.assertEqual(self.elias.decode_elias_message(self.pix,maximun,size),check_result)


    def test_decode_elias_message_matrix_no_code_message(self):
        check_result =-1
        size = 4*4*3
        maximun = 4-1 
        self.pix[0,0] = [121,122,123]
        self.pix[0,1] = [121,122,123] 
        self.pix[0,2] = [121,122,123]
        self.pix[0,3] = [121,122,123]
        self.pix[1,0] = [121,122,123]       
        self.assertEqual(self.elias.decode_elias_message(self.pix,maximun,size),check_result)

if __name__ == '__main__':
    unittest.main()

