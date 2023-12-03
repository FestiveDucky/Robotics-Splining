import math
from constants import *
from button import *
import pygame, pygame.gfxdraw, time


# colors = [(230, 25, 75), (245, 130, 48), (255, 225, 25), (210, 245, 60), (60, 180, 75), (70, 240, 240), (0, 130, 200),
#           (145, 30, 180),
#           (240, 50, 230)]


class Point(pygame.sprite.Sprite):
    def __init__(self, coords, group):
        super().__init__(group)
        self.coords = coords
        self.selected = False
        self.size = (HEIGHT/72)
        self.rect = pygame.Rect(self.coords[0] - self.size / 2, self.coords[1] - self.size / 2, self.size, self.size)

    def update(self, display, special=False):
        if not special:
            if self.selected:
                pygame.draw.circle(display, (0, 255, 0), self.coords, LINE_THICKNESS * 2)
            else:
                pygame.draw.circle(display, (255, 255, 255), self.coords, LINE_THICKNESS * 2)
        else:
            pygame.draw.circle(display, colors[0], self.coords, LINE_THICKNESS * 2)

    def setCoords(self, coords):
        self.coords = coords
        self.rect = pygame.Rect(self.coords[0] - 10, self.coords[1] - 10, 20, 20)

    def getCoords(self):
        return self.coords


