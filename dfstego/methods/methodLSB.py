import numpy as np
import binascii
import sys 
import importlib.util as import_utils

spec = import_utils.spec_from_file_location("utils", "dfstego/utilities/myutils.py")
utils = import_utils.module_from_spec(spec)
spec.loader.exec_module(utils)

myconstants = utils.import_module("myconstants", "dfstego/utilities/myconstants.py")

def code_message_elias(message):
    """
    Función que le pasamos una cadena de caracteres y transforma la cadena en un numero binario,
    ese número binario lo transforma en un número en *codificación Elías Delta*.
    *Parametros*: 
        -> message : La cadena de carácteres a codificar en codigo ASCII y codificación Elías delta 
    *Codificación Elías Delta*: 
        -> Primero se le añade a su izquierda el número de bits, codificado en binario que codifican el número.
        Por ejemplo, si tenemos 101 añadiriamos 3 codificado en binario a la izquierda obtendriamos 11101.
        
        -> Después tenemos que añadir a la izquierda un número de ceros igual a los bits necesarios para la codificación
        del número de bits.  En el ejemplo que hemos puesto hemos codificado 3 que su codificación que require 2 bits 
        por lo tanto añadiríamos 2 ceros y obtendríamos 0011101 
    
    """
    bits = utils.transform_message_to_bin(message)
    size = len(bits)-1
    binario_aux = bin(size)
    binario_aux= binario_aux[2:(len(binario_aux))]
    bits= bits[2:]
    return utils.get_zeros(len(binario_aux))+binario_aux+bits

def change_bit(pix,x,y,z,element):
    """
    Función que le pasamos una matriz de pixeles,las coordenas y el color del pixel a modificar, más el elemento a codificar o 0 o 1 
    y modifica el bit menos significativo el color del pixel que pasamos según el elemento que hayamos pasado si no coincide con el elemento a codificar.

    *Paramtetros* : 
        -> pix     : Matriz de color de pixeles de la imagen en la que hay que codificar el mensaje
        -> x,y     : Coordenas del pixel a modificar , son dos enteros
        -> z       : Color a modificar del pixel, es un entero entre los valores 0,1,2. 0 indica rojo, 1 indica green , 2 indica blue  
        -> element : Bit que tenemos que codificar en el pixel, en forma de caracter '0' o '1'
    """
    value = pix[x,y][z]
    change =False
    if (element == '1') and value % 2 == 0:
        value = value | 1
        change =True
    else:
        if (element == '0') and value % 2 == 1:
            value = value ^ 1
            change =True
    if change:
            if z == myconstants.red:
                    pix[x,y]=(value,pix[x,y][myconstants.green],pix[x,y][myconstants.blue])
            if z == myconstants.green:
                    pix[x,y]=(pix[x,y][myconstants.red],value,pix[x,y][myconstants.blue])
            if z == myconstants.blue:
                    pix[x,y]=(pix[x,y][myconstants.red],pix[x,y][myconstants.green],value)

def move_pointer(x,y,z,maximum):
    """
    Función que mueve el puntero de la matriz de color de pixeles una posición ya sea por en la dimensión del color o en las coordenas x e y.
    Dadas las coordenas actuales de la matriz x,y,z (donde z representa el color), primero se mueve en la coordena del color, si no esta en azul 
    pasamos a la siguiente en el orden RGB (rojo-verde-azul), si estamos en azul tenemos que cambiar de coordena de pixel, y nos moveremos primero 
    por la coordena y. Si hemos llegado al final de la coordenada y pasaremos a mover la coordena x. 
    Ejemplos :
        Si tenemos un maximo de y de 10, y empezamos en la coordena x,y (0,0) y con el color rojo, al salir de la función seguiremos en la coordena (0,0)
        pero habremos pasado al verde
        Si tenemos un maximo de y de 10, y empezamos en la coordena x,y (0,0) y con el color azul, al salir de la función saltaremos a la coordena (0,1)
        pero habremos pasado al rojo 
        Si tenemos un maximo de y de 10, y empezamos en la coordena x,y (0,10) y con el color azul, al salir de la función saltaremos a la coordena (1,0)
        pero habremos pasado al rojo 
    

    *Paramtetros* :         
        -> x,y     : Coordenas del pixel donde estamos, son dos enteros.
        -> z       : Color del pixel por donde estamos, es un entero entre los valores 0,1,2. 0 indica rojo, 1 indica green , 2 indica blue  
        -> maximun : Maximo de la coordenada y es un entero

    *Salida*:
        -> x,y,z : Seran las tres coordenadas se hayan modificado o no, son tres enteros
    """
    if z < myconstants.blue :
        z = z + 1
    else:
        z = myconstants.red
        if y < maximum:
            y = y+1
        else:
            y=0
            x= x+1
    return x,y,z

