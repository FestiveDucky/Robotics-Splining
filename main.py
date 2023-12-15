from itertools import chain

import pygame

from obstacles import *
from drawing import *
from constants import *
from random import randint as ri

from pointsConverter import converter
from robot import *


# Obstacles backup: 913 1489 914 305 881 306 883 1492 1210 1491 585 1488 585 1488 585 1517 585 1517 1208 1520 1208 1520 1210 1494 580 278 1211 278 1211 274 1210 307 1209 305 582 306 582 306 583 278 0 1199 295 1203 295 1203 295 595 295 595 0 596 1 294 307 0 1797 306 1489 0 1799 1491 1487 1799 312 1799 1 1493 1503 596 1505 1200 1505 1200 1797 1201 1503 597 1797 593
# TODO change obstacles color
# TODO Add text which notifies of collision (sometimes unknown)
# TODO (ROBOTSIM) change animate to robot simulation, add calculate estimated time of robot travel
# Maybe make sure aligned vertices are always within the screen


def saveSpline(newTab):
    newRobotData = menu.getRobotValues()
    splines[splineTab] = [newRobotData[0], newRobotData[1], c.points[:], newRobotData[2]]
    with open("save.txt", "w") as f:
        # We write out the height so that we can rescale the points for different resolutions
        f.write(str(HEIGHT) + "\n")
        f.write(" ".join(list(map(str, list(chain.from_iterable(obstaclesPoints))))) + "\n")
        f.write(f"{newTab} {len(splines)}\n")
        for spline in splines:
            f.write(f"{spline[0][0]} {spline[0][1]} {spline[1]} {spline[3]}\n")
            f.write(" ".join(list(map(str, list(chain.from_iterable(spline[2]))))) + "\n")


def loadNewSpline():
    # If new tab, generate new spline data
    if splineTab > len(splines) - 1:
        ps = [(HEIGHT * 5 / 32, HEIGHT * 7 / 8), (ri(100, HEIGHT), ri(100, HEIGHT - 100)),
                  (ri(100, HEIGHT), ri(100, HEIGHT - 100)), (ri(100, HEIGHT), ri(100, HEIGHT - 100))]
        splines.append([(0, 0), 0, ps, f"spline{splineTab}"])

    # Get rest of spline data
    ps = splines[splineTab][2]
    curve = Curve(ps, gamedisplay, precision)
    menu.setRobotValues((splines[splineTab][0], splines[splineTab][1], splines[splineTab][3]))
    return curve



