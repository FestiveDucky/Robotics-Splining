from itertools import chain
from random import randint as ri

from drawing import *
from eventGUI import *
from obstacles import *
from pointsConverter import converter
from robot import *


# Obstacles backup: 913 1489 914 305 881 306 883 1492 1210 1491 585 1488 585 1488 585 1517 585 1517 1208 1520 1208 1520 1210 1494 580 278 1211 278 1211 274 1210 307 1209 305 582 306 582 306 583 278 0 1199 295 1203 295 1203 295 595 295 595 0 596 1 294 307 0 1797 306 1489 0 1799 1491 1487 1799 312 1799 1 1493 1503 596 1505 1200 1505 1200 1797 1201 1503 597 1797 593
# TODO make sure aligned vertices are always within the screen
# TODO make menu settings be saved
# add ability to have back to back independent splines

def saveSpline(newTab):
    newRobotData = menu.getRobotValues()
    splines[splineTab] = [newRobotData[0], newRobotData[1], c.points[:], newRobotData[2], splines[splineTab][4][:], [curve.isLine for curve in c.curves], [curve.reversed for curve in c.curves]]
    with open("save.txt", "w") as f:
        # We write out the height so that we can rescale the points for different resolutions
        f.write(str(HEIGHT) + "\n")
        f.write(" ".join(list(map(str, list(chain.from_iterable(obstaclesPoints))))) + "\n")
        f.write(f"{newTab} {len(splines)}\n")
        for spline in splines:
            f.write(f"{spline[0][0]} {spline[0][1]} {spline[1]} {spline[3]}\n")
            f.write(" ".join(list(map(str, list(chain.from_iterable(spline[2]))))) + "\n")
            f.write(" ".join(list(map(str, list(chain.from_iterable(spline[4]))))) + "\n")
            f.write(" ".join(list(map(str, spline[5]))) + "\n")
            f.write(" ".join(list(map(str, spline[6]))) + "\n")


def loadNewSpline():
    # If new tab, generate new spline data
    if splineTab > len(splines) - 1:
        ps = [(HEIGHT * 5 / 32, HEIGHT * 7 / 8), (ri(100, HEIGHT), ri(100, HEIGHT - 100)),
              (ri(100, HEIGHT), ri(100, HEIGHT - 100)), (ri(100, HEIGHT), ri(100, HEIGHT - 100))]
        splines.append([(0, 0), 0, ps, f"spline{splineTab}", [], [False], [False]])

    # Get rest of spline data
    ps = splines[splineTab][2]
    curve = Curve(ps, gamedisplay, precision, splines[splineTab][5], splines[splineTab][6])
    menu.setRobotValues((splines[splineTab][0], splines[splineTab][1], splines[splineTab][3]))

    robotEventClasses.clear()
    robotEventGroup.empty()
    curve.calculate(obstacleClasses)
    curvePoints = curve.getData()[0]
    for rEvent in splines[splineTab][4]:
        robotEventClasses.append(RobotEvent(robotEventGroup, curvePoints[rEvent[0]], rEvent[1], (86 / 288) * HEIGHT, rEvent[0]))

    return curve


