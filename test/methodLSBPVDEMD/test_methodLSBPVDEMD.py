from PIL import Image,ImageFilter
import importlib.util as import_utils
import random
import numpy as np
import unittest

spec = import_utils.spec_from_file_location("utils", "dfstego/utilities/myutils.py")
utils = import_utils.module_from_spec(spec)
spec.loader.exec_module(utils)
myconstants = utils.import_module("myconstants", "dfstego/utilities/myconstants.py")

 
class MethodLSBPVDEMDTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('In setUpClass() MethodLSBPVDEMD')
        cls.merge = utils.import_module("merge", "dfstego/methods/MethodLSBPVDEMD.py")

    @classmethod
    def tearDownClass(cls):
        print('In tearDownClass() MethodLSBPVDEMD')
        del cls.merge
    

    def setUp(self):
        super().setUp()           
        self.pix = np.zeros((4,4,3),np.uint8)
        self.pix[0,0] = [152,22,122]
        self.pix[0,1] = [128,23,123]
        self.pix[1,0] = [129,24,122]
        self.pix[1,1] = [130,25,123]
        self.pix[0,2] = [152,22,122]
        self.pix[0,3] = [153,23,123]
        self.pix[1,2] = [154,24,122]
        self.pix[1,3] = [155,25,123]
        self.pix[2,0] = [152,22,122]
        self.pix[2,1] = [153,23,123]
        self.pix[3,0] = [154,24,122]
        self.pix[3,1] = [155,25,123]
        self.pix[2,2] = [152,22,122]
        self.pix[2,3] = [153,23,123]
        self.pix[3,2] = [154,24,122]
        self.pix[3,3] = [155,25,123]
        
        self.data = [1,1,1,0,0,1,0,0,1,1,1,0,0,1,0,0,1] 
       

    def tearDown(self):
        del self.pix
        del self.data
        super().tearDown()


    def test_change_block_all_pixel_code_emd(self):
        values_corrects_red = [[152,159],[158,149]]
        values_corrects_blue= [[122,122],[122,122]]   
        pointer_aux = 0
        pointer = self.merge.change_block(self.pix,0,2,self.data,pointer_aux)
        self.assertEqual(pointer,pointer_aux +6) 
        for i in range(2):
            for j in range(2):                       
                self.assertEqual(self.pix[i,j+2][0],values_corrects_red[i][j])
                self.assertEqual(self.pix[i,j+2][2],values_corrects_blue[i][j])    

    
    def test_change_block_all_pixel_code_pvd(self):
        values_corrects_red = [[153,130],[136,136]]
        values_corrects_blue= [[122,123],[123,123]]   
        pointer_aux = 0
        pointer = self.merge.change_block(self.pix,0,0,self.data,pointer_aux)
        self.assertEqual(pointer,pointer_aux +9) 
        for i in range(2):
            for j in range(2):                       
                self.assertEqual(self.pix[i,j][0],values_corrects_red[i][j])
                self.assertEqual(self.pix[i,j][2],values_corrects_blue[i][j])
 

    def test_change_block_not_all_pixel_code_emd(self):
        values_corrects_red = [[152,148],[155,155]]
        values_corrects_blue= [[122,122],[123,123]] 
        values_corrects_green= [[22,23],[25,24]] 
        pointer_aux = 14
        pointer = self.merge.change_block(self.pix,0,2,self.data,pointer_aux)
        self.assertEqual(pointer,pointer_aux +6) 
        for i in range(2):
            for j in range(2):                       
                self.assertEqual(self.pix[i,j+2][0],values_corrects_red[i][j])
                self.assertEqual(self.pix[i,j+2][1],values_corrects_green[i][j])
                self.assertEqual(self.pix[i,j+2][2],values_corrects_blue[i][j]) 
    

    
    def test_change_block_not_all_pixel_code_pvd(self):
        values_corrects_red = [[153,135],[153,130]]
        values_corrects_blue= [[122,123],[122,122]] 
        values_corrects_green= [[22,23],[26,24]] 
        pointer_aux = 12
        pointer = self.merge.change_block(self.pix,0,0,self.data,pointer_aux)
        self.assertEqual(pointer,pointer_aux +5) 
        for i in range(2):
            for j in range(2):                       
                self.assertEqual(self.pix[i,j][0],values_corrects_red[i][j])
                self.assertEqual(self.pix[i,j][1],values_corrects_green[i][j])
                self.assertEqual(self.pix[i,j][2],values_corrects_blue[i][j])  


    def test_transform_image_message_correct(self):        
        self.data = [1,1,1,0,0,1,0,0,1,1,1,1,0,0,1] 
        values_corrects_red = [[153,130,152,159],[136,136,158,149]]
        values_corrects_blue= [[122,123,122,122],[123,123,122,122]] 
        values_corrects_green= [[22,23,22,23],[24,25,24,25]] 
        result = self.merge.transform_image(self.pix,self.data,3,3)
        self.assertEqual(result,1)
        for i in range(2):
            for j in range(4):                      
                self.assertEqual(self.pix[i,j][0],values_corrects_red[i][j])
                self.assertEqual(self.pix[i,j][1],values_corrects_green[i][j])
                self.assertEqual(self.pix[i,j][2],values_corrects_blue[i][j])


    def test_transform_image_message_too_long(self):
        self.data = [1,1,1,0,0,1,0,0,1,1,0,1,1,0,1,1,0] 
        self.pix = np.zeros((2,2,3),np.uint8)
        result = self.merge.transform_image(self.pix,self.data,1,1)
        self.assertEqual(result,0) 


if __name__ == '__main__':
    unittest.main()


