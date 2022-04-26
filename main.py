import PIL.Image
from ctypes.wintypes import RGB
from os import listdir
from os.path import isfile, isdir
import numpy as np
import argparse

MAX_INT = 42424242

def rgb2hex(rgb : tuple) -> str:
    return('#{:02x}{:02x}{:02x}'.format(rgb[0],rgb[1],rgb[2]))

def hex2rgb(hex : str) -> tuple:
    return(tuple(int(hex.strip("#")[i:i+2], 16) for i in (0, 2, 4)))

def mean_color_of_image(image : PIL.Image.Image) -> tuple:
    array = np.array(image.getdata())
    mean = array.mean(axis=0, dtype=int)
    mean = mean[:3]
    return(tuple(mean))

def median_color_of_image(image : PIL.Image.Image) -> tuple:
    array = np.array(image.getdata())
    median = np.mean(array, axis=0, dtype=int)
    median = median[:3]
    return(tuple(median))

def get_palette_from_file(filePath : str) -> list:
    palette = list()
    array = np.genfromtxt(filePath, delimiter=",", dtype=int)
    for rgb in array:
        palette.append(tuple(rgb))
    return(palette)

def get_palette_from_folder(directoryPath : str) -> list:
    palette = list()
    for file in listdir(directoryPath):
        tmp_img = PIL.Image.open(directoryPath+"/"+file)
        tmp_averagecolor = mean_color_of_image(tmp_img)
        palette.append(tmp_averagecolor)
    return(palette)

def closest_rgb(color : tuple, color_list : list) -> tuple:
    color_list = np.array(color_list)
    color = np.array(color)
    distances = np.sqrt(np.sum((color_list-color)**2,axis=1))
    index_of_smallest = np.where(distances==np.amin(distances))
    return(tuple(color_list[index_of_smallest][0]))

def closest_image(color_palette : list, image : PIL.Image.Image) -> PIL.Image.Image:
    image.convert("RGB")
    closest_image = image.copy()
    closest_colors = dict()

    for x in range(image.width):
        for y in range(image.height):
            tmp_rgb = image.getpixel((x,y))
            if(tmp_rgb not in closest_colors):
                closest_colors[tmp_rgb] = closest_rgb(tmp_rgb, color_palette)
            closest_image.putpixel((x,y), closest_colors[tmp_rgb])
    return closest_image

def get_colors2array(get_colors : list) -> np.ndarray:
    array = np.empty(shape=[0,4], dtype=int)
    for x in range(len(get_colors)):
        if(get_colors[x][1][3] != 0):
            array = np.vstack([array, np.append(get_colors[x][0], np.array(get_colors[x][1][:3]))])
    return(array)


def main():

    parser = argparse.ArgumentParser(description='Script to convert spritesheet to a restricted color palette scraped from directory.')

    parser.add_argument('-i', '--imagePath', action='store', dest='imagePath', type=str, default="spritesheet.png", help='Spritesheet to process.')
    parser.add_argument('-c', '--color_palette', action='store', dest='color_palette', type=str, default="fusebeads_palette", help='Path to color palette : either a txt file with coma-separated r,g,b values per line OR path to a directory where each image file dominant color will be scraped.')
    parser.add_argument('-o', '--outpath', action='store', dest='outPath', type=str, default="PROCESSED_spritesheet", help='outfile path to write converted spritesheet as png and converted color pixel count as csv.')
    parser.add_argument("-v", "--verbose", action = "store_true", dest='verbose', help = "run script with more verbose.")

    args = parser.parse_args()

    if(args.verbose):
        print("# loading input image :"+args.imagePath)
    image=PIL.Image.open(args.imagePath)
    image.load()

    # store alpha channel
    alphachan = image.split()[-1]
    image = image.convert("RGB")

    ## Get color palette from taking average color for each files in directory (or pickled list)
    if(args.verbose):
        print("# loading color palette from :"+args.color_palette)

    if(isfile(args.color_palette)):
        palette_rgb = get_palette_from_file(args.color_palette)
    elif(isdir(args.color_palette)):
        palette_rgb = get_palette_from_folder(args.color_palette)
    else:
        print("--color_palette need to be a file or a directory path.")
        exit()
    
    #palette_hex = [rgb2hex(rgb) for rgb in palette_rgb]

    ## Convert colors to color palette (aka avaliable fusebead colors)
    if(args.verbose):
        print("# converting each pixel to closest color in palette")

    new_image = closest_image(palette_rgb, image)
    new_image.putalpha(alphachan) #add alpha channel again

    ## Count number of pixels of each new color (aka necessary fusebeads of each color to complete the project)
    image_colors_rgb = new_image.getcolors(MAX_INT)

    ## Output
    if(args.verbose):
        print("# output management")
        
    new_image.save(args.outPath+".png")
    np.savetxt(args.outPath+".csv", get_colors2array(image_colors_rgb), delimiter=",", fmt="%i", comments="", header="pixel count,r,g,b")

    return(True)

if __name__ == "__main__":
    main()