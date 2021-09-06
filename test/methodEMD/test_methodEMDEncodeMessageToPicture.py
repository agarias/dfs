from PIL import Image,ImageFilter
import importlib.util as import_utils
import random
import numpy as np
import unittest

spec = import_utils.spec_from_file_location("utils", "dfstego/utilities/myutils.py")
utils = import_utils.module_from_spec(spec)
spec.loader.exec_module(utils)
myconstants = utils.import_module("myconstants", "dfstego/utilities/myconstants.py")


class MethodEMDEncodeMessageToPictureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print('In setUpClass() MethodEMDEncodeMessageToPicture')
        cls.emd = utils.import_module("emd", "dfstego/methods/methodEMD.py")

    @classmethod
    def tearDownClass(cls):
        print('In tearDownClass() MethodEMDEncodeMessageToPicture')
        del cls.emd
    

    def setUp(self):
        super().setUp()    
        name_image = "test_image.png"
        if self._testMethodName == "test_encode_message_to_picture_image_incorrect":
            name_image = "test_image_fake.png"
        else:
            x = 200
            y = 200
            if self._testMethodName == "test_encode_message_to_picture_image_correct_message_too_long":
                x = 2
                y = 2            
            img = Image.new('RGBA', (x, y), "white") 
            pix = img.load()
            # recorremos cada uno de los elementos
            for v in range(x):
                for w in range(y):
                    pix[v,w] = (random.randint(0,256),random.randint(0,256),random.randint(0,256))
            # guardamos la imagen png
            name_image = myconstants.path_images_output+name_image
            img.save(name_image)

        self.name_image =name_image  
        name,extension = self.name_image.split(sep='.')        
        self.stego_image = name+"-stego."+extension
       

    def tearDown(self):
        utils.remove_image(self.name_image)
        del self.name_image        
        utils.remove_image(self.stego_image)
        del self.stego_image
        super().tearDown()

    def test_encode_message_to_picture_image_correct(self):
        check_result = 1 
        message = "a"
        self.assertEqual(self.emd.encode_message_to_picture(self.name_image,message),check_result)
        check_result = 0
        im = utils.read_image(self.stego_image)
        self.assertNotEqual(im,check_result)
        result = self.emd.decode_message_to_picture(self.stego_image)
        self.assertEqual(result,message)
        im.close()

    def test_encode_message_to_picture_image_correct_no_message(self):
        check_result = 0 
        message = ''
        self.assertEqual(self.emd.encode_message_to_picture(self.name_image,message),check_result)
        check_result = 0
        im = utils.read_image(self.stego_image)
        self.assertEqual(im,check_result)


    def test_encode_message_to_picture_image_correct_message_too_long(self):
        check_result = 0 
        message = "a"
        self.assertEqual(self.emd.encode_message_to_picture(self.name_image,message),check_result)
        check_result = 0
        im = utils.read_image(self.stego_image)
        self.assertEqual(im,check_result)

 
    def test_encode_message_to_picture_image_incorrect(self):        
        check_result = 0 
        message = "a"
        self.assertEqual(self.emd.encode_message_to_picture(self.name_image,message),check_result)
        name,extension = self.name_image.split(sep='.')
        check_result = 0
        stego_image = name+"-stego."+extension
        im = utils.read_image(stego_image)
        self.assertEqual(im,check_result)

if __name__ == '__main__':
    unittest.main()


