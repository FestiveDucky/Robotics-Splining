import pygame


class Button(pygame.sprite.Sprite):
    def __init__(self, group, display, text, pos, val, size):
        super().__init__(group)
        self.display = display
        self.size = (size/20) * 3
        self.font = pygame.font.Font('freesansbold.ttf', int(16 * (size/200)))
        self.text = self.font.render(text, True, (240, 240, 240))
        self.textRect = self.text.get_rect()
        self.textRect.topleft = (pos[0] + (size/20) * 4, pos[1] + 7*(size/200))
        self.rect = pygame.Rect(pos[0], pos[1], self.size, self.size)
        self.pos = pos
        self.enabled = val

    def update(self):
        self.display.blit(self.text, self.textRect)
        pygame.draw.rect(self.display, (23, 40, 52), self.rect)

        color = (10, 10, 10)
        if self.enabled:
            color = (10, 100, 80)

        pygame.draw.rect(self.display, color, pygame.Rect(self.pos[0] + self.size/6, self.pos[1] + self.size/6, self.size*2/3, self.size*2/3))

    def pressed(self):
        self.enabled = not self.enabled

    def set(self, val):
        self.enabled = val


ORANGE = (243, 170, 78)
DARK_BLUE = (17, 24, 32)
SEMI_DARK_BLUE = (47, 54, 62)
BLUE = (77, 84, 92)
