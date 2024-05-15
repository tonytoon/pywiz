import pygame
import pygame.freetype
from pygame.locals import *
import numpy as np
import globals

def loadTextures(file):
    wall_textures = []
    wallTexData = pygame.surfarray.array2d(pygame.Surface.convert(pygame.image.load(file)))
    for y in range(19):
        for x in range(6):
            wall_textures.append(np.rot90(wallTexData[x*globals.TEXTURE_WIDTH:(x+1)*globals.TEXTURE_WIDTH,y*globals.TEXTURE_HEIGHT:(y+1)*globals.TEXTURE_HEIGHT]))
            #wall_textures.append(wallTexData[x*globals.TEXTURE_WIDTH:(x+1)*globals.TEXTURE_WIDTH,y*globals.TEXTURE_HEIGHT:(y+1)*globals.TEXTURE_HEIGHT])
    return wall_textures