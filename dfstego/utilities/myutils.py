from PIL import Image,ImageFilter
import numpy as np
import binascii
import sys
import os, subprocess
import importlib.util as import_utils


def import_module(name_module,path_module):
    spec = import_utils.spec_from_file_location(name_module,path_module)
    module = import_utils.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


myconstants = import_module("myconstants", "dfstego/utilities/myconstants.py")


def transform_data_to_dec(element):
    if (element == '1'):
        return 1
    else:
        return 0
    

def is_in_range(value):
    check = False
    if (value > myconstants.redmin) and (value < myconstants.redmax):
        check = True
    return check


def transform_pixel_rg_bto_gray_scale(pixel):
    return np.dot(pixel,[.3,.6,.1])


def get_zeros(lenght):
    zeros=''
    i = 0
    while ( i <lenght):
        zeros = zeros+'0'
        i = i+1
    return zeros


def transform_message_to_bin(message):
    return bin(int.from_bytes(message.encode(), 'big'))


def transform_bit_to_message(decimal):
    try:
        return decimal.to_bytes((decimal.bit_length() + 7) // 8, 'big').decode()
    except:
        return ''


def read_image(name_image): 
    #_leer _imageen
    try:
        return Image.open(name_image) 
    except:
        return 0


def remove_image(name_image):
    #_leer _imageen
    try:
        os.remove(name_image)
    except:
       return 0


def recovery_image_name(path_image):
    aux= path_image.split(sep='/')   
    image = aux[len(aux)-1]
    name,extension = image.split(sep='.')
    return name,extension


def save_image(image,extension,name_image):
    try:     
        image.save(myconstants.path_images_output + name_image + '.' +extension,extension)
    except:
        print("no se puede guardar la imagen ")


def calculated_dec_of_bin(elements,data,pointer):
    potencia = 1
    value = 0 
    mask = 255     
    data_code = data[pointer:pointer+elements]
    new_pointer = pointer + elements
    while elements > 0 and len(data_code) > 0:
        value = value + data_code[elements-1]*potencia
        mask=mask-potencia
        elements = elements-1
        potencia = potencia*2
    
    return value,new_pointer,mask