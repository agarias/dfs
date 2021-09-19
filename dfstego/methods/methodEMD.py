import sys
import importlib.util as import_utils

spec = import_utils.spec_from_file_location("utils", "dfstego/utilities/myutils.py")
utils = import_utils.module_from_spec(spec)
spec.loader.exec_module(utils)

myconstants = utils.import_module("myconstants", "dfstego/utilities/myconstants.py")


def change_data(data,pointer,value):
    """
    Función que recibe un array de bits de un mesaje de texto, la posición del array de bits del siguiente bit a codificar,
    y el valor de la coordenada de color roja de un píxel y que se devuelverá con dos bits codificados en sus bits LSB.

    *Parametros*: 
        -> data : Array de bits a codificar en la matriz de píxeles.

        -> value : Variable que funcionan como entrada/salida y que representa el valor de la coordenada de color roja
                  de un píxel,y se devolverá el valor con dos bits codificados.
        -> pointer : Variable que funciona como entrada/salida donde se indica cual es el siguiente bit a códificar
                     tanto al recibirlo como al devolverlo.          
    """
    dat = data[pointer]*2+data[pointer+1]
    value_red = int((value & myconstants.mask_emb_block_pixel) + dat)
    condition = abs(value -value_red - myconstants.red_color_addition_1) < abs(value -value_red + myconstants.red_color_addition_1)
    if condition and utils.is_in_range(value_red - myconstants.red_color_addition_1):
        value_red = value_red - myconstants.red_color_addition_1
    elif utils.is_in_range(value_red + myconstants.red_color_addition_1):
        value_red = value_red + myconstants.red_color_addition_1
    return value_red


def change_data_end(data,pointer,value_red,value_blue,value_green):
    """
    Función que recibe un array de bits de un mesaje de texto y la posición del array de bits 
    del siguiente bit a codificar que devuelve los valores azul,verde y rojo del pixel 
    que finaliza la codificación del mensaje con el método implementado en el módulo.
    *Parametros*: 
        -> data         : Array de bits a codificar en la matriz de píxeles.

        -> value_blue,value_green,value_red : Variables que funcionan de entrada/salida y que representan los valores azul, verde y rojo del píxel
                                              que finaliza la codificación y que se devolverán modificados según el método
                                              implementado en el módulo.
        -> pointer : Variable que funciona como entrada/salida donde se indica cual es el siguiente bit a códificar
                     tanto al recibirlo como al devolverlo.          
    """
    value_blue = value_blue | myconstants.mask_emb_pixel_end         
    value_green = value_green & myconstants.mask_green_label 
    if len(data)> pointer:
        value_green = value_green | myconstants.mask_emb_pixel_end
        value_red = (value_red & myconstants.mask_to_lsb_0) + data[pointer]
    return value_red,value_blue,value_green


def change_pixel(pix,x,y,data,pointer):
    """
    Función que recibe una matriz de píxeles de una imagen, un array de bits de un mesaje de texto
    las coordenas deun pixel y la posición del array de bits del siguiente bit a codificar
    que codifica parte del mensaje en el píxel inidicado con el método implementado en el módulo.
    *Parametros*: 
        -> x, y         : Coordenas del píxel. 
        -> data         : Array de bits a codificar en la matriz de píxeles.
        
        -> pix : Variable de entrada/salida que representa la Matriz de píxeles de una imagen,
                 se devuelve modificada con los bits del mensajes correspondientes codificados en el pixel.
        -> pointer : Variable que funciona como entrada/salida donde se indica cual es el siguiente bit a códificar
                     tanto al recibirlo como al devolverlo.          
    """ 
    value_red = pix[x,y][myconstants.red]
    value_blue = pix[x,y][myconstants.blue] & myconstants.mask_blue_label
    value_green = pix[x,y][myconstants.green]
    if len(data)< (pointer+2):
        value_red,value_blue,value_green = change_data_end(data,pointer,value_red,value_blue,value_green)
    else:
        value_red = change_data(data,pointer,value_red)
    pix[x,y]=(value_red,value_green,value_blue)
    return pointer+2


