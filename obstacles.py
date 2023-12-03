import pygame.sprite

from constants import *


# TODO make obstacles be saved to file and load/update file automatically, ignore last obstacle if we have odd number
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, group, p1, p2):
        super().__init__(group)
        self.p1 = p1
        self.p2 = p2

    def calculateIntersection(self, op1, op2):
        # Scuffed solution to division by zero error
        if self.p2[0] - self.p1[0] == 0:
            self.p1 = (self.p1[0] + 0.01, self.p1[1])
        if op2[0] - op1[0] == 0:
            op1 = (op1[0] + 0.01, op1[1])

        # Line calculations
        m1 = (self.p2[1] - self.p1[1]) / (self.p2[0] - self.p1[0])
        m2 = (op2[1] - op1[1]) / (op2[0] - op1[0])
        b1 = -(m1 * self.p1[0]) + self.p1[1]
        b2 = -(m2 * op1[0]) + op1[1]

        # For parallel lines we check if they are the same line
        if m2 == m1:
            if b1 == b2:
                # Identical
                return True
            return False

        xInter = (b1 - b2) / (m2 - m1)
        yInter = xInter * m1 + b1

        # print(xInter, yInter)
        # print(f"Y = {m1}x + {b1}")
        # print(f"Y = {m2}x + {b2}")

        # Determine if the intersection is between the points
        if min(op1[0], op2[0]) <= xInter <= max(op1[0], op2[0]) and min(op1[1], op2[1]) <= yInter <= max(op1[1], op2[
            1]) and min(self.p1[0], self.p2[0]) <= xInter <= max(self.p1[0], self.p2[0]) and min(self.p1[1], self.p2[
            1]) <= yInter <= max(self.p1[1], self.p2[1]):
            return True
        return False

    def update(self, display):
        drawThickLine(display, (255, 0, 0), self.p1, self.p2)


if __name__ == '__main__':
    b = pygame.sprite.Group()
    a = Obstacle(b, (-1, 0), (1, 2))
    print(a.calculateIntersection((-1, 2), (1, -2)))
