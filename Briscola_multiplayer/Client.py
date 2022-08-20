import random

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
screen_center = (screen_w//2, screen_h//2)
background = pygame.image.load("table6.png")
background = pygame. transform. scale(background, (screen_w, screen_h))

class Card:
    def __init__(self, card_code, position):
        self.position = position
        self.card_code = card_code
        self.face = pygame.image.load("svg-napoletane/" + card_code + ".png")
        self.back = pygame.image.load("svg-napoletane/back.png")
        self.rect = self.face.get_rect()
        self.rect.center = position
        self.turned = False
        self.vel = 20

        # Variables for checking when the dealing is done
        self.moving = False
        self.done_dealing = False

        # Variables used to handle the mouse click
        self.pressed = False
        self.click = False

        # Variable use for moving the card
        self.target_position = position

    def set_target_position(self, hand_position, deal=False):
        self.target_position = hand_position
        self.deal = deal

    def move_card(self):
        card_moved = False
        if self.position[0] > self.target_position[0] + self.vel:
            self.position[0] -= self.vel
            card_moved = True
            self.moving = True
        elif self.position[0] < self.target_position[0] - self.vel:
            self.position[0] += self.vel
            card_moved = True
            self.moving = True
        if self.position[1] < self.target_position[1] - self.vel:
            self.position[1] += self.vel
            card_moved = True
            self.moving = True
        elif self.position[1] > self.target_position[1] + self.vel:
            self.position[1] -= self.vel
            card_moved = True
            self.moving = True

        self.rect.center = self.position

        if not card_moved and self.moving and self.deal:
            self.moving = False
            self.done_dealing = True
        return self.done_dealing

    def draw(self, screen):
        if not self.turned:
            screen.blit(self.face, self.rect)
        else:
            screen.blit(self.back, self.rect)
        done_dealing = self.move_card()
        return done_dealing

    def turn(self):
        self.turned = not self.turned

    def check_click(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (0,0,0), self.rect, width=5, border_radius=10)
            if pygame.mouse.get_pressed()[0]:   # checks fot the left button click
                self.pressed = True
            else:
                if self.pressed == True:    # We consider the button pressed only if the mouse button was pressed and then released
                    self.click = True
                    self.pressed = False
        else:
            self.click = False
            self.pressed = False
        if self.click:
            print("Click")
        return self.click

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

class Dealer:
    def __init__(self, turn):
        self.turn = turn
        self.plays_num = 0
        self.num_of_players = 2
        self.play_results = {}

    def deal(self, deck, player):
        # Pop 3 random cards from the deck
        rand_card_1 = deck.pop(random.choice(list(deck.keys())))
        rand_card_2 = deck.pop(random.choice(list(deck.keys())))
        rand_card_3 = deck.pop(random.choice(list(deck.keys())))

        # Deal the cards
        rand_card_1.set_target_position(player.hand_positions[0], deal=True)
        rand_card_2.set_target_position(player.hand_positions[1], deal=True)
        rand_card_3.set_target_position(player.hand_positions[2], deal=True)

        # Assign cards to player
        player.cards_in_hand = [rand_card_1, rand_card_2, rand_card_3]

    def set_briscola(self, deck):
        rand_card = deck.pop(random.choice(list(deck.keys())))
        return rand_card

    def register_play(self, ):
        # Registers play results
        self.play_results[self.turn] = card

        # Updates turn and play's number
        self.plays_num = (self.plays_num+1) % (self.num_of_players+1)
        if self.plays_num == 1 and self.turn == 1:
            self.turn = 2
        elif self.plays_num == 1 and self.turn == 2:
            self.turn = 1
        elif self.plays_num == 2:
            self.turn = 0

    # def get_winner(self, player1, card_p1, player2, card_p2):


class Player:
    def __init__(self, hand_positions):
        self.cards_in_hand = []
        self.hand_positions = hand_positions

        # Cards played positions
        self.card_played_position_1 = [screen_center[0] - 10, screen_center[1]]
        self.card_played_position_2 = [screen_center[0]+60, screen_center[1]]

    def draw_card(self, deck, index):
        rand_card = deck.pop(random.choice(list(deck.keys())))
        rand_card.set_target_position(self.hand_positions[index])
        self.cards_in_hand[index] = rand_card

    def play(self, card, plays_num):
        # If the player is the first to play, the card will be in a certain position,
        # if it is the second it will be in another position

        if plays_num == 1:
            card.set_target_position(self.card_played_position_1)
        else:
            card.set_target_position(self.card_played_position_2)


# Buttons creation
btn_exit = Button('X', (screen_w - 100, 50), 40, 40, border_raduis=30, over_color='#D74B4B')
btn_draw = Button('DRAW', (80, 50), 100, 40, border_raduis=30)

# Cards creation
deck = {}
card_suits = ['B', 'C', 'D', 'S']
for i in range(0, 40):
    deck_key = str(i%10) + card_suits[i//10]
    deck[deck_key] = Card("back", [screen_w-200, screen_h//2])
dummy_deck = pygame.image.load("svg-napoletane/back.png")
dummy_deck_rect = dummy_deck.get_rect()
dummy_deck_rect.center = [screen_w - 200, screen_h // 2]

# Dealer and players setup
dealer = Dealer(1)      # Player 1 begins
player1 = Player(hand_positions=[[screen_w // 2 + 110, screen_h - 200], [screen_w // 2 - 10, screen_h - 200], [screen_w // 2 - 130, screen_h - 200]])
player2 = Player(hand_positions=[[screen_w // 2 + 110, 200], [screen_w // 2 - 10, 200], [screen_w // 2 - 130, 200]])
players = [player1, player2]
briscola = dealer.set_briscola(deck)
briscola.set_target_position([screen_w-200, screen_h//2-160])
dealer.deal(deck, player1)
dealer.deal(deck, player2)

# Loop management variables
running = True
clock = pygame.time.Clock()
done_dealing = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

    screen.blit(background, (0, 0))
    pygame.draw.circle(screen, (255,0,0), screen_center, 4) # TODO: remove

    # Buttons
    btn_exit.draw(screen)
    if btn_exit.check_click():
        running = False
        pygame.quit()
        sys.exit()
    btn_draw.draw(screen)

    # ------------------------------------ Game -------------------------------------- #
    if done_dealing:
        briscola.draw(screen)
    screen.blit(dummy_deck, dummy_deck_rect)    # Draws a dummy deck
    for card in player1.cards_in_hand + player2.cards_in_hand:
        done_dealing = card.draw(screen)

    # Checks for mouse clicks only for the cards of the player whose turn is now.
    # When both players have played the check is performed again only when a new play is ready (
    # result calculated and cards drawn)
    if dealer.turn > 0:
        for card in players[dealer.turn-1].cards_in_hand:
            card_clicked = card.check_click(screen)
            if card_clicked:
                print("IFFFF")
                dealer.register_play()
                players[dealer.turn-1].play(card, dealer.plays_num)
        # if dealer.plays_num == 2:
        #     dealer.get_winner()
    # -------------------------------------------------------------------------------- #

    clock.tick(60)
    pygame.display.update()