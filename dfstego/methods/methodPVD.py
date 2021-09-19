import sys
import importlib.util as import_utils
import time

spec = import_utils.spec_from_file_location("utils", "dfstego/utilities/myutils.py")
utils = import_utils.module_from_spec(spec)
spec.loader.exec_module(utils)

myconstants = utils.import_module("myconstants", "dfstego/utilities/myconstants.py")


def classify(diff):
    nbits = 0   
    if diff < 64:
        nbits = 3
    else:
        nbits = 4
    return nbits


def change_source(pix,x,y):
    """
    Función que recibe una matriz de píxeles de una imagen y las coordenas del pixel origen de un bloque
    y que modifica el píxel inidicado con el método implementado en el módulo.
    *Parametros*: 
        -> x,y : Coordenas del píxel origen. 

        -> pix : Variable de entrada/salida que representa la Matriz de píxeles de una imagen,
                 se devuelve con la modificación del pixel indicado.       
    """ 
    value_red_initial = int(pix[x,y][myconstants.red])
    value_red = value_red_initial | 1
    
    diff = value_red_initial-value_red
    if (diff > myconstants.diffmax) and ((value_red + myconstants.red_color_addition ) < myconstants.redmax):
        value_red=value_red + myconstants.red_color_addition       
    elif (diff < myconstants.diffmin) and ((value_red - myconstants.red_color_addition ) > myconstants.redmin):
        value_red=value_red - myconstants.red_color_addition

    pix[x,y]=(value_red,pix[x,y][myconstants.green],pix[x,y][myconstants.blue])


def calculate_new_diff(diff): 
    if diff > 7:
        if diff >127:
            return 128
        else:
            aux = 8
            while (diff-aux) >= 0:
                aux = aux*2
            return aux // 2
    else:
        return 0

        
def change_image_with_data_end(value_blue,value_green,value_red,pointer,value_source,data):
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
    elements = len(data) - pointer
    value_blue = value_blue & myconstants.mask_blue_label
    value_green = value_green & myconstants.mask_green_label_0
    if elements != 0:
        value,pointer,mask = utils.calculated_dec_of_bin(elements,data,pointer)                       
        if elements == 1:
            value_green = value_green & myconstants.mask_green_label_1
        else:
            value_green = value_green & myconstants.mask_green_label           
        value_green = value_green | elements        
        value_red = value_source & mask
        value_red = value_red + value
    return value_blue,value_green,value_red,pointer


def change_pixel(pix,x,y,value_source,data,pointer):
    """
    Función que recibe una matriz de píxeles de una imagen, un array de bits de un mesaje de texto
    las coordenas deun pixel y la posición del array de bits del siguiente bit a codificar
    que codifica parte del mensaje en el píxel inidicado con el método implementado en el módulo.
    *Parametros*: 
        -> x, y         : Coordenas del píxel. 
        -> data         : Array de bits a codificar en la matriz de píxeles.
        -> value_source : Valor de la coordena de color rojo del origen del bloque al que pertece el píxel

        -> pix : Variable de entrada/salida que representa la Matriz de píxeles de una imagen,
                 se devuelve modificada con los bits del mensajes correspondientes codificados en el pixel.
        -> pointer : Variable que funciona como entrada/salida donde se indica cual es el siguiente bit a códificar
                     tanto al recibirlo como al devolverlo.          
    """     
    diff = abs(value_source -int(pix[x,y][myconstants.red]))
    counter = classify(diff)
    diff = calculate_new_diff(diff)
    value_red = pix[x,y][myconstants.red]
    value_blue = pix[x,y][myconstants.blue] | 1
    value_green = pix[x,y][myconstants.green]
    if len(data)< (pointer+counter):
        value_blue,value_green,value_red,pointer = change_image_with_data_end(value_blue,value_green,value_red,pointer,value_source,data)
    else:
        value_red,pointer,_ = utils.calculated_dec_of_bin(counter,data,pointer)                    
        value_red =value_red + diff
                
        if utils.is_in_range(value_source - value_red):
            value_red=value_source - value_red                   
        else :
            value_red=value_source + value_red                     

    pix[x,y]=(value_red,value_green,value_blue)
    return pointer


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
    value_source = pix[x,y][myconstants.red]    
    pointer = change_pixel(pix,x,v,value_source,data,pointer)   
    pointer = change_pixel(pix,w,y,value_source,data,pointer)    
    pointer = change_pixel(pix,w,v,value_source,data,pointer) 
    return pointer