# def encode_message(message,pix,maximum):   
#     value_b = len(message) % 256
#     value_g = len(message) // 256
#     pix[0,0]=(pix[0,0][0],value_g,value_b)
#     x = 0
#     y = 1
#     z = 0
#     for element in message:
#         change_bit(pix,x,y,z,element)
#         x,y,z = move_pointer(x,y,z,maximum)
def read_loop_bits(end,x,y,z,pix,maximum):
    """
    Función que lee un número determinado de bits codificados en una matriz de color de pixeles y que empieza en unas determinadas coordenadas. 

    *Paramtetros* : 
        -> end     : Numero de bits a leer.
        -> x,y     : Coordenas del pixel donde estamos, son dos enteros.
        -> z       : Color del pixel por donde estamos, es un entero entre los valores 0,1,2. 0 indica rojo, 1 indica green , 2 indica blue.
        -> pix     : Matriz de color de pixeles de la imagen en la que hay un mensaje codificado  
        -> maximun : Maximo de la coordenada y es un entero
    *Salida* : 
        -> x,y,z     : Las coordenadas modificas son tres enteros 
        -> read_bits : Será una cadena de caracteres con los bits leidos de la matriz.  
    """
    bits_aux = 1
    read_bits =''
    while(bits_aux < end ):
        value = pix[x,y][z]
        if value % 2 == 0:
            read_bits = read_bits+"0"
        else:
            read_bits = read_bits+"1"
        bits_aux = bits_aux+1
        x,y,z = move_pointer(x,y,z,maximum)
    return x,y,z,read_bits

def decode_elias_message(pix,maximun,my_size):
    """
    Función que lee un número binario codificado en un matriz de color de pixeles y lo devuelve en decimal. 

    *Paramtetros* : 
        -> pix     : Matriz de color de pixeles de la imagen en la que hay un mensaje codificado  
        -> maximun : Maximo de la coordenada y, es un entero
    *Salida* : 
        -> Numero decimal recogido de la imagen que debería representar un mensaje
        -> Si no hay níngun número códificado devolvemos -1 
    """
    x = 0
    y = 0
    z = 0
    bits = 0
    continue_loop = True
    while ((bits < my_size ) & continue_loop):
        value = pix[x,y][z]
        if value % 2 == 0:
            bits = bits +1
        else:
            continue_loop = False
        x,y,z = move_pointer(x,y,z,maximun)
    if bits> 0 :
        x,y,z,read_bits =read_loop_bits(bits,x,y,z,pix,maximun)
        read_bits = '1'+ read_bits
        new_size = int(read_bits, 2)
        if (new_size >0):
            x,y,z,read_bits =read_loop_bits(new_size,x,y,z,pix,maximun)
            try:
                return int(read_bits, 2)
            except:
                return -1
        else:
            return -1
    else:
        return -1
    


def loop_through_bits(end,bits_message,pointer):
    bits = 0
    read_bits = ''
    if not (pointer < len(bits_message)):
        read_bits = '0'
    while (bits< end) and (pointer < len(bits_message)):
        value = bits_message[pointer]
        if value == "0":
            read_bits = read_bits+"0"
        else:
            read_bits = read_bits+"1"
        bits = bits+ 1
        pointer = pointer +1
    return read_bits,pointer


def decode_elias_bits_message(bits_message):
    pointer = 0
    bits = 0
    continue_loop = True
    while (continue_loop):
        value = bits_message[pointer]        
        if value == "0":
            bits = bits +1
            pointer = pointer +1
        else:
            continue_loop = False
    if bits> 0 :
        end = pointer
        read_bits,pointer = loop_through_bits(end,bits_message,pointer)
        end = int(read_bits, 2)
        if (end >0):
            read_bits,pointer = loop_through_bits(end,bits_message,pointer)    
            return int(read_bits, 2)
        else:
            return -1
    else:
        return -1


def encode_message_to_picture(picture,message):
    im = utils.read_image(picture)
    if im == 0 :
        return 0
    name,extension = utils.recovery_image_name(picture)
    pix = im.load()    
    maximun = im.size[1]-1
    my_size = im.size[0]*im.size[1]*3
    if not message:
        return 0

    bits_message = code_message_elias(message)
    if len(bits_message) > my_size: 
        return 0
    x = 0
    y = 0
    z = 0
    for element in bits_message:
        change_bit(pix,x,y,z,element)
        x,y,z = move_pointer(x,y,z,maximun)
    utils.save_image(im,extension,name+'-stego')
    return 1

def decode_message_to_picture(picture):
    im = utils.read_image(picture)
    if im == 0 :
        return "No hemos encontrado imagen"
    maximum = im.size[1]-1
    pix =  im.load()    
    my_size = im.size[0]*im.size[1]*3
    decimal = decode_elias_message(pix,maximum,my_size)
    output = utils.transform_bit_to_message(decimal) 
    return output