if __name__ == '__main__':
    # Titles the game
    pygame.display.set_caption('Auton Generator')
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
    generate_auton = False
    values = [draw_lerps, show_segments, show_mid_line, draw_points, draw_curve, draw_circle, draw_vectors,
              draw_bounding_boxes, hide_points, evenly_spaced, generate_auton]

    obstacleGroup = pygame.sprite.Group()
    obstaclesPoints = []
    obstacleClasses = []

    robotEventGroup = pygame.sprite.Group()
    robotEventClasses = []

    splines = []

    # Load data from file
    with open("save.txt", "r") as f:
        originalRes = float(f.readline())
        # Load the obstacles
        obstacles = f.readline().split()
        for i in range(1, len(obstacles), 2):
            coord = (float(obstacles[i - 1]) / originalRes * HEIGHT, float(obstacles[i]) / originalRes * HEIGHT)
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
                splinePoints.append(
                    (float(pointValues[i - 1]) / originalRes * HEIGHT, float(pointValues[i]) / originalRes * HEIGHT))

            # Load events
            splineEvents = []
            eventData = f.readline().split()
            for i in range(1, len(eventData), 2):
                splineEvents.append((int(eventData[i - 1]), int(eventData[i])))

            # Load lines
            lines = list(map(lambda x: x == "True", f.readline().split()))
            # Load reversed curves
            reversedCurves = list(map(lambda x: x == "True", f.readline().split()))


            splines.append([(float(rx), float(ry)), float(rangle), splinePoints, name, splineEvents, lines, reversedCurves])

    # Initialization of classes
    menu = Menu(gamedisplay, WIDTH, HEIGHT, values, (86 / 288) * HEIGHT)
    c = loadNewSpline()

    r = Robot(c.points[0])

    # Setting up the display
    gamedisplay.fill((14, 25, 36))
    gamedisplay.blit(bg, (0, 0))
    c.draw(draw_points, draw_curve, False, 0, False, show_segments, show_mid_line, False, draw_bounding_boxes,
           hide_points, obstacleClasses, evenly_spaced)
    c.updatePoints()
    menu.draw(c.arcLength, splineTab)
    obstacleGroup.update(gamedisplay)
    robotEventGroup.update()
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
                    draw_lerps, show_segments, show_mid_line, draw_points, draw_curve, draw_circle, draw_vectors, draw_bounding_boxes, hide_points, evenly_spaced, generate_auton = values

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

                    c.setPoints()
                    update = True

                    # Update event positions based on new point positions
                    c.calculate(obstacleClasses)
                    points = c.getData()[0]
                    for rEvent in robotEventClasses:
                        rEvent.setCoords(points[rEvent.index])
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
                # Pygame key values for number from 1 - 7
                elif e.key in [49, 50, 51, 52, 53, 54, 55]:
                    mousePos = pygame.mouse.get_pos()
                    nearestPoint = [None, 10000000, -1]
                    for i, splinePoint in enumerate(c.getData()[0]):
                        dist = math.dist(splinePoint, mousePos)
                        if dist < nearestPoint[1]:
                            nearestPoint = [splinePoint, dist, i]
                    splines[splineTab][4].append((nearestPoint[2], e.key - 48))
                    robotEventClasses.append(
                        RobotEvent(robotEventGroup, nearestPoint[0], e.key - 48, (86 / 288) * HEIGHT, nearestPoint[2]))
                    update = True
                elif e.key == pygame.K_k:
                    mousePos = pygame.mouse.get_pos()
                    nearestPoint = [None, 10000000, -1]
                    for i, splinePoint in enumerate(c.getData()[0]):
                        dist = math.dist(splinePoint, mousePos)
                        if dist < nearestPoint[1]:
                            nearestPoint = [splinePoint, dist, i]
                    c.curves[nearestPoint[2]//(precision + 1)].toggleDirection()
                    update = True

                elif e.key == pygame.K_0 and len(robotEventClasses) != 0:
                    # Find closest point
                    mousePos = pygame.mouse.get_pos()
                    nearestPoint = [None, 10000000, -1]
                    for i, event in enumerate(robotEventClasses):
                        dist = math.dist(event.coords, mousePos)
                        if dist < nearestPoint[1]:
                            nearestPoint = [event.coords, dist, i]

                    splines[splineTab][4].pop(nearestPoint[2])
                    robotEventClasses.pop(nearestPoint[2]).kill()
                    update = True
                elif e.key == pygame.K_t:
                    r.manualMove(c.points[0])
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

                    c.setPoints()
                    update = True

                    # Update event positions based on new point positions
                    c.calculate(obstacleClasses)
                    points = c.getData()[0]
                    for rEvent in robotEventClasses:
                        rEvent.setCoords(points[rEvent.index])
                elif e.key == pygame.K_l and mousePos[0] < HEIGHT and mousePos[1] < HEIGHT:
                    c.addCurve([c.points[-1], mousePos, mousePos], True)
                    update = True
                elif e.key == pygame.K_r:
                    c.removeCurve()
                    toRemove = []
                    c.calculate(obstacleClasses)
                    amountOfSplinePoints = len(c.getData()[0])
                    for i, event in enumerate(robotEventClasses):
                        if event.index >= amountOfSplinePoints:
                            toRemove.append(i)

                    toRemove = sorted(toRemove, reverse=True)
                    for removal in toRemove:
                        splines[splineTab][4].pop(removal)
                        robotEventClasses.pop(removal).kill()
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
                    saveSpline(splineTab)

                    exportedPoints = []
                    # Get the first point (robot start) and make the rest of the points based of that
                    start = c.points[0]

                    for i in range(len(coordinates)):
                        exportedPoints.append((round((start[1] - coordinates[i][1]) / PPI, 3), round((start[0] - coordinates[i][0]) / PPI, 3), None if curvatures[i] is None else round(curvatures[i] / PPI, 3)))
                    converter(menu.getRobotValues(), splines[splineTab], exportedPoints, not generate_auton)
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
            robotEventGroup.update()

            if not hide_points:
                c.updatePoints()

        # Updating the display
        pygame.display.update()
