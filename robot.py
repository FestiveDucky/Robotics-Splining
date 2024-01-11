import time

import pygame
import math
from constants import *


def newPoint(angle, distance, x, y):
    angle = math.radians(angle)
    return x + math.cos(angle) * distance, y + math.sin(angle) * distance


class Robot:
    def __init__(self, start):
        self.coords = start
        self.rotation = 0
        self.im = pygame.surface.Surface((PPI * TRACKWIDTH, PPI * ROBOTLENGTH))
        self.im.set_colorkey((0, 0, 0))
        # self.speed = 1
        # self.leftMotorVoltage = 600
        # self.rightMotorVoltage = 600
        # self.previousAccel = (0, 0)
        self.im.fill((1, 1, 1))
        self.im.set_alpha(30)
        self.rect = self.im.get_rect(centerx=start[0], centery=start[1])
        # self.t = 0
        # self.rect = pygame.Rect(start, (PPI*TRACKWIDTH, PPI*TRACKWIDTH))

    # def move(self):
    #     leftLinearSpeed = 2 * pi * WHEELRADIUS * self.leftMotorVoltage / 60
    #     rightLinearSpeed = 2 * pi * WHEELRADIUS * self.rightMotorVoltage / 60
    #
    #     # Radians per minute
    #     angularVelocity = (leftLinearSpeed - rightLinearSpeed) / TRACKWIDTH
    #     # Degrees per minute
    #     angularVelocity = degrees(angularVelocity)
    #     self.rotation += angularVelocity / 60
    #     if self.rotation < 0:
    #         self.rotation += 360
    #     elif self.rotation >= 360:
    #         self.rotation -= 360
    #
    #     # in/minute
    #     averageLinearSpeed = (leftLinearSpeed + rightLinearSpeed) / 2
    #
    #     # Speed converted to in/s
    #     self.coords = newPoint(-self.rotation, averageLinearSpeed / 60, self.coords[0], self.coords[1])
    #
    #     newImage = pygame.transform.rotate(self.image, self.rotation % 360)
    #     self.rect = newImage.get_rect()
    #     self.rect.center = self.coords
    #     return newImage
    #
    # def calculateVoltages(self, accelValues):
    #     if self.t >= len(accelValues):
    #         return True
    #     accelX, accelY = accelValues[self.t]
    #
    #     maxAccel = 100
    #     scaling = 0.1
    #
    #     vectorAngle = minAngleBetweenAngles(self.rotation, calculateAngle((0, 0), (accelY, accelX)))
    #
    #     vectorMagnitude = math.sqrt((accelX ** 2) + (accelY ** 2))
    #     voltageChange = vectorMagnitude * vectorAngle * scaling
    #
    #     # TODO set a max to voltage
    #     self.leftMotorVoltage += voltageChange * 0.5 + vectorMagnitude * 0.5
    #     self.rightMotorVoltage -= voltageChange * 0.5 + vectorMagnitude + 0.5
    #
    #     self.rightMotorVoltage = max(min(self.rightMotorVoltage, 12000), 0)
    #     self.leftMotorVoltage = max(min(self.leftMotorVoltage, 12000), 0)
    #
    #
    #     print(f"Right: {self.rightMotorVoltage}")
    #     print(f"Left: {self.leftMotorVoltage}")
    #     print("-------------------")
    #     self.t += 1
    #     return False
    #
    #
    # def animate(self, display, maxVelocity, accelerations, points, menu, curve):
    #     print(accelerations)
    #     while not events():
    #         display.fill((14, 25, 36))
    #         display.blit(bg, (0, 0))
    #         curve.draw(False, True, False, 0, False, False, False, False, False, False, [], haveEvents=False)
    #         menu.draw(curve.arcLength)
    #         if self.calculateVoltages(accelerations):
    #             break
    #         display.blit(self.move(), self.rect)
    #         pygame.draw.circle(display, (150, 0, 255), self.coords, 5, 5)
    #
    #         # Updating the display
    #         pygame.display.update()
    #
    # def turn(self, direction):
    #     self.rotation += 2 * direction
    #
    # def accelerate(self, direction):
    #     self.speed += 0.01 * direction
    #
    def manualMove(self, start):
        moving = True
        following = False
        while moving:
            ev = pygame.event.get()
            for e in ev:
                if e.type == pygame.QUIT:
                    pygame.quit()
                if e.type == pygame.MOUSEMOTION:
                    if following:
                        self.coords = e.pos
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_t:
                        moving = False
                    elif e.key == pygame.K_SPACE:
                        following = not following
                        self.coords = pygame.mouse.get_pos()
                    elif e.key == pygame.K_p:
                        print(f"(X, Y) of robot: ({round((start[1] - self.coords[1]) / PPI, 3)}, {round((start[0] - self.coords[0]) / PPI, 3)})")

            # For rotation of bot
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.rotation += 2
            if keys[pygame.K_RIGHT]:
                self.rotation -= 2

            gamedisplay.fill((14, 25, 36), pygame.Rect((HEIGHT, 0, LINE_THICKNESS * 2, HEIGHT)))

            im = pygame.transform.rotate(self.im, self.rotation % 360)
            self.rect = im.get_rect()
            self.rect.center = self.coords
            gamedisplay.blit(bg, (0, 0))
            gamedisplay.blit(im, self.rect)
            pygame.draw.circle(gamedisplay, (255, 255, 255), self.coords, LINE_THICKNESS * 2)

            pygame.display.update()
