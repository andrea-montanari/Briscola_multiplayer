import pygame
import sys
import ctypes

pygame.init()

# PyGame configuration variables
size = (0, 0)

# Sets window to maximum dimension without loosing the taskbar
screen = pygame.display.set_mode(size, pygame.RESIZABLE)
pygame.display.set_caption("Bouncing Ball")
# if sys.platform == "win32":
#     HWND = pygame.display.get_wm_info()['window']
#     SW_MAXIMIZE = 3
#     ctypes.windll.user32.ShowWindow(HWND, SW_MAXIMIZE)

screen_w, screen_h = screen.get_size()
print(screen_w, " ", screen_h)
background = pygame.image.load("table6.png")
background = pygame. transform. scale(background, (screen_w, screen_h))

class Card:
    def __init__(self, position, card_code):
        self.position = position
        self.face = pygame.image.load("svg-napoletane/" + card_code + ".png")
        self.back = pygame.image.load("svg-napoletane/back.png")
        self.rect = self.face.get_rect()
        self.rect.center = position
        self.turned = False
        print(self.position)

    def draw(self, screen):
        if not self.turned:
            screen.blit(self.face, self.rect)
        else:
            screen.blit(self.back, self.rect)

    def turn(self):
        self.turned = not self.turned

    def move(self):
        self.position[0] += 1

running = True
clock = pygame.time.Clock()
asso_denari = Card([screen_w//2, screen_h//2], "1D")
image = pygame.image.load("svg-napoletane/1D.png")
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

    pygame.time.delay(500)

    screen.blit(background, (0, 0))

    # Draw card on screen
    asso_denari.draw(screen)
    asso_denari.turn()
    asso_denari.move()

    pygame.display.update()
