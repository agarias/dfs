from PIL import Image,ImageFilter
import importlib.util as import_utils
import random
import numpy as np
import unittest

spec = import_utils.spec_from_file_location("utils", "dfstego/utilities/myutils.py")
utils = import_utils.module_from_spec(spec)
spec.loader.exec_module(utils)
myconstants = utils.import_module("myconstants", "dfstego/utilities/myconstants.py")

 
class MethodEMDTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('In setUpClass() MethodEMD')
        cls.emd = utils.import_module("emd", "dfstego/methods/methodEMD.py")

    @classmethod
    def tearDownClass(cls):
        print('In tearDownClass() MethodEMD')
        del cls.emd
    

    def setUp(self):
        super().setUp()           
        self.pix = np.zeros((4,4,3),np.uint8)
        self.pix[0,0] = [152,22,122]
        self.pix[0,1] = [153,23,123]
        self.pix[1,0] = [154,24,122]
        self.pix[1,1] = [155,25,123]
        self.pix[0,2] = [152,22,122]
        self.pix[0,3] = [153,23,123]
        self.pix[1,2] = [154,24,122]
        self.pix[1,3] = [155,25,123]
        self.data = [1,1,1,0,0,1,0,0,1] 
       

    def tearDown(self):
        del self.pix
        del self.data
        super().tearDown()


    def test_change_block_all_pixel_code(self):
        values_corrects_red = [[152,159],[158,149]]
        value_correct_blue= 122 
        pointer_aux = 0
        pointer = self.emd.change_block(self.pix,0,0,self.data,pointer_aux)
        self.assertEqual(pointer,pointer_aux +6) 
        for i in range(2):
            for j in range(2):                       
                self.assertEqual(self.pix[i,j][0],values_corrects_red[i][j])
                self.assertEqual(self.pix[i,j][2],value_correct_blue)
 
    def test_change_block_not_all_pixel_code(self):
        values_corrects_red = [[152,158],[149,155]]
        values_corrects_blue= [[122,122],[122,123]] 
        values_corrects_green= [[22,23],[24,24]] 
        pointer_aux = 5
        pointer = self.emd.change_block(self.pix,0,0,self.data,pointer_aux)
        self.assertEqual(pointer,pointer_aux +6) 
        for i in range(2):
            for j in range(2):                       
                self.assertEqual(self.pix[i,j][0],values_corrects_red[i][j])
                self.assertEqual(self.pix[i,j][1],values_corrects_green[i][j])
                self.assertEqual(self.pix[i,j][2],values_corrects_blue[i][j])  


    def test_transform_image_message_correct(self):
        values_corrects_red = [[152,159,152,148],[158,149,155,155]]
        values_corrects_blue= [[122,122,122,122],[122,122,123,123]] 
        values_corrects_green= [[22,23,22,23],[24,25,25,24]] 
        result = self.emd.transform_image(self.pix,self.data,4,4)
        self.assertEqual(result,1)
        for i in range(2):
            for j in range(4):                      
                self.assertEqual(self.pix[i,j][0],values_corrects_red[i][j])
                self.assertEqual(self.pix[i,j][1],values_corrects_green[i][j])
                self.assertEqual(self.pix[i,j][2],values_corrects_blue[i][j])


    def test_transform_image_message_too_long(self):
        self.pix = np.zeros((2,2,3),np.uint8)
        result = self.emd.transform_image(self.pix,self.data,1,1)
        self.assertEqual(result,0) 
    

    def test_change_pixel_two_bits_all_options(self):
        self.pix[0,2] = [154,24,122]
        self.pix[0,3] = [155,25,123]
        values_corrects_red = [159,158,149,148]
        value_correct_blue= 122 
        pointer_aux = 0
        for i in range(4):
            with self.subTest("Message for this subtest",i=i):

                pointer = self.emd.change_pixel(self.pix,0,i,self.data,pointer_aux)        
                self.assertEqual(self.pix[0,i][0],values_corrects_red[i])
                self.assertEqual(self.pix[0,i][2],value_correct_blue)
                self.assertEqual(pointer,pointer_aux +2)
           
            pointer_aux = pointer    

    def test_change_pixel_two_bits_end_message(self):
        value_correct_red = 157
        value_correct_blue= 122 
        pointer_aux = 7
        pointer = self.emd.change_pixel(self.pix,0,0,self.data,pointer_aux)
        self.assertEqual(self.pix[0,0][0],value_correct_red)
        self.assertEqual(self.pix[0,0][2],value_correct_blue)
        self.assertEqual(pointer,pointer_aux +2)
    def test_change_pixel_one_bit_end_message(self):
        value_correct_red = 153
        value_correct_blue= 123
        value_correct_green= 23 
        pointer_aux = 8
        pointer = self.emd.change_pixel(self.pix,0,0,self.data,pointer_aux)
        self.assertEqual(self.pix[0,0][0],value_correct_red)
        self.assertEqual(self.pix[0,0][1],value_correct_green)
        self.assertEqual(self.pix[0,0][2],value_correct_blue)
        self.assertEqual(pointer,pointer_aux +2)


    def test_change_pixel_no_bit_end_message(self):
        value_correct_red = 152
        value_correct_blue= 123
        value_correct_green= 22 
        pointer_aux = 9
        pointer = self.emd.change_pixel(self.pix,0,0,self.data,pointer_aux)
        self.assertEqual(self.pix[0,0][0],value_correct_red)
        self.assertEqual(self.pix[0,0][1],value_correct_green)
        self.assertEqual(self.pix[0,0][2],value_correct_blue)
        self.assertEqual(pointer,pointer_aux +2)


    def test_change_source_no_change_red(self):
        value_correct_red = self.pix[0,0][0]
        pointer_aux = 0
        self.emd.change_source(self.pix,0,0,self.data,pointer_aux)
        self.assertEqual(self.pix[0,0][0],value_correct_red)


    def test_change_source_change_red(self):
        value_correct_red = 152
        pointer_aux = 0
        for i in range(4):
            with self.subTest("Message for this subtest",i=i):

                self.emd.change_source(self.pix,0,i,self.data,pointer_aux)        
                self.assertEqual(self.pix[0,i][0],value_correct_red)

if __name__ == '__main__':
    unittest.main()