def change_source(pix,x,y):
    """
    Función que recibe una matriz de píxeles de una imagen y las coordenas del pixel origen de un bloque
    y que modifica el píxel inidicado con el método implementado en el módulo.

    *Parametros*: 
        -> x,y : Coordenas del píxel origen. 

        -> pix : Variable de entrada/salida que representa la Matriz de píxeles de una imagen,
                 se devuelve con la modificación del pixel indicado.       
    """ 
    value_source = pix[x,y][myconstants.red] & myconstants.mask_merge_emd_source
    d = int(pix[x,y][myconstants.red])-value_source
   
    if (utils.is_in_range(value_source+myconstants.red_color_addition)) and (d > myconstants.diffmax ):
        value_source = value_source+myconstants.red_color_addition
    elif(utils.is_in_range(value_source-myconstants.red_color_addition)) and (d < myconstants.diffmin ):
        value_source = value_source-myconstants.red_color_addition
    
    pix[x,y]=(value_source,pix[x,y][myconstants.green],pix[x,y][myconstants.blue])


def change_block(pix,x,y,data,pointer):
    """
    Función que recibe una matriz de píxeles de una imagen, un array de bits de un mesaje de texto
    las coordenas del origen de un bloque 2x2 y la posición del array de bits del siguiente bit a codificar
    que codifica parte del mensaje en el bloque inidicado con el método implementado en el módulo.
    *Parametros*: 
        -> x, y : Coordenas del origen del bloque 2x2 . 
        -> data : Array de bits a codificar en la matriz de píxeles.

        -> pix : Varieble de entrada/salida que representa la Matriz de píxeles de una imagen,
                 se devuelve modificada con los bits del mensajes correspondientes codificados en el bloque.
        -> pointer : Variable que funciona como entrada/salida donde se indica cual es el siguiente bit a códificar
                     tanto al recibirlo como al devolverlo.          
    """ 
    v = y+1
    w = x+1    
    change_source(pix,x,y)    
    pointer = change_pixel(pix,x,v,data,pointer)   
    pointer = change_pixel(pix,w,y,data,pointer)    
    pointer = change_pixel(pix,w,v,data,pointer) 
    return pointer


def transform_image(pix,data,xmax,ymax):
    """
    Función que recibe una matriz de pixeles de una imagen y un array de bits de un mesaje de texto
    que codifica el mensaje en la matriz de pixeles con el método implementado en el módulo.
    *Parametros*:        
        -> xmax, ymax : Limites vertical y horizontal de la matriz donde se puede codificar el mensaje. 
        -> data       : Array de bits a codificar en la matriz de píxeles

        -> pix : Varieble de entrada/salida que representa la Matriz de píxeles de una imagen,
                 se devuelve modificada con los bits del mensajes codificados.
    *Salida*:   
        -> Devuleve 1 si no ha habido ningún problema y 0 si no se ha podido codificar el mensaje.
    """ 
    pointer = 0 
    x = 0
    y = 0   
    while pointer < len(data):
        if ((y)< (ymax)) and ((x)< (xmax)):
            pointer = change_block(pix,x,y,data,pointer)
        y = y+2
        if y > ymax:
            y = 0 
            x = x+2
            if x > xmax:
                return 0
    if (y < ymax) and (x < xmax):
        value_red = pix[x,y][myconstants.red] | myconstants.mask_emd_source_end
        pix[x,y]=(value_red,pix[x,y][myconstants.green],pix[x,y][myconstants.blue])
        
    return 1


def get_bits_pixel(pix,x,y,output,continue_loop):
    """
    Función que recibe una matriz de píxeles y las coordenas de un pixel, en el que se busca parte de un mesaje de texto codificado
    con el método implementado en el módulo, y devulve los bits codificados en el píxel.
    *Parametros*: 
        -> pix          : Matriz de pixeles en la que se busca un mesaje de texto codificado con el método implementado en el módulo.
        -> x,y          : Coordenadas del pixel. 

        -> output        : Variable que funciona como entrada/salida donde se devolverán los bits obtenidos en el píxel, 
                           si contiene información los bits se guardan despues de esta. 
        -> continue_loop : Variable que funciona como entrada/salida y que indica si continuamos buscando en la matriz 
                           y seguimos con el siguiente píxel. 
    """
    value = pix[x,y][myconstants.blue]
    if value % 2 == 0:
        value_red = pix[x,y][myconstants.red] % myconstants.red_color_addition_1
        value_red_bin = bin(value_red)[2:]
        output = output + utils.get_zeros(2-len(value_red_bin)) + value_red_bin
    else:
        if  pix[x,y][myconstants.green]% 2 == 1:
            if pix[x,y][myconstants.red] % 2 == 0:
                output = output + '0'
            else:
                output = output + '1'
        continue_loop = False
    return continue_loop,output


