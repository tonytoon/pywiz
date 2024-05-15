import pygame
import pygame.freetype
from pygame.locals import *
import math
import numpy as np
import csv
import globals
import textures
import raycast

class Maze:
    def __init__(self, x, y):
        self.width = x
        self.height = y
        self.cells = [0 for a in range(x*y)]

    def getCell(self, x, y):
        if y >= 0 and y <= 19 and x >= 0 and x <= 19:
            return self.cells[(y*self.width)+x]
        else:
            return(31)

    def getWalls(self, x, y):
        walls = []
        if y >= 0 and y <= 19 and x >= 0 and y <= 19:
            if self.cells[(y*self.width)+x] & globals.WALL_N: walls.append("N")
            if self.cells[(y*self.width)+x] & globals.WALL_E: walls.append("E")
            if self.cells[(y*self.width)+x] & globals.WALL_S: walls.append("S")
            if self.cells[(y*self.width)+x] & globals.WALL_W: walls.append("W")
        else:
            walls = "OOB"
        return walls

    def setCell(self, x, y, value):
        self.cells[(y*self.width)+x] = value
        
    def fromCSV(self, filename):
        with open(filename, encoding='utf-8-sig') as csvfile:
            csvreader = csv.reader(csvfile)
            for y, row in enumerate(csvreader):
                for x, cell in enumerate(row):
                    self.setCell(x, y, int(cell))
    
    def printMaze(self):
        for y in range(20):
            for x in range(20):
                print(self.getCell(x,y), end="")
            print()

def tryMove(pos, dir):
    return True

def vectorToCompass(dir_vector):
    angle = np.round(np.degrees(np.arctan2(-dir_vector[1],dir_vector[0])),0)
    if angle == 0 or angle == 360:
        return "EAST"
    elif angle == 90 or angle == -270:
        return "NORTH"
    elif angle == 180 or angle == -180:
        return "WEST"
    elif angle == 270 or angle == -90:
        return "SOUTH"
    else:
        return angle


screen = pygame.display.set_mode((globals.APP_WIDTH,globals.APP_HEIGHT))
wall_textures = textures.loadTextures("wolf_walls.png")
maze = Maze(20,20)
maze.fromCSV('maze2.csv')
#print(31 >> 5)
running = True

pygame.init()

clock = pygame.time.Clock()

TURN_STEP = math.pi / 2
starting_pos = (0.5,19.5)
pos_vector = np.array(starting_pos)
dir_vector = np.array([0,-1])
cam_vector = np.array([1.12,0])

screen_dirty = True
demo = False
texnum = 0

while running:
    angle = 0
    turned = False
    moved = False

    # event handling, gets all event from the event queue

    for event in pygame.event.get():
        # only do something if the event is of type QUIT
        if event.type == pygame.QUIT:
            # change the value to False, to exit the main loop
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == K_EQUALS:
                if texnum < 113:
                    texnum += 1
                    screen_dirty = True
                #cam_vector[0] += .25
                #print(np.degrees(np.arctan2(-cam_vector[0],dir_vector[1])))
            if event.key == K_MINUS:
                if texnum > 0:
                    texnum -= 1
                    screen_dirty = True
                #cam_vector[0] -= .25
                #print(np.degrees(np.arctan2(-cam_vector[0],dir_vector[1])))
            if event.key == K_LEFT:
                angle += (TURN_STEP)
                turned = True
                print("You turn left.")
            if event.key == K_RIGHT:
                angle -= (TURN_STEP)
                turned = True
                print("You turn right.")
            if event.key == K_UP:
                new_pos_vector = np.add(pos_vector,dir_vector)
                if tryMove(pos_vector,dir_vector):
                    print("You step forwards.")
                    pos_vector = new_pos_vector
                    moved = True
                else:
                    print("You bump into something!")
            if event.key == K_DOWN:
                new_pos_vector = np.subtract(pos_vector,dir_vector)
                if tryMove(pos_vector,dir_vector):
                    print("You step forwards.")
                    pos_vector = new_pos_vector
                    moved = True
                else:
                    print("You bump into something!")
            if event.key == K_b:
                globals.render_thin = not globals.render_thin
                print(f"RENDER_THIN set to {globals.render_thin}")
                screen_dirty = True
            if event.key == K_t:
                globals.render_textured = not globals.render_textured
                print(f"RENDER_TEXTURED set to {globals.render_textured}")
                screen_dirty = True
            if event.key == K_d:
                demo = not demo
                print(f"")
            if event.key == K_s:
                globals.shading = not globals.shading
                print(f"shading set to {globals.shading}")
                screen_dirty = True
        
    if demo:
        angle += .05
        turned = True

    if turned:
        c = np.cos(angle)
        s = np.sin(angle)
        rotation = np.array([[c,-s],[s,c]])
        dir_vector = np.matmul(dir_vector, rotation)
        cam_vector = np.matmul(cam_vector, rotation)
        screen_dirty = True
    
    mapCell = (int(np.floor(pos_vector[0])), int(np.floor(pos_vector[1])))

    if (turned and not demo) or moved:
        print(f"You are at {pos_vector} in cell {mapCell} and are facing {vectorToCompass(dir_vector)}.")
        print(f"There are walls to the: {maze.getWalls(mapCell[0],mapCell[1])}")
        turned = False
        moved = False
        screen_dirty = True
    
    if screen_dirty:
        view = raycast.rayCast(pos_vector, dir_vector, cam_vector, maze, wall_textures)
        screen.blit(view,(0,0))
        pygame.display.flip()
        screen_dirty = False
    
    clock.tick(60)

    