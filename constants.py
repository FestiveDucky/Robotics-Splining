import pygame,ctypes
from PIL import Image
from math import *
import pygame.gfxdraw

pygame.init()

fullscreen = False

# Automatically resizes everything for you
ctypes.windll.user32.SetProcessDPIAware()
WIDTH, HEIGHT = pygame.display.list_modes()[0]

# Will bug out on a resolution with a ratio less than 1.3:1

image = Image.open('VEXOverUnder.png')
new_image = image.resize((HEIGHT, HEIGHT))
new_image.save(f'VEXOverUnder_{HEIGHT}.png')

if fullscreen:
    gamedisplay = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
else:
    gamedisplay = pygame.display.set_mode((WIDTH, HEIGHT))

bg = pygame.transform.smoothscale(pygame.image.load(f"VEXOverUnder_{HEIGHT}.png").convert(), (HEIGHT, HEIGHT))

# Constants
FIELD_DIMENSION = 12
# Convert it into inches
FIELD_DIMENSION *= 12
# IMAGE MUST BE A SQUARE

# Pixels per inch
PPI = HEIGHT / FIELD_DIMENSION
TRACKWIDTH = 18
WHEELRADIUS = 1
precision = 100
# speed = 0
speed = 0.005

colors = [(217, 15, 73), (182, 158, 60), (13, 192, 128)]

LINE_COLOR = (42, 150, 204)
LINE_THICKNESS = HEIGHT/720


def pointOnLine(p1, p2, t):
    return (p2[0] - p1[0]) * t + p1[0], (p2[1] - p1[1]) * t + p1[1]


def drawThickLine(display, color, p1, p2):
    # Not my code, found on the internet to draw thicker lines
    center_L1 = pointOnLine(p1, p2, 0.5)
    length = dist(p1, p2)
    thickness = LINE_THICKNESS
    angle = atan2(p1[1] - p2[1], p1[0] - p2[0])
    UL = (center_L1[0] + (length / 2.) * cos(angle) - (thickness / 2.) * sin(angle),
          center_L1[1] + (thickness / 2.) * cos(angle) + (length / 2.) * sin(angle))
    UR = (center_L1[0] - (length / 2.) * cos(angle) - (thickness / 2.) * sin(angle),
          center_L1[1] + (thickness / 2.) * cos(angle) - (length / 2.) * sin(angle))
    BL = (center_L1[0] + (length / 2.) * cos(angle) + (thickness / 2.) * sin(angle),
          center_L1[1] - (thickness / 2.) * cos(angle) + (length / 2.) * sin(angle))
    BR = (center_L1[0] - (length / 2.) * cos(angle) + (thickness / 2.) * sin(angle),
          center_L1[1] - (thickness / 2.) * cos(angle) - (length / 2.) * sin(angle))

    pygame.gfxdraw.aapolygon(display, (UL, UR, BR, BL), color)
    pygame.gfxdraw.filled_polygon(display, (UL, UR, BR, BL), color)


def events(nested=False):
    while True:
        ev = pygame.event.get()
        for e in ev:
            if e.type == pygame.QUIT:
                pygame.quit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    if not nested:
                        return events(True)
                    else:
                        return False
                elif e.key == pygame.K_c:
                    return True
        if not nested:
            return False


def calculateAngle(p1, p2):
    # p1 is your point, p2 is other point
    # First value of coordinate needs to be y value and second value needs to be x value
    angle = degrees(atan2(p2[0] - p1[0], p2[1] - p1[1]))
    if angle < 0:
        angle += 360
    return angle


def minAngleBetweenAngles(a1, a2):
    # Angles must be between 0 - 359, a1 is your angle
    # Returned sign indicates whether the shortest angle is clockwise (+) or ccw (-)

    largerAngle = max(a1, a2)
    smallerAngle = min(a1, a2)
    dist = largerAngle - smallerAngle
    sign = 1
    if dist > 180:
        sign *= -1
        dist = 360 - dist
    if largerAngle == a1:
        sign *= -1

    return dist * sign
