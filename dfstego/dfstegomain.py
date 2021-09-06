import importlib.util as import_utils
import sys
import base64

spec = import_utils.spec_from_file_location("utils", "dfstego/utilities/myutils.py")
utils = import_utils.module_from_spec(spec)
spec.loader.exec_module(utils)

lsb = utils.import_module("lsb", "dfstego/methods/methodLSB.py")
emd = utils.import_module("emd", "dfstego/methods/methodEMD.py")
pvd = utils.import_module("pvd", "dfstego/methods/methodPVD.py")
merge = utils.import_module("merge", "dfstego/methods/methodLSBPVDEMD.py")
myconstants = utils.import_module("myconstants", "dfstego/utilities/myconstants.py")



def decode_image(image_stego,method):
    output = ''
    if method == myconstants.lsb:
        output = lsb.decode_message_to_picture(image_stego)
    elif method == myconstants.pvd:
        output = pvd.decode_message_to_picture(image_stego)
    elif method == myconstants.emd:
        output = emd.decode_message_to_picture(image_stego)
    elif method == myconstants.merge:
        output = merge.decode_message_to_picture(image_stego)
    else:
        print('_todavía no hemos implementado el método')
    if output == '':
        print('No hemos podido decodificar el mensaje. Elija otro método')
    else:
        print('El mensaje codificado era :')
        print(output)
    return 0

def code_message(image,message,method):
    exit = 0 
    if method ==  myconstants.lsb:
        exit = lsb.encode_message_to_picture(image,message)
    elif method == myconstants.pvd:
        exit = pvd.encode_message_to_picture(image,message)
    elif method == myconstants.emd:
        exit = emd.encode_message_to_picture(image,message)
    elif method == myconstants.merge:
        exit = merge.encode_message_to_picture(image,message)
    else:
        print('Todavía no hemos implementado el método')
    if exit == 1 :
        print('Se ha codificado mensaje')
    else:
        print('No hemos podido codificar mensaje') 
    return 0

def read_argv():
    command = sys.argv[1]

    if len(sys.argv) == 5:
        if command == 'code': 
            code_message(sys.argv[2],sys.argv[3],sys.argv[4])
    elif len(sys.argv) == 4: 
        if command == 'decode':
            decode_image(sys.argv[2],sys.argv[3])
    else:
        print("Error - Introduce los argumentos correctamente")
        print("Ejemplo: code imagen.png 'Esto es un mensaje a codificar' pvd")
        print("Ejemplo: decode imagenstego.png emd")

if __name__ == '__main__':
    read_argv()


# image = open('avatar.png', 'rb') 
# image_read = image.read()
# image_64_encode = base64.b64encode(image_read)

# image_64_decode = base64.b64decode(image_64_encode) 
# image_result = open('avatar_decode.png', 'wb') # create a writable image and write the decoding result
# image_result.write(image_64_decode)