def transform_image(pix,data,ymax,xmax):
    """
    Función que recibe una matriz de píxeles de una imagen y un array de bits de un mesaje de texto
    que codifica el mensaje en la matriz de píxeles con el método implementado en el módulo.
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
        value_red = pix[x,y][myconstants.red] & myconstants.mask_to_lsb_0
        pix[x,y]=(value_red,pix[x,y][myconstants.green],pix[x,y][myconstants.blue])
    
    return 1


def get_mask(elements):
    """
    Función que recibe un numero de digitos binarios a codificar en un numero de 8 bits  
    y devuleve la máscara para poder codificar ese número de digitos binarios.
    *Parametros*: 
        -> elements : Número de digitos binarios a codificar. 
    *Salida*: 
        -> mask: Máscara para poder codificar elements digitos binarios en un número de 8 bits. 

    """
    potencia = 1
    mask = 255
    while elements > 0: 
        mask = mask -potencia
        potencia = 2*potencia
        elements = elements -1     
    return mask


def get_new_output(value,elements,output):
    """
    Función que recibe un numero de digitos y un valor decimal,transforma el valor decimal en binario con el numero de digitos indicado
    y lo añade los bits obtenidos a un array de bits que se recibe.
    *Parametros*: 
        -> value    : Valor decimal que hay pasar a binario.
        -> elements : Número de digitos que hay que usar para pasar  value a  binario. 

        -> output   : Variable que funciona como entrada/salida donde se devolverán los bits obtenidos del valor indicado,
                      si contiene información los bits se guardan despues de esta.

    """
    if elements != 0:
        bin_output = bin(value)[2:]
        if len(bin_output)< elements:
            bin_output = utils.get_zeros(elements-len(bin_output))+bin_output
        output = output+ bin_output
    return output


def get_bits_pixel(pix,x,y,value_source,output,continue_loop):
    """
    Función que recibe una matriz de píxeles y las coordenas de un pixel, en el que se busca parte de un mesaje de texto codificado
    con el método implementado en el módulo, y devulve los bits codificados en el píxel.
    *Parametros*: 
        -> pix          : Matriz de pixeles en la que se busca un mesaje de texto codificado con el método implementado en el módulo.
        -> x,y          : Coordenadas del pixel. 
        -> value_source : Valor de la coordenada de color rojo del origen del bloque.

        -> output        : Variable que funciona como entrada/salida donde se devolverán los bits obtenidos en el píxel, 
                           si contiene información los bits se guardan despues de esta. 
        -> continue_loop : Variable que funciona como entrada/salida y que indica si continuamos buscando en la matriz 
                           y seguimos con el siguiente píxel. 

    """
    value = int(pix[x,y][myconstants.blue])
    diff = abs(int(pix[x,y][myconstants.red])-value_source)
    if continue_loop:
        if (value % 2)== 1:
            counter = classify(diff)
            value_output= diff-calculate_new_diff(diff) 
            output = get_new_output(value_output,counter,output)
        else:
            elements = pix[x,y][myconstants.green] & myconstants.mask_decode_elements
            mask = get_mask(elements)
            aux = pix[x,y][myconstants.red] & mask
            value = pix[x,y][myconstants.red] - aux         
            output = get_new_output(value,elements,output)
            continue_loop=False        
    
    return continue_loop,output


def get_bits_block(pix,x,y,output,continue_loop):
    """
    Función que recibe una matriz de pixeles y las coordenas del origen de un bloque 2x2,
    en el que se busca parte de un mesaje de texto codificado con el método implementado en el módulo
    , y devulve los bits codificados en el bloque.
    *Parametros*: 
        -> pix    : Matriz de pixeles en la que se busca un mesaje de texto codificado con el método implementado en el módulo.
        -> x,y    : Coordenadas del origen del bloque 2x2. 

        -> output        : Variable que funciona como entrada/salida donde se devolverán los bits obtenidos en el bloque, 
                           si contiene información los bits se guardan despues de esta. 
        -> continue_loop : Variable que funciona como entrada/salida y que indica si continuamos buscando en la matriz 
                           y seguimos con el siguiente bloque. 

    """ 
    v = y+1
    w = x+1 
    value_source = pix[x,y][myconstants.red]
    continue_loop,output = get_bits_pixel(pix,x,v,value_source,output,continue_loop)
    continue_loop,output = get_bits_pixel(pix,w,y,value_source,output,continue_loop)
    continue_loop,output = get_bits_pixel(pix,w,v,value_source,output,continue_loop)

    return continue_loop,output


def get_message_pvd(pix,ymax,xmax,output):
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
    while ((x < xmax) and continue_loop):
        value = pix[x,y][myconstants.red]
        if (value % 2)== 1:
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
    if not message:
        return 0  
    name,extension = utils.recovery_image_name(picture)
    pix = im.load()
    bits_message = utils.transform_message_to_bin(message)[2:]
    data = [utils.transform_data_to_dec(bits_message[i]) for i in range(len(bits_message))] 
    result = transform_image(pix,data,im.size[1]-3,im.size[0]-3)
    if result == 1: 
        utils.save_image(im,extension,name+'-stego')
    else:
        im.close()
    return result


def decode_message_to_picture(picture):
    """
    Función que recibe una imagen en la que busca un mesaje de texto codificado con el método implementado en el módulo
    , y que si lo encuentra lo devuelve.
    *Parametros*: 
        -> picture : Imagen en la que se busca un mesaje de texto codificado con el método implementado en el módulo.
     *Salida* : 
        -> Mensaje de texto codificado en la imagen
        -> Si no es posible encontrar el mensaje se devuelve una cadena vacía
        -> Si no es posible encontrar la imagen se devuelve una mensaje indicándolo
    """ 
    im = utils.read_image(picture)
    if im == 0 :
        return "No hemos encontrado imagen"
    pix = im.load()
    output = ""
    output = get_message_pvd(pix,im.size[1]-3,im.size[0]-3,output)
    try:
        output = utils.transform_bit_to_message(int(output,2))        
    except:
        output = ''
    return output