import sys
import importlib.util as import_utils

spec = import_utils.spec_from_file_location("utils", "dfstego/utilities/myutils.py")
utils = import_utils.module_from_spec(spec)
spec.loader.exec_module(utils)

elias = utils.import_module("elias", "dfstego/methods/methodLSB.py")
emd = utils.import_module("emd", "dfstego/methods/methodEMD.py")
pvd = utils.import_module("pvd", "dfstego/methods/methodPVD.py")
myconstants = utils.import_module("myconstants", "dfstego/utilities/myconstants.py")


def values_block(x,y,v,w,pix):
    red_pc = int(pix[x,y][myconstants.red])
    red_p1 = int(pix[x,v][myconstants.red])
    red_p2 = int(pix[w,y][myconstants.red])
    red_p3 = int(pix[w,v][myconstants.red])
    return red_pc,red_p1,red_p2,red_p3


def calculate_average_pixel_value_difference(red_pc,red_p1,red_p2,red_p3):
    d1=abs(red_pc-red_p1)
    d2=abs(red_pc-red_p2)
    d3=abs(red_pc-red_p3)
    return (d1+d2+d3)/(myconstants.pixels_in_block-1)

    
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
    red_pc,red_p1,red_p2,red_p3 = values_block(x,y,v,w,pix)
    average = calculate_average_pixel_value_difference(red_pc,red_p1,red_p2,red_p3)
    if average > myconstants.average_max_in_lsb_pvd_emd:
        pointer = pvd.change_block(pix,x,y,data,pointer)
    else:
        pointer = emd.change_block(pix,x,y,data,pointer)

    return pointer


def transform_image(pix,data,ymax,xmax):

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
        value_red = (pix[x,y][myconstants.red] & myconstants.mask_merge_emd_source) | myconstants.mask_merge_end_source
        pix[x,y]=(value_red,pix[x,y][myconstants.green],pix[x,y][myconstants.blue])
    return 1

def get_message(pix,ymax,xmax,output):
    """
    Función que recibe una matriz de pixeles en la que busca un mesaje de texto codificado con el método implementado en el módulo
    , y devulve los bits del mensaje codificado.
    *Parametros*: 
        -> pix          : Matriz de pixeles en la que se busca un mesaje de texto codificado con el método implementado en el módulo.
        -> xmax, ymax   : Limites vertical y horizontal en los que buscar el mensaje de texto codificado en la matriz de pixeles. 
        
        -> output : Variable que funciona como entrada/salida donde se devolverá el mensaje obtenido de la matriz, 
                    si contiene información el mensaje obtenido se guarda despues de esta. Devuelve 0 si hay algún problema 

    """ 
    x = 0
    y = 0
    continue_loop = True
    while (x < xmax and continue_loop):
        value = pix[x,y][myconstants.red]
        if (value % 2)== 1:
            continue_loop,output = pvd.get_bits_block(pix,x,y,output,continue_loop)
        else:
            continue_loop,output = emd.get_bits_block(pix,x,y,output,continue_loop)
            
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
    pix = im.load() 
    name,extension = utils.recovery_image_name(picture)    
    bits_message = elias.code_message_elias(message)
    data = [utils.transform_data_to_dec(bits_message[i]) for i in range(len(bits_message))]   
    result = transform_image(pix,data,im.size[1]-3,im.size[0]-3)
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
    binary = ''
    binary = get_message(pix,im.size[1]-3,im.size[0]-3,binary) 
    try:
        output = elias.decode_elias_bits_message(binary)
        output = utils.transform_bit_to_message(output)
    except:
        output = '' 
    return output