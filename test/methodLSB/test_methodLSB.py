from PIL import Image,ImageFilter
import importlib.util as import_utils
import random
import numpy as np
import unittest

spec = import_utils.spec_from_file_location("utils", "dfstego/utilities/myutils.py")
utils = import_utils.module_from_spec(spec)
spec.loader.exec_module(utils)
myconstants = utils.import_module("myconstants", "dfstego/utilities/myconstants.py")


class MethodLSBTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print('In setUpClass() MethodLSBTest')
        cls.elias = utils.import_module("elias", "dfstego/methods/methodLSB.py")

    @classmethod
    def tearDownClass(cls):
        print('In tearDownClass() MethodLSBTest')
        del cls.elias

    def test_code_message_elias_return_correctly(self):
        message = "a"
        codEliasDeltaMessage = "000010001100001"
        self.assertEqual(self.elias.code_message_elias(message),codEliasDeltaMessage)
    

    def test_decode_elias_bits_message_number_code(self):
       codEliasDeltaMessage = "000010001100001"
       check_result = 97
       self.assertEqual(self.elias.decode_elias_bits_message(codEliasDeltaMessage),check_result)

    def test_decode_elias_bits_message_not_number_code(self):
        codEliasDeltaMessage = "10010001100001"
        check_result = -1
        self.assertEqual(self.elias.decode_elias_bits_message(codEliasDeltaMessage),check_result)


if __name__ == '__main__':
    unittest.main()

