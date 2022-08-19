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

    # TODO: stato della carta (in mazzo, in mano, in quale mano, ...)

class Button:
    def __init__(self, text, pos, width, height, elevation=6, border_raduis=10, font=pygame.font.Font(None,30), text_color=(255,255,255), top_color='#475F77', bottom_color='#354B5E', over_color='#354B5E', rounded=True):
        # Core attributes
        self.pressed = False
        self.click = False
        self.elevation = elevation
        self.dynamic_elevation = elevation
        self.original_y_pos = pos[1]
        self.border_radius = border_raduis

        # Top rectangle
        self.top_rect = pygame.Rect((pos), (width, height))
        self.top_color = top_color
        self.over_color = over_color
        self.saved_color = self.top_color

        # Bottom rectangle
        self.bottom_rect = pygame.Rect(pos, (width, elevation))
        self.bottom_color = bottom_color

        # Text
        self.text_surf = font.render(text, True, text_color)
        self.text_rect = self.text_surf.get_rect(center = self.top_rect.center)

    def draw(self, screen):
        # Elevation logic
        self.top_rect.y = self.original_y_pos - self.dynamic_elevation
        self.text_rect.center = self.top_rect.center

        self.bottom_rect.midtop = self.top_rect.midtop
        self.bottom_rect.height = self.top_rect.height + self.dynamic_elevation

        pygame.draw.rect(screen, self.bottom_color, self.bottom_rect, border_radius=self.border_radius)
        pygame.draw.rect(screen, self.top_color, self.top_rect, border_radius=self.border_radius)
        screen.blit(self.text_surf, self.text_rect)
        self.check_click()

    def check_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.top_rect.collidepoint(mouse_pos):
            self.top_color = self.over_color
            if pygame.mouse.get_pressed()[0]:   # checks fot the left button click
                self.pressed = True
                self.dynamic_elevation = 0
            else:
                self.dynamic_elevation = self.elevation
                if self.pressed == True:    # We consider the button pressed only if the mouse button was pressed and then released
                    self.click = True
                    self.pressed = False
        else:
            self.click = False
            self.pressed = False
            self.dynamic_elevation = self.elevation
            self.top_color = self.saved_color

        return self.click

# Buttons creation
btn_exit = Button('X', (screen_w - 100, 50), 40, 40, border_raduis=30, over_color='#D74B4B')
btn_start = Button('START', (80, 50), 100, 40, border_raduis=30)

# Cards creation
asso_denari = Card([screen_w//2, screen_h//2], "1D")


running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()

    # pygame.time.delay(500)

    screen.blit(background, (0, 0))

    # Buttons
    btn_exit.draw(screen)
    button_pressed = btn_exit.check_click()
    if button_pressed:
        running = False
        pygame.quit()
    btn_start.draw(screen)

    # Draw card on screen
    asso_denari.draw(screen)
    # asso_denari.turn()
    asso_denari.move()

    pygame.display.update()
    clock.tick(60)