if __name__ == '__main__':
    # Titles the game
    pygame.display.set_caption('Spline Generator')
    clock = pygame.time.Clock()

    show_segments = True
    show_mid_line = False
    draw_lerps = False
    draw_curve = True
    draw_points = False
    draw_circle = False
    draw_vectors = False
    draw_bounding_boxes = False
    hide_points = False
    evenly_spaced = False
    values = [draw_lerps, show_segments, show_mid_line, draw_points, draw_curve, draw_circle, draw_vectors,
              draw_bounding_boxes, hide_points, evenly_spaced]

    obstacleGroup = pygame.sprite.Group()
    obstaclesPoints = []
    obstacleClasses = []

    splines = []

    # Load data from file
    with open("save.txt", "r") as f:
        originalRes = float(f.readline())
        # Load the obstacles
        obstacles = f.readline().split()
        for i in range(1, len(obstacles), 2):
            coord = (float(obstacles[i - 1])/originalRes * HEIGHT, float(obstacles[i])/originalRes * HEIGHT)
            obstaclesPoints.append(coord)
            if len(obstaclesPoints) % 2 == 0:
                obstacleClasses.append(Obstacle(obstacleGroup, obstaclesPoints[-2], coord))
        # Read in tab number and number of splines
        splineTab, numSplines = f.readline().split()
        splineTab = int(splineTab)
        numSplines = int(numSplines)
        for j in range(numSplines):
            splinePoints = []

            # Read in robot values and spline name
            rx, ry, rangle, name = f.readline().split()

            # Load all the splines with respective robot values
            pointValues = f.readline().split()
            for i in range(1, len(pointValues), 2):
                splinePoints.append((float(pointValues[i - 1])/originalRes * HEIGHT, float(pointValues[i])/originalRes * HEIGHT))

            splines.append([(float(rx), float(ry)), float(rangle), splinePoints, name])

    # Initialization of classes
    menu = Menu(gamedisplay, WIDTH, HEIGHT, values, (86/288)*HEIGHT)
    # r = Robot(c.points[0])

    c = loadNewSpline()

    # Setting up the display
    gamedisplay.fill((14, 25, 36))
    gamedisplay.blit(bg, (0, 0))
    c.draw(draw_points, draw_curve, False, 0, False, show_segments, show_mid_line, False, draw_bounding_boxes,
           hide_points, obstacleClasses, evenly_spaced)
    c.updatePoints()
    menu.draw(c.arcLength, splineTab)
    obstacleGroup.update(gamedisplay)
    pygame.display.update()

    # Creating base variables
    FPS = 120
    gameRunning = True
    moving_point = None
    mousePos = (0, 0)
    # Starting the game loop
    while gameRunning:
        clock.tick(FPS)

        update = False

        # Checking events
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                gameRunning = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mousex, mousey = e.pos

                pointsClicked = c.getPointsClicked(mousex, mousey)
                if len(pointsClicked) > 0:
                    pointsClicked[0].selected = True
                    moving_point = pointsClicked[0]

                buttonsClicked = menu.getButtonsClicked(mousex, mousey)
                if len(buttonsClicked) > 0:
                    buttonsClicked[0].pressed()
                    values = menu.getValues()
                    draw_lerps, show_segments, show_mid_line, draw_points, draw_curve, draw_circle, draw_vectors, draw_bounding_boxes, hide_points, evenly_spaced = values

                    update = True

                textBoxesClicked = menu.getTextBoxesClicked(mousex, mousey)
                if len(textBoxesClicked) > 0:
                    if textBoxesClicked[0] == menu.text_boxes[2]:
                        textBoxesClicked[0].typing(False)
                    else:
                        textBoxesClicked[0].typing(True)
                    coordinates = textBoxesClicked[0].getTypedValues()
                    update = True

            elif e.type == pygame.MOUSEMOTION:
                mousex, mousey = e.pos
                mousePos = e.pos
                if moving_point is not None:
                    # Make sure the point is within the bounds of the background
                    mousex = max(min(HEIGHT, mousex), 0)
                    mousey = max(min(HEIGHT, mousey), 0)

                    old_pos = moving_point.getCoords()
                    vector = (mousex - old_pos[0], mousey - old_pos[1])
                    moving_point.setCoords((mousex, mousey))

                    if not moving_point.alive():
                        moving_point = None
                    else:
                        c.allignSegments(moving_point, vector)
                    update = c.setPoints()


            elif e.type == pygame.MOUSEBUTTONUP:
                if moving_point is not None:
                    moving_point.selected = False
                    moving_point = None
                if not hide_points:
                    c.updatePoints()
                update = True
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_a:
                    c.draw(draw_points, draw_curve, draw_lerps, speed, draw_circle, show_segments, show_mid_line,
                           draw_vectors, draw_bounding_boxes, hide_points, obstacleClasses, evenly_spaced)
                    update = True
                elif e.key == pygame.K_p and mousePos[0] < HEIGHT and mousePos[1] < HEIGHT:
                    midpoint = ((mousePos[0] + c.points[-1][0]) / 2, (mousePos[1] + c.points[-1][1]) / 2)
                    scale = int((WIDTH + HEIGHT) / 20)

                    # Generates two points a random scale distance away from the midpoint of the curve
                    # The max and min values make sure the points are on the screen
                    point1 = (max(min(ri(-scale, scale) + midpoint[0], HEIGHT), 0),
                              max(min(ri(-scale, scale) + midpoint[1], HEIGHT), 0))
                    point2 = (max(min(ri(-scale, scale) + midpoint[0], HEIGHT), 0),
                              max(min(ri(-scale, scale) + midpoint[1], HEIGHT), 0))

                    c.addCurve([point1, point2, mousePos])
                    c.allignSegments(c.point_classes[-3], (0, 0))
                    update = c.setPoints()
                # elif e.key == pygame.K_m:
                #     # Move robot
                #     values = c.draw(False, False, False, 0, False, False, False, False, False,
                #                     False, [], evenly_spaced)
                #     # Prints out stored derivatives
                #     d = []
                #     for curve in c.curves:
                #         d += curve.derivatives[:]
                #
                #     # Max derivative 1 x value, ...
                #     md1x, md1y, md2x, md2y = 0, 0, 0, 0
                #     for d1 in d[0]:
                #         md1x = max(md1x, abs(d1[0]))
                #         md1y = max(md1y, abs(d1[1]))
                #     for d2 in d[1]:
                #         md2x = max(md2x, abs(d2[0]))
                #         md2y = max(md2y, abs(d2[1]))
                #
                #     if md1x == 0: md1x = 1
                #     if md1y == 0: md1y = 1
                #     if md2x == 0: md2x = 1
                #     if md2y == 0: md2y = 1
                #
                #     # Compress them
                #     # for d1 in d[0]:
                #     #     print(round(d1[0] / md1x, 3), round(d1[1] / md1y, 3))
                #     accelerations = []
                #     for d2 in d[1]:
                #         accelerations.append((round(d2[0] / md2x, 3), round(d2[1] / md2y, 3)))
                #
                #     r.animate(gamedisplay, 4000, accelerations, values, menu, c)

                elif e.key == pygame.K_r:
                    c.removeCurve()
                    update = True
                elif e.key == pygame.K_UP:
                    speed += 0.01
                elif e.key == pygame.K_DOWN and speed > 0.01:
                    speed -= 0.01
                elif e.key == pygame.K_LEFT and splineTab > 0:
                    saveSpline(splineTab - 1)
                    splineTab -= 1
                    c = loadNewSpline()
                    update = True
                elif e.key == pygame.K_RIGHT:
                    saveSpline(splineTab + 1)
                    splineTab += 1
                    c = loadNewSpline()
                    update = True
                elif e.key == pygame.K_SPACE:
                    update = True
                elif e.key == pygame.K_o and mousePos[0] < HEIGHT and mousePos[1] < HEIGHT:
                    obstaclesPoints.append(mousePos)
                    if len(obstaclesPoints) % 2 == 0:
                        obstacleClasses.append(Obstacle(obstacleGroup, obstaclesPoints[-2], mousePos))
                    update = True
                elif e.key == pygame.K_DELETE:
                    obstaclesPoints.pop()
                    if len(obstaclesPoints) % 2 != 0:
                        obstacleClasses.pop().kill()
                    update = True
                elif e.key == pygame.K_e:
                    # Export points to a file
                    c.calculate(obstacleClasses)
                    if evenly_spaced:
                        c.equallySpace(obstacleClasses)
                    coordinates, curvatures = c.getData()
                    with open("points.txt", "w") as fout:
                        # Get the first point (robot start) and make the rest of the points based of that
                        start = c.points[0]

                        for i in range(len(coordinates)):
                            fout.write(
                                f"{round((start[1] - coordinates[i][1]) / PPI, 3)} {round((start[0] - coordinates[i][0]) / PPI, 3)} {round(curvatures[i] / PPI, 3)}\n")
                    converter(menu.getRobotValues())
                elif e.key == pygame.K_s:
                    saveSpline(splineTab)

        # Drawing to the screen
        if update:
            # This fill is needed for points that cross over edge of image
            gamedisplay.fill((14, 25, 36), pygame.Rect((HEIGHT, 0, LINE_THICKNESS * 2, HEIGHT)))
            gamedisplay.blit(bg, (0, 0))

            c.draw(draw_points, draw_curve, False, 0, False, show_segments, show_mid_line, False, draw_bounding_boxes,
                   hide_points, obstacleClasses, evenly_spaced)
            menu.draw(c.arcLength, splineTab)
            obstacleGroup.update(gamedisplay)

            if not hide_points:
                c.updatePoints()

            # gamedisplay.blit(r.move(), r.rect)
        # Updating the display
        pygame.display.update()