class CubicBezierCurve:
    def __init__(self, points, display):
        assert len(points) == 4
        self.points = []
        self.display = display
        self.point_group = pygame.sprite.LayeredUpdates()
        self.point_classes = points
        self.arcLength = 0
        # First, Second
        self.data = {"t": [], "points": [], "firstDerivatives": [], "secondDerivatives": [], "curvatures": [],
                     "normalVectorPoints": []}
        self.collidesWithObstacles = False

        self.setNewPoints()

    def drawLerps(self, t, points, drawLines, total_points, animation):
        new_points = []
        for i in range(len(points) - 1):
            # Drawing the lerps
            if drawLines:
                drawThickLine(self.display, colors[abs(len(points) - total_points)], points[i], points[i + 1])

                # Drawing the points on the lines
                pygame.draw.circle(self.display, colors[abs(len(points) - total_points)], points[i], LINE_THICKNESS * 2)

            # Saving the new point
            new_points.append(pointOnLine(points[i], points[i + 1], t))

        # Drawing the extra point we missed
        if drawLines:
            pygame.draw.circle(self.display, colors[abs(len(points) - total_points)], points[-1], LINE_THICKNESS * 2)

        if len(new_points) != 1:
            # Running again until we reach the final point
            return self.drawLerps(t, new_points, drawLines, total_points, animation)
        # Draw the final point
        if animation:
            pygame.draw.circle(self.display, LINE_COLOR, new_points[0], LINE_THICKNESS * 2)
        return new_points[0]

    def animate(self, precision, drawPoints, drawCurve, drawLerps, pause, drawCircle, drawVectors,
                hidePoints, obstacles, redrawCurves=None, pointG=None, tValues=None):
        if tValues is None:
            tValues = list(map(lambda x: x / precision, range(precision + 1)))
        if redrawCurves is None:
            redrawCurves = []
        for i, t in enumerate(tValues):
            if pause != 0:
                events()

                pygame.display.update()
                time.sleep(pause)
                if i != precision:
                    self.display.fill((14, 25, 36))

            p = self.drawLerps(t, self.points, drawLerps, len(self.points), pause != 0)
            d1 = self.data["firstDerivatives"][i]
            d2 = self.data["secondDerivatives"][i]
            r = self.data["curvatures"][i]
            p4, p5 = self.data["normalVectorPoints"][i]
            if pause != 0:
                self.reDraw(i, drawCurve, drawPoints)
                for c in redrawCurves:
                    # c.calculateBezierCurve(precision, [])
                    c.animate(precision, drawPoints, drawCurve, False, 0, False, False, hidePoints, [], pointG=pointG)
            if (drawLerps or not hidePoints) and pointG is not None and pause != 0:
                pointG.update(self.display, drawLerps)

            if drawCircle and r is not None:
                # Circle on inside
                d1 = (-d1[1] + p[0], d1[0] + p[1])
                # Circle on outside
                # d1 = (d1[1] + p[0], -d1[0] + p[1])
                d = r / math.dist(p, d1)
                p1 = ((1 - d) * p[0] + d * d1[0], (1 - d) * p[1] + d * d1[1])
                pygame.draw.circle(self.display, LINE_COLOR, p1, abs(r), width=1)

            if drawVectors:
                p2 = (d1[0] * 0.2 + p[0], d1[1] * 0.2 + p[1])
                p3 = (d2[0] * 0.05 + p2[0], d2[1] * 0.05 + p2[1])

                drawThickLine(self.display, (134, 30, 63), p, p2)
                drawThickLine(self.display, (98, 44, 156), p2, p3)
                drawThickLine(self.display, (134, 30, 63), p, p4)
                drawThickLine(self.display, (134, 30, 63), p, p5)

            # Determines if the line is too close to obstacles which would cause the bot to hit them
            color = LINE_COLOR
            for obstacle in obstacles:
                if obstacle.calculateIntersection(p4, p5):
                    color = (255, 255, 0)
                    break

            if i != 0 and drawCurve:
                drawThickLine(self.display, color, self.data["points"][i - 1], self.data["points"][i])

            if drawPoints:
                pygame.draw.circle(self.display, color, p, LINE_THICKNESS)

    def BezierPoint(self, t, points):
        new_points = []
        for i in range(len(points) - 1):
            # Saving the new point
            new_points.append(pointOnLine(points[i], points[i + 1], t))

        if len(new_points) != 1:
            # Running again until we reach the final point
            return self.BezierPoint(t, new_points)
        return new_points[0]

    def calculateBezierCurve(self, precision, obstacles, tValues=None):
        if tValues is None:
            tValues = list(map(lambda x: x / precision, range(precision + 1)))
        self.data["t"] = []
        self.data["points"] = []
        self.data["firstDerivatives"] = []
        self.data["secondDerivatives"] = []
        self.data["curvatures"] = []
        self.data["normalVectorPoints"] = []
        self.collidesWithObstacles = False
        self.arcLength = 0
        for t in tValues:
            p = self.BezierPoint(t, self.points)

            d1 = self.firstDerivative(t)
            d2 = self.secondDerivative(t)

            self.data["t"].append(t)
            self.data["points"].append(p)
            self.data["firstDerivatives"].append(d1)
            self.data["secondDerivatives"].append(d2)
            self.data["curvatures"].append(self.curvatureRadius(t))

            # Calculate normal vectors
            p4 = (-d1[1] + p[0], d1[0] + p[1])
            p5 = (d1[1] + p[0], -d1[0] + p[1])
            # Length of vector
            d11 = (TRACKWIDTH * PPI) / (math.dist(p, p4) * 2)
            d22 = (TRACKWIDTH * PPI) / (math.dist(p, p5) * 2)
            # Endpoints of normal vectors
            p4 = ((1 - d11) * p[0] + d11 * p4[0], (1 - d11) * p[1] + d11 * p4[1])
            p5 = ((1 - d22) * p[0] + d22 * p5[0], (1 - d22) * p[1] + d22 * p5[1])

            self.data["normalVectorPoints"].append((p4, p5))

            if tValues[0] != t:
                self.arcLength += math.dist(self.data["points"][-2], self.data["points"][-1])

            # Determines if the path is too close to the obstacles which would cause the bot to hit them
            for obstacle in obstacles:
                if obstacle.calculateIntersection(p4, p5):
                    self.collidesWithObstacles = True
                    break

    def reDraw(self, ind, dC, dP):
        for i in range(ind):
            if dP:
                pygame.draw.circle(self.display, LINE_COLOR, self.data["points"][i], LINE_THICKNESS)
            if dC:
                if i != 0:
                    drawThickLine(self.display, LINE_COLOR, self.data["points"][i - 1], self.data["points"][i])

    """Updates the point values of the curve if they were moved by the Curve class"""

    def setNewPoints(self):
        old_points = self.points[:]
        self.points = [point.getCoords() for point in self.point_classes]
        if old_points == self.points:
            return False
        return True

    """Calculates the second derivative at a certain t value"""

    def secondDerivative(self, t):
        final_vector = [0, 0]
        final_vector[0] += self.points[0][0] * (-6. * t + 6)
        final_vector[1] += self.points[0][1] * (-6. * t + 6)
        final_vector[0] += self.points[1][0] * (18 * t - 12)
        final_vector[1] += self.points[1][1] * (18 * t - 12)
        final_vector[0] += self.points[2][0] * (-18 * t + 6)
        final_vector[1] += self.points[2][1] * (-18 * t + 6)
        final_vector[0] += self.points[3][0] * (6 * t)
        final_vector[1] += self.points[3][1] * (6 * t)
        return tuple(final_vector)

    """Calculates the second derivative at a certain t value"""

    def firstDerivative(self, t):
        # stackoverflow.com/questions/4089443/find-the-tangent-of-a-point-on-a-bezier-curve
        final_vector = [0, 0]
        final_vector[0] += 3. * ((1 - t) ** 2) * (self.points[1][0] - self.points[0][0])
        final_vector[1] += 3. * ((1 - t) ** 2) * (self.points[1][1] - self.points[0][1])
        final_vector[0] += 6. * t * (1 - t) * (self.points[2][0] - self.points[1][0])
        final_vector[1] += 6. * t * (1 - t) * (self.points[2][1] - self.points[1][1])
        final_vector[0] += 3. * t ** 2 * (self.points[3][0] - self.points[2][0])
        final_vector[1] += 3. * t ** 2 * (self.points[3][1] - self.points[2][1])
        return tuple(final_vector)

    """Calculates the curvature at a certain t value"""

    def curvatureRadius(self, t):
        f = self.firstDerivative(t)
        s = self.secondDerivative(t)
        # numerator = abs(f[0] * s[1] - f[1] * s[0])
        numerator = f[0] * s[1] - f[1] * s[0]
        flip = False
        if numerator < 0:
            flip = True
            numerator = abs(numerator)
        denominator = ((f[0] ** 2) + (f[1] ** 2)) ** (1.5)
        if denominator == 0 or numerator == 0:
            print("Undefined Curvature (A line)")
        else:

            k = numerator / denominator
            if flip:
                return -(1. / k)
            return 1. / k

    """Calculates the bounding box of the curve"""

    def boundingBox(self, draw=True, pygameRect=False):
        xRoots = self.quadraticFormula(
            -3 * self.points[0][0] + 9 * self.points[1][0] - 9 * self.points[2][0] + 3 * self.points[3][0],
            6 * self.points[0][0] - 12 * self.points[1][0] + 6 * self.points[2][0],
            -3 * self.points[0][0] + 3 * self.points[1][0])
        yRoots = self.quadraticFormula(
            -3 * self.points[0][1] + 9 * self.points[1][1] - 9 * self.points[2][1] + 3 * self.points[3][1],
            6 * self.points[0][1] - 12 * self.points[1][1] + 6 * self.points[2][1],
            -3 * self.points[0][1] + 3 * self.points[1][1])

        t_values = [0, 1]
        if xRoots is not None:
            if 0 < xRoots[0] < 1:
                t_values.append(xRoots[0])
            if 0 < xRoots[1] < 1:
                t_values.append(xRoots[1])
        if yRoots is not None:
            if 0 < yRoots[0] < 1:
                t_values.append(yRoots[0])
            if 0 < yRoots[1] < 1:
                t_values.append(yRoots[1])

        points = [self.BezierPoint(t, self.points) for t in t_values]
        xValues = list(map(lambda x: x[0], points))
        xBounds = [max(xValues), min(xValues)]
        yValues = list(map(lambda x: x[1], points))
        yBounds = [max(yValues), min(yValues)]

        if pygameRect:
            return pygame.Rect(xBounds[1], yBounds[1], xBounds[0] - xBounds[1], yBounds[0] - yBounds[1])

        if draw:
            pygame.draw.rect(self.display, (150, 150, 150),
                             pygame.Rect(xBounds[1], yBounds[1], xBounds[0] - xBounds[1], yBounds[0] - yBounds[1]), 1)
        else:
            return xBounds + yBounds

    @staticmethod
    def quadraticFormula(a, b, c):
        if b ** 2 - 4 * a * c < 0:
            return
        d = math.sqrt(b ** 2 - 4 * a * c)
        return (-b + d) / (2 * a), (-b - d) / (2 * a)


