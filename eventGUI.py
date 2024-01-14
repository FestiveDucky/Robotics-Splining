from constants import *


class RobotEvent(pygame.sprite.Sprite):
    def __init__(self, group, coords, eventNum, size, index):
        super().__init__(group)
        self.coords = coords
        self.num = eventNum
        self.index = index
        self.font = pygame.font.Font('freesansbold.ttf', int(8 * (size / 200)))
        self.text = self.font.render(f"{self.num}", True, (30, 30, 30))
        self.textRect = self.text.get_rect()
        self.textRect.center = self.coords

    def update(self):
        pygame.draw.circle(gamedisplay, (171, 98, 164), self.coords, LINE_THICKNESS * 5)
        gamedisplay.blit(self.text, self.textRect)

    def setCoords(self, coords):
        self.coords = coords
        self.textRect.center = self.coords
