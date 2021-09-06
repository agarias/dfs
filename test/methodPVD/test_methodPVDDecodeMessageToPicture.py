from PIL import Image,ImageFilter
import importlib.util as import_utils
import random
import numpy as np
import unittest

spec = import_utils.spec_from_file_location("utils", "dfstego/utilities/myutils.py")
utils = import_utils.module_from_spec(spec)
spec.loader.exec_module(utils)
myconstants = utils.import_module("myconstants", "dfstego/utilities/myconstants.py")


class MethodPVDDecodeMessageToPictureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print('In setUpClass() MethodPVDDecodeMessageToPicture')
        cls.pvd = utils.import_module("pvd", "dfstego/methods/methodPVD.py")

    @classmethod
    def tearDownClass(cls):
        print('In tearDownClass() MethodPVDDecodeMessageToPicture')
        del cls.pvd
    

    def setUp(self):
        img = Image.new('RGBA', (200, 200), "white") 
        pix = img.load()
        #1100001
        # recorremos cada uno de los elementos
        for v in range(200):
            for w in range(200):
                pix[v,w] = (random.randint(0,256),random.randint(0,256),random.randint(0,256))
        pix[0,0] = (153,26,122)
        pix[0,1] = (139,23,123)
        pix[1,0] = (153,23,123)
        pix[1,1] = (165,25,122)
        pix[0,2] = (152,22,123)
        pix[0,3] = (153,23,123)
        pix[1,2] = (151,24,123)
        pix[1,3] = (152,24,123) 
        pix[0,4] = (160,22,122)
        pix[0,5] = (156,23,122)
        pix[1,4] = (151,25,123)
        pix[1,5] = (152,24,123)
        name_image = "test_image.png"
        self.name_image  = myconstants.path_images_input+name_image       
        self.img = img
        self.pix = pix
       

    def tearDown(self):
        if (self.name_image != "test_image_fake.png"):
            utils.remove_image(self.name_image)
        del self.name_image
        del self.img
        del self.pix
        super().tearDown()

    def test_decode_message_to_picture_image_correct(self):
        self.img.save(self.name_image)
        message = "a"
        self.assertNotEqual(self.name_image,"error")
        self.assertEqual(self.pvd.decode_message_to_picture(self.name_image),message)


    def test_decode_message_to_picture_image_correct_no_message(self):
        
        self.pix[0,0] = (122,122,124)
        self.img.save(self.name_image)
        message = ''
        self.assertNotEqual(self.name_image,"error")
        self.assertEqual(self.pvd.decode_message_to_picture(self.name_image),message)


    def test_decode_message_to_picture_image_incorrect(self):
        self.name_image = "test_image_fake.png"
        message = "No hemos encontrado imagen"
        self.assertEqual(self.pvd.decode_message_to_picture(self.name_image),message)


if __name__ == '__main__':
    unittest.main()


