from PIL import Image,ImageFilter
import importlib.util as import_utils
import random
import numpy as np
import unittest

spec = import_utils.spec_from_file_location("utils", "dfstego/utilities/myutils.py")
utils = import_utils.module_from_spec(spec)
spec.loader.exec_module(utils)
myconstants = utils.import_module("myconstants", "dfstego/utilities/myconstants.py")

 
class MethodPVDTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('In setUpClass() MethodPVD')
        cls.pvd = utils.import_module("pvd", "dfstego/methods/methodPVD.py")

    @classmethod
    def tearDownClass(cls):
        print('In tearDownClass() MethodPVD')
        del cls.pvd
    

    def setUp(self):
        super().setUp()           
        self.pix = np.zeros((4,4,3),np.uint8)
        self.pix[0,0] = [152,22,122]
        self.pix[0,1] = [153,23,123]
        self.pix[1,0] = [154,24,122]
        self.pix[1,1] = [155,25,123]
        self.pix[0,2] = [153,22,122]
        self.pix[0,3] = [153,23,123]
        self.pix[1,2] = [154,24,122]
        self.pix[1,3] = [155,25,123]
        self.data = [1,1,1,0,0,1,0,0,1] 
       

    def tearDown(self):
        del self.pix
        del self.data
        super().tearDown()


    def test_change_block_all_pixel_code(self):
        values_corrects_red = [[153,146],[152,152]]
        values_corrects_blue= [[122,123],[123,123]]   
        pointer_aux = 0
        pointer = self.pvd.change_block(self.pix,0,0,self.data,pointer_aux)
        self.assertEqual(pointer,pointer_aux +9) 
        for i in range(2):
            for j in range(2):                       
                self.assertEqual(self.pix[i,j][0],values_corrects_red[i][j])
                self.assertEqual(self.pix[i,j][2],values_corrects_blue[i][j])
 
    def test_change_block_not_all_pixel_code(self):
        values_corrects_red = [[153,151],[153,155]]
        values_corrects_blue= [[122,123],[122,122]] 
        values_corrects_green= [[22,23],[26,24]] 
        pointer_aux = 4
        pointer = self.pvd.change_block(self.pix,0,0,self.data,pointer_aux)
        self.assertEqual(pointer,pointer_aux +5) 
        for i in range(2):
            for j in range(2):                       
                self.assertEqual(self.pix[i,j][0],values_corrects_red[i][j])
                self.assertEqual(self.pix[i,j][1],values_corrects_green[i][j])
                self.assertEqual(self.pix[i,j][2],values_corrects_blue[i][j])  


    def test_transform_image_message_correct(self):
        values_corrects_red = [[153,146,152,153],[152,152,154,155]]
        values_corrects_blue= [[122,123,122,123],[123,123,122,123]] 
        values_corrects_green= [[22,23,22,23],[24,25,24,25]] 
        result = self.pvd.transform_image(self.pix,self.data,3,3)
        self.assertEqual(result,1)
        for i in range(2):
            for j in range(4):                      
                self.assertEqual(self.pix[i,j][0],values_corrects_red[i][j])
                self.assertEqual(self.pix[i,j][1],values_corrects_green[i][j])
                self.assertEqual(self.pix[i,j][2],values_corrects_blue[i][j])


    def test_transform_image_message_too_long(self):
        self.data = [1,1,1,0,0,1,0,0,1,1,0,1,1,0,1,1,0] 
        self.pix = np.zeros((2,2,3),np.uint8)
        result = self.pvd.transform_image(self.pix,self.data,1,1)
        self.assertEqual(result,0) 


    def test_change_pixel_four_bits_all_options(self):

        values_corrects_red = [139,135]
        values_sources = [217,67]
        value_correct_blue= 123 
        pointer_aux = 0
        for i in range(2):
            with self.subTest("Message for this subtest",i=i):
                pointer = self.pvd.change_pixel(self.pix,0,i,values_sources[i],self.data,pointer_aux)        
                self.assertEqual(self.pix[0,i][0],values_corrects_red[i])
                self.assertEqual(self.pix[0,i][2],value_correct_blue)
                self.assertEqual(pointer,pointer_aux +4)
           
            pointer_aux = pointer    

    
    def test_change_pixel_three_bits_all_options(self):
        self.pix[0,0] = [96,22,122]
        values_corrects_red = [75,151]
        values_sources = [36,152]
        value_correct_blue= 123 
        pointer_aux = 0
        for i in range(2):
            with self.subTest("Message for this subtest",i=i):
                pointer = self.pvd.change_pixel(self.pix,0,i,values_sources[i],self.data,pointer_aux)        
                self.assertEqual(self.pix[0,i][0],values_corrects_red[i])
                self.assertEqual(self.pix[0,i][2],value_correct_blue)
                self.assertEqual(pointer,pointer_aux +3)
           
            pointer_aux = pointer


    def test_change_pixel_three_bits_end_message(self):
        value_correct_red = 65
        value_correct_blue= 122 
        value_correct_green= 23 
        value_source = 67
        pointer_aux = 6
        pointer = self.pvd.change_pixel(self.pix,0,0,value_source,self.data,pointer_aux)
        self.assertEqual(self.pix[0,0][0],value_correct_red)
        self.assertEqual(self.pix[0,0][1],value_correct_green)
        self.assertEqual(self.pix[0,0][2],value_correct_blue)
        self.assertEqual(pointer,pointer_aux +3)    

    def test_change_pixel_two_bits_end_message(self):
        value_correct_red = 65
        value_correct_blue= 122 
        value_correct_green= 22 
        value_source = 67
        pointer_aux = 7
        pointer = self.pvd.change_pixel(self.pix,0,0,value_source,self.data,pointer_aux)
        self.assertEqual(self.pix[0,0][0],value_correct_red)
        self.assertEqual(self.pix[0,0][1],value_correct_green)
        self.assertEqual(self.pix[0,0][2],value_correct_blue)
        self.assertEqual(pointer,pointer_aux +2)  


    def test_change_pixel_one_bit_end_message(self):
        value_correct_red = 67
        value_correct_blue= 122
        value_correct_green= 21
        value_source = 67 
        pointer_aux = 8
        pointer = self.pvd.change_pixel(self.pix,0,0,value_source,self.data,pointer_aux)
        self.assertEqual(self.pix[0,0][0],value_correct_red)
        self.assertEqual(self.pix[0,0][1],value_correct_green)
        self.assertEqual(self.pix[0,0][2],value_correct_blue)
        self.assertEqual(pointer,pointer_aux +1)


    def test_change_pixel_no_bit_end_message(self):
        value_correct_red = 152
        value_correct_blue= 122
        value_correct_green= 20 
        value_source = 67
        pointer_aux = 9
        pointer = self.pvd.change_pixel(self.pix,0,0,value_source,self.data,pointer_aux)
        self.assertEqual(self.pix[0,0][0],value_correct_red)
        self.assertEqual(self.pix[0,0][1],value_correct_green)
        self.assertEqual(self.pix[0,0][2],value_correct_blue)
        self.assertEqual(pointer,pointer_aux)


    def test_change_source_no_change_red(self):        
        value_correct_red = self.pix[0,1][0]
        self.pvd.change_source(self.pix,0,1)
        self.assertEqual(self.pix[0,1][0],value_correct_red)


    def test_change_source_change_red(self):
        value_correct_red = 153
        pointer_aux = 0
        for i in range(4):
            with self.subTest("Message for this subtest",i=i):
                self.pvd.change_source(self.pix,0,i)        
                self.assertEqual(self.pix[0,i][0],value_correct_red)

if __name__ == '__main__':
    unittest.main()