def get_bits_block(pix,x,y,output,continue_loop):
    """
    Función que recibe una matriz de píxeles y las coordenas de un pixel, en el que se busca parte de un mesaje de texto codificado
    con el método implementado en el módulo, y devulve los bits codificados en el píxel.
    *Parametros*: 
        -> pix          : Matriz de pixeles en la que se busca un mesaje de texto codificado con el método implementado en el módulo.
        -> x,y          : Coordenadas del pixel.

        -> output        : Variable que funciona como entrada/salida donde se devolverán los bits obtenidos en el píxel, 
                           si contiene información los bits se guardan despues de esta. 
        -> continue_loop : Variable que funciona como entrada/salida y que indica si continuamos buscando en la matriz 
                           y seguimos con el siguiente píxel. 

    """
    v = y+1
    w = x+1
    value_source = pix[x,y][myconstants.red] & myconstants.mask_merge_source_emd_or_end
    if value_source != myconstants.mask_emd_source :
        continue_loop = False     

    if continue_loop:
        continue_loop,output = get_bits_pixel(pix,x,v,output,continue_loop)
        continue_loop,output = get_bits_pixel(pix,w,y,output,continue_loop)
        continue_loop,output = get_bits_pixel(pix,w,v,output,continue_loop)

    return continue_loop,output


def get_message_emb(pix,ymax,xmax,output):
    """
    Función que recibe una matriz de pixeles en la que busca un mesaje de texto codificado con el método implementado en el módulo
    , y devulve los bits del mensaje codificado.
    *Parametros*: 
        -> pix          : Matriz de pixeles en la que se busca un mesaje de texto codificado con el método implementado en el módulo.
        -> xmax, ymax   : Limites vertical y horizontal en los que buscar el mensaje de texto codificado en la matriz de pixeles. 
        
        -> output : Variable que funciona como entrada/salida donde se devolverá el mensaje obtenido de la matriz, 
                    si contiene información el mensaje obtenido se guarda despues de esta. 

    """ 
    continue_loop = True
    x = 0
    y = 0
    while (x < xmax and continue_loop):
        value = pix[x,y][myconstants.red]
        if (value % 2)== 0:
            continue_loop,output = get_bits_block(pix,x,y,output,continue_loop)
        else:
            continue_loop = False
        
        y = y+2
        if y > ymax:
            x = x+2
            y = 0
            if x > xmax:
                return '0'

    return output


def encode_message_to_picture(picture,message):
    """
    Función que recibe una imagen y un mesaje, y crea una nueva imagen en la caperta 
    resources/images/output de este proyecto con el mensaje recibido codificado 
    a partir de la imagen recibida con el método implementado em el módulo.
    *Parametros*: 
        -> picture : imagen sin codificar
        -> message : mensaje a codificar en la imagen
    *Salida* :   
        -> Devuelve 1 si no ha habido ningún problema y 0 si no se ha podido codificar el mensaje    
    """
    im = utils.read_image(picture)
    if im == 0 :
        return 0
    name,extension = utils.recovery_image_name(picture)
    pix = im.load()    
    if not message:
        return 0    
    bits_message = utils.transform_message_to_bin(message)[2:]
    data = [utils.transform_data_to_dec(bits_message[i]) for i in range(len(bits_message))]
    result = transform_image(pix,data,im.size[0]-3,im.size[1]-3)
    if result == 1: 
        utils.save_image(im,extension,name+'-stego')
    else:
        im.close()        
    return result

def decode_message_to_picture(picture):
    """
    Función que recibe una imagen en la que busca un mesaje de texto codificado en el método implementado en el módulo
    , y que si lo encuentra lo devuelve.
    *Parametros*: 
        -> picture : en la que busca un mesaje de texto codificado en el método implementado en el módulo
     *Salida* : 
        -> Mensaje de texto codificado en la imagen
        -> Si no es posible encontrar el mensaje se devuelve una cadena vacía
        -> Si no es posible encontrar la imagen se devuelve una mensaje indicándolo
    """
    im = utils.read_image(picture)
    if im == 0 :
        return "No hemos encontrado imagen"
    pix = im.load()
    output = "0b"
    output = get_message_emb(pix,im.size[1]-3,im.size[0]-3,output)
    try:
        output = utils.transform_bit_to_message(int(output,2))
    except:
        output = '' 
    
    return output