class Curve:
    def __init__(self, points, display, precision):
        assert len(points) >= 4
        self.points = points
        self.precision = precision
        self.point_group = pygame.sprite.LayeredUpdates()
        self.point_classes = []
        self.curves = []
        for i in range(len(points)):
            self.point_classes.append(Point(points[i], self.point_group))
            if i % 3 == 0 and i != 0:
                self.curves.append(CubicBezierCurve(
                    [self.point_classes[i - 3], self.point_classes[i - 2], self.point_classes[i - 1],
                     self.point_classes[i]], display))
        self.display = display
        self.arcLength = 0

    """Recalculates all curve values including arc length"""

    def calculate(self, obstacles):
        self.arcLength = 0
        for curve in self.curves:
            curve.calculateBezierCurve(self.precision, obstacles)
            self.arcLength += curve.arcLength

    def equallySpace(self, obstacles):
        allTValues = []
        for curve in self.curves:
            interval = curve.arcLength / self.precision
            manualTValues = []
            index = 0
            distance = 0
            points = curve.data["points"]
            tValues = curve.data["t"]
            for i in range(self.precision):
                desiredPosition = interval * i
                while distance + math.dist(points[index], points[index + 1]) <= desiredPosition:
                    distance += math.dist(points[index], points[index + 1])
                    index += 1
                change = math.dist(points[index], points[index + 1])
                desiredChange = desiredPosition - distance
                tInterval = tValues[index + 1] - tValues[index]
                manualTValues.append(tValues[index] + desiredChange / change * tInterval)
            # Account for the last point
            manualTValues.append(1)
            curve.calculateBezierCurve(self.precision, obstacles, tValues=manualTValues)
            allTValues.append(manualTValues)
        return allTValues

    def draw(self, drawPoints, drawCurve, drawLerps, pause, drawCircle, drawOutline, drawMidLine, drawVectors,
             drawBoundingBoxes, hidePoints, obstacles, equallySpaced):

        self.calculate(obstacles)

        manualTValues = []
        if equallySpaced:
            manualTValues = self.equallySpace(obstacles)

        redraw_curves = []
        for i, curve in enumerate(self.curves):
            curve.animate(self.precision, drawPoints, drawCurve, drawLerps, pause, drawCircle, drawVectors,
                          hidePoints, obstacles, redrawCurves=redraw_curves, pointG=self.point_group,
                          tValues=manualTValues[i] if manualTValues else None)
            redraw_curves.append(curve)

        if drawOutline:
            self.drawOutline(drawMidLine)

        if drawBoundingBoxes:
            for curve in self.curves:
                curve.boundingBox()

    def drawOutline(self, drawMidLine):
        for i in range(len(self.points) - 1):
            if i % 3 != 1 or drawMidLine:
                drawThickLine(self.display, colors[i % 3], self.points[i], self.points[i + 1])

    def allignSegments(self, p, move):
        i = self.point_classes.index(p)
        if i % 3 == 1 and i != 1:
            otherP = self.point_classes[i - 2]
            centerP = self.point_classes[i - 1]
        elif i % 3 == 2 and i != len(self.point_classes) - 2:
            otherP = self.point_classes[i + 2]
            centerP = self.point_classes[i + 1]
        elif i % 3 == 0 and i != 0 and i != len(self.point_classes) - 1:
            # TODO make movement be blocked by poinst going off the screen
            c = self.point_classes[i - 1].getCoords()
            self.point_classes[i - 1].setCoords((c[0] + move[0], c[1] + move[1]))
            c = self.point_classes[i + 1].getCoords()
            self.point_classes[i + 1].setCoords((c[0] + move[0], c[1] + move[1]))
            return
        else:
            return

        # d = -math.dist(otherP.getCoords(), centerP.getCoords()) / math.dist(p.getCoords(), centerP.getCoords())
        # d is a percentage
        d = -1
        p2 = p.getCoords()
        p1 = centerP.getCoords()
        nextCoords = ((1 - d) * p1[0] + d * p2[0], (1 - d) * p1[1] + d * p2[1])

        # Makes sure that the mirrored point does not go off the screen
        boundedCoords = (max(min(nextCoords[0], HEIGHT), 0),
                         max(min(nextCoords[1], HEIGHT), 0))

        newSelfCoords = ((1 - d) * p1[0] + d * boundedCoords[0], (1 - d) * p1[1] + d * boundedCoords[1])

        otherP.setCoords(boundedCoords)
        p.setCoords(newSelfCoords)

    def getData(self):
        curvatures = []
        points = []
        for curve in self.curves:
            points += curve.data["points"]
            curvatures += curve.data["curvatures"]
        return points, curvatures

    def updatePoints(self):
        self.point_group.update(self.display)

    def getPointsClicked(self, mx, my):
        return self.point_group.get_sprites_at((mx, my))

    def addCurve(self, points):
        assert len(points) == 3
        for p in points:
            self.point_classes.append(Point(p, self.point_group))
        self.points += points
        self.curves.append(CubicBezierCurve(
            [self.point_classes[-4], self.point_classes[-3], self.point_classes[-2], self.point_classes[-1]],
            self.display))

    def removeCurve(self):
        if len(self.curves) > 1:
            self.arcLength -= self.curves[-1].arcLength
            self.curves.pop()
            self.point_group.remove(self.point_classes[-1])
            self.point_group.remove(self.point_classes[-2])
            self.point_group.remove(self.point_classes[-3])
            self.point_classes = self.point_classes[:-3]
            self.points = self.points[:-3]

    def setPoints(self):
        self.points = [point.getCoords() for point in self.point_classes]

        change = False
        for curve in self.curves:
            if curve.setNewPoints():
                change = True
        return change


