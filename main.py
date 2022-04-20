from PIL import Image, ImageOps
from os import listdir
import pickle


def rgb2hex(r,g,b):
    return('#{:02x}{:02x}{:02x}'.format(r,g,b))

def hex2rgb(hex):
    return(tuple(int(hex.strip("#")[i:i+2], 16) for i in (0, 2, 4)) )

def average_color_of_image(pil_img):
    img = pil_img.copy()
    img = img.convert("RGB")
    img = img.resize((1, 1), resample=0)
    return(img.getpixel((0, 0)))

def get_palette_from_folder(directoryPath):
    palette = list()
    for file in listdir(directoryPath):
        tmp_img = Image.open(file)
        tmp_averagecolor = average_color_of_image(tmp_img)
        palette.append(tmp_averagecolor)
    return(palette)


filePath="firered-leafgreen.png"

image=Image.open(filePath)
image.load()

## Image processing
imageSize = image.size

# remove alpha channel
invert_im = image.convert("RGB") 

# invert image (so that white is 0)
invert_im = ImageOps.invert(invert_im)

# crop background
imageBox = invert_im.getbbox()
cropped=image.crop(imageBox)

## Get color palette from taking average color of all files in directory (or pickled list)

## Convert colors to color palette (aka avaliable fusebead colors)

## Count number of pixels of each new color (aka necessary fusebeads of each color to complete the project)
