import globals
import pygame
import math
from pygame.locals import *
import numpy as np

# hide divide by zero errors
# numpy returns infinity when we divide by zero
# and that works within our algorithm fine
np.seterr(divide='ignore')


def rayCast(pv, dv, cv, maze, wall_textures):
    # adapted from the excellent tutorial at https://lodev.org/cgtutor/raycasting.html
    
    view = pygame.Surface((globals.VIEW_WIDTH,globals.VIEW_HEIGHT))

    # create an array equal to the size of our view surface
    # letting numpy copy between arrays is pretty fast
    # so we want to use that as much as possible

    strips_array = np.zeros([globals.VIEW_WIDTH, globals.VIEW_HEIGHT])

    # for each pixel in our view

    for viewx in range(globals.VIEW_WIDTH):
        column = 2 * viewx / globals.VIEW_WIDTH - 1
        raydir = dv + cv * column
        
        dist_delta = abs(1 / raydir)
        step = np.array([0,0])
        side_dist = np.array([np.inf, np.inf])
        map_cell = np.array([math.floor(pv[0]), math.floor(pv[1])])
        
        if raydir[0] < 0:
            step[0] = -1
            side_dist[0] = (pv[0] - map_cell[0]) * dist_delta[0]
        else:
            step[0] = 1
            side_dist[0] = (map_cell[0] + 1 - pv[0]) * dist_delta[0]

        if raydir[1] < 0:
            step[1] = -1
            side_dist[1] = (pv[1] - map_cell[1]) * dist_delta[1]
        else:
            step[1] = 1
            side_dist[1] = (map_cell[1] + 1 - pv[1]) * dist_delta[1]

        wallhit = False

        while not wallhit:
            if side_dist[0] < side_dist[1]:
                side_dist[0] += dist_delta[0]
                map_cell[0] += step[0]
                side = 0
            else:
                side_dist[1] += dist_delta[1]
                map_cell[1] += step[1]
                side = 1

            cell = None

            # thin wall rendering
            if globals.render_thin:
                if side == 0:
                    if step[0] < 0: # the ray is traveling west
                        cell = maze.getCell(map_cell[0] + 1, map_cell[1])
                        wallhit |= cell & globals.WALL_W
                    else: # the ray is traveling east
                        cell = maze.getCell(map_cell[0] - 1, map_cell[1])
                        wallhit |= cell & globals.WALL_E
                else:
                    if step[1] < 0: # the ray is traveling north
                        cell = maze.getCell(map_cell[0], map_cell[1] + 1)
                        wallhit |= cell & globals.WALL_N
                    else: # the ray is traveling south
                        cell = maze.getCell(map_cell[0], map_cell[1] - 1)
                        wallhit |= cell & globals.WALL_S

            #block-based rendering
            else:
                cell = maze.getCell(map_cell[0], map_cell[1])
                if cell != 0: wallhit = True

        if side == 0:
            perpwall_dist = side_dist[0] - dist_delta[0]
        else:
            perpwall_dist = side_dist[1] - dist_delta[1]

        lineheight = int(globals.VIEW_HEIGHT / perpwall_dist) if perpwall_dist !=0 else int(globals.VIEW_HEIGHT)
        
        if globals.render_textured:
            texture = wall_textures[cell >> 5]

            #texturing calculations

            if side == 0:
                wallx = pv[1] + perpwall_dist * raydir[1]
            else:
                wallx = pv[0] + perpwall_dist * raydir[0]
            
            wallx -= np.floor(wallx)

            #x coordinate on the texture
            texturex = int(wallx * globals.TEXTURE_WIDTH)

            if side == 0 and raydir[0] > 0:
                texturex = globals.TEXTURE_WIDTH - texturex - 1
            if side == 1 and raydir[1] < 0:
                texturex = globals.TEXTURE_WIDTH - texturex - 1

            #optimize this
            
            # if stripheight is larger than VIEW_HEIGHT we setup an offset into the texture
            # so that we don't end up trying to draw stuff that'll end up off screen.
            
            stripheight = globals.VIEW_HEIGHT if lineheight > globals.VIEW_HEIGHT else lineheight
            strip_offset = (lineheight - stripheight) // 2
            
            # t_step is how many pixels we move down our source texture for every pixel we move down the screen
            # it will be > 1 if the texture is being rendered smaller than its native size
            # it will be < 1 if the texture is being rendered greater than its native size
            t_step = globals.TEXTURE_HEIGHT / lineheight
            
            shade = 2 if globals.shading else 1
            
            for viewy in range(stripheight):
                if side == 0:
                    strips_array[viewx,viewy + (globals.VIEW_HEIGHT - stripheight) // 2] = texture[texturex,int((viewy + strip_offset) * t_step)] // shade
                else:
                    strips_array[viewx,viewy + (globals.VIEW_HEIGHT - stripheight) // 2] = texture[texturex,int((viewy + strip_offset) * t_step)]

        # untextured renderer
        else:
            if globals.shading:
                shade = pygame.Color(2,2,2)
            else:
                shade = pygame.Color(1,1,1)
            if side == 0:
                if cell & globals.WALL_OOB:
                    pygame.draw.line(view, pygame.Color('red') // shade, (viewx, -lineheight / 2 + globals.VIEW_HEIGHT / 2), (viewx, lineheight / 2 + globals.VIEW_HEIGHT / 2))
                else:
                    pygame.draw.line(view, pygame.Color('green') // shade, (viewx, -lineheight / 2 + globals.VIEW_HEIGHT / 2), (viewx, lineheight / 2 + globals.VIEW_HEIGHT / 2))
            else:
                if cell & globals.WALL_OOB:
                    pygame.draw.line(view, pygame.Color('red'), (viewx, -lineheight / 2 + globals.VIEW_HEIGHT / 2), (viewx, lineheight / 2 + globals.VIEW_HEIGHT / 2))
                else:
                    pygame.draw.line(view, pygame.Color('green'), (viewx, -lineheight / 2 + globals.VIEW_HEIGHT / 2), (viewx, lineheight / 2 + globals.VIEW_HEIGHT / 2))
    
    if globals.render_textured:
        pygame.surfarray.blit_array(view,strips_array)

    return view
