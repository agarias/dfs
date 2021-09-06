import sys
import importlib.util as import_utils

spec = import_utils.spec_from_file_location("utils", "dfstego/utilities/myutils.py")
utils = import_utils.module_from_spec(spec)
spec.loader.exec_module(utils)

myconstants = utils.import_module("myconstants", "dfstego/utilities/myconstants.py")


def change_data(data,pointer,value):
    dat = data[pointer]*2+data[pointer+1]
    value_red = int((value & myconstants.mask_emb_block_pixel) + dat)
    condition = abs(value -value_red - myconstants.red_color_addition_1) < abs(value -value_red + myconstants.red_color_addition_1)
    if condition and utils.is_in_range(value_red - myconstants.red_color_addition_1):
        value_red = value_red - myconstants.red_color_addition_1
    elif utils.is_in_range(value_red + myconstants.red_color_addition_1):
        value_red = value_red + myconstants.red_color_addition_1
    return value_red


def change_data_end(data,pointer,value_red,value_blue,value_green):
    value_blue = value_blue | myconstants.mask_emb_pixel_end         
    value_green = value_green & myconstants.mask_green_label 
    if len(data)> pointer:
        value_green = value_green | myconstants.mask_emb_pixel_end
        value_red = (value_red & myconstants.mask_to_lsb_0) + data[pointer]
    return value_red,value_blue,value_green


def change_pixel(pix,x,y,data,pointer):
    value_red = pix[x,y][myconstants.red]
    value_blue = pix[x,y][myconstants.blue] & myconstants.mask_blue_label
    value_green = pix[x,y][myconstants.green]
    if len(data)< (pointer+2):
        value_red,value_blue,value_green = change_data_end(data,pointer,value_red,value_blue,value_green)
    else:
        value_red = change_data(data,pointer,value_red)
    pix[x,y]=(value_red,value_green,value_blue)
    return pointer+2


def change_source(pix,x,y,data,pointer):
    value_source = pix[x,y][myconstants.red] & myconstants.mask_merge_emd_source
    d = int(pix[x,y][myconstants.red])-value_source
    # if not is_merge:
    #     if len(data)< (pointer+2):
    #         s =data[pointer]*4+data[pointer+1]*2
    #         i = pix[x,y][myconstants.red] & myconstants.mask_emb_block_source_0
    #         d = i-s
    #     value_source = (pix[x,y][myconstants.red] & myconstants.mask_emb_block_source_0) + s
    #     pointer = pointer+2
    
    if (utils.is_in_range(value_source+myconstants.red_color_addition)) and (d > myconstants.diffmax ):
        value_source = value_source+myconstants.red_color_addition
    elif(utils.is_in_range(value_source-myconstants.red_color_addition)) and (d < myconstants.diffmin ):
        value_source = value_source-myconstants.red_color_addition
    
    pix[x,y]=(value_source,pix[x,y][myconstants.green],pix[x,y][myconstants.blue])   
    return pointer


def change_block(pix,x,y,data,pointer):
    v = y+1
    w = x+1    
    pointer = change_source(pix,x,y,data,pointer)    
    pointer = change_pixel(pix,x,v,data,pointer)   
    pointer = change_pixel(pix,w,y,data,pointer)    
    pointer = change_pixel(pix,w,v,data,pointer) 
    return pointer


def transform_image(pix,data,xmax,ymax):
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
    # if (y < ymax) and (x < xmax):
    #     value_red = pix[x,y][myconstants.red] | myconstants.mask_emd_source_end
    #     pix[x,y]=(value_red,pix[x,y][myconstants.green],pix[x,y][myconstants.blue])
        
    return 1


def get_bits_pixel(pix,x,y,output,continue_loop):
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


def get_bits_block(pix,x,y,output,continue_loop,is_merge = False):
    v = y+1
    w = x+1
    value_source = pix[x,y][myconstants.red] & myconstants.mask_merge_source_emd_or_end
    if value_source != myconstants.mask_emd_source :
        continue_loop = False     

    if continue_loop:
        # if not is_merge :
        #     value_source = pix[x,y][myconstants.red] & myconstants.mask_emb_block_source_1
        #     value_source_bin = bin(value_source//2)[2:]
        #     output= output + utils.get_zeros(2-len(value_source_bin)) + value_source_bin
        continue_loop,output = get_bits_pixel(pix,x,v,output,continue_loop)
        continue_loop,output = get_bits_pixel(pix,w,y,output,continue_loop)
        continue_loop,output = get_bits_pixel(pix,w,v,output,continue_loop)

    return continue_loop,output


def get_message_emb(pix,ymax,xmax,output):
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