class Menu:
    def __init__(self, display, w, h, vals, size):
        self.buttons = []
        self.display = display
        self.button_group = pygame.sprite.LayeredUpdates()
        self.size = size
        self.w = w
        self.h = h

        spread = self.size / 4
        self.buttons.append(Button(self.button_group, self.display, "Draw Lerps",
                                   (self.w - self.size + 10 * (self.size / 200), len(self.buttons) * spread + 20),
                                   vals[0], self.size))
        self.buttons.append(Button(self.button_group, self.display, "Draw Segments",
                                   (self.w - self.size + 10 * (self.size / 200), len(self.buttons) * spread + 20),
                                   vals[1], self.size))
        self.buttons.append(Button(self.button_group, self.display, "Draw Mid-Line",
                                   (self.w - self.size + 10 * (self.size / 200), len(self.buttons) * spread + 20),
                                   vals[2], self.size))
        self.buttons.append(Button(self.button_group, self.display, "Draw Points",
                                   (self.w - self.size + 10 * (self.size / 200), len(self.buttons) * spread + 20),
                                   vals[3], self.size))
        self.buttons.append(Button(self.button_group, self.display, "Draw Curve",
                                   (self.w - self.size + 10 * (self.size / 200), len(self.buttons) * spread + 20),
                                   vals[4], self.size))
        self.buttons.append(Button(self.button_group, self.display, "Draw Circle",
                                   (self.w - self.size + 10 * (self.size / 200), len(self.buttons) * spread + 20),
                                   vals[5], self.size))
        self.buttons.append(Button(self.button_group, self.display, "Draw Vectors",
                                   (self.w - self.size + 10 * (self.size / 200), len(self.buttons) * spread + 20),
                                   vals[6], self.size))
        self.buttons.append(Button(self.button_group, self.display, "Bounding Boxes",
                                   (self.w - self.size + 10 * (self.size / 200), len(self.buttons) * spread + 20),
                                   vals[7], self.size))
        self.buttons.append(Button(self.button_group, self.display, "Hide Points",
                                   (self.w - self.size + 10 * (self.size / 200), len(self.buttons) * spread + 20),
                                   vals[8], self.size))
        self.buttons.append(Button(self.button_group, self.display, "Equidistant Points",
                                   (self.w - self.size + 10 * (self.size / 200), len(self.buttons) * spread + 20),
                                   vals[9], self.size))

        self.font = pygame.font.Font('freesansbold.ttf', int(16 * (self.size / 200)))
        self.arcLengthTextPos = (self.w - self.size + 10 * (self.size / 200), len(self.buttons) * spread + 20)
        self.arcLengthTextTopLeft = (self.arcLengthTextPos[0] + 20, self.arcLengthTextPos[1])
        # self.arcLengthTextTopLeft = (self.arcLengthTextPos[0] + (self.size / 20) * 4, self.arcLengthTextPos[1] + 7 * (self.size / 200))

    def draw(self, arcLength):
        pygame.draw.rect(self.display, (34, 45, 56), pygame.Rect(self.w - self.size, 0, self.size, self.h))
        self.button_group.update()

        arcLengthText = self.font.render(f"Path Length: {round(arcLength / PPI, 3)}", True, (240, 240, 240))
        arcLengthTextRect = arcLengthText.get_rect()
        arcLengthTextRect.topleft = self.arcLengthTextTopLeft
        self.display.blit(arcLengthText, arcLengthTextRect)

    def getValues(self):
        return [b.enabled for b in self.buttons]
