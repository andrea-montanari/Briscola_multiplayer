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
background = pygame.image.load("table6.png").convert()
background = pygame. transform. scale(background, (screen_w, screen_h))

class Card:
    card_values = [11,2,10.5,4,5,6,7,8,9,10]
    card_points = [11,0,10,0,0,0,0,2,3,4]

    # Creating an event that notifies the the dealer is done dealing
    DONE_DEALING = pygame.USEREVENT + 1
    done_dealing_event = pygame.event.Event(DONE_DEALING)

    def __init__(self, card_code, position):
        self.position = position
        self.number = int(card_code[:-1])
        self.seed = card_code[-1]
        self.face = pygame.image.load("svg-napoletane/" + card_code + ".png")
        print("Card code nella classe Card: ", card_code)
        self.back = pygame.image.load("svg-napoletane/back.png")
        self.rect = self.face.get_rect()
        self.rect.center = position
        self.turned = False
        self.vel = 5

        # Values assignment: used to determine the hand winner
        self.value = Card.card_values[self.number-1]
        # Points assignment: used to determine the game winner
        self.points = Card.card_points[self.number-1]

        # Variables for checking when the dealing is done
        self.moving = False

        # Variables used to handle the mouse click
        self.pressed = False
        self.click = False

        # Variable use for moving the card
        self.target_position = position

    def set_target_position(self, target_position):
        self.target_position = target_position

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

        if not card_moved and self.moving:
            # Posting an event that notifies that the the dealer is done dealing (the event is published multiple
            # times but it had effect only the first time)
            pygame.event.post(Card.done_dealing_event)

            self.moving = False

    def is_moving(self):
        # target_x_r = self.target_position[0] + self.vel
        # target_x_l = self.target_position[0] - self.vel
        # target_y_down = self.target_position[0] + self.vel
        # target_y_up = self.target_position[0] - self.vel
        # if self.position[0] < target_x_r and self.position[0] > target_x_l \
        #     and self.position[1] < target_y_up and self.position[1] > target_position_down:
        #     return False
        # return True
        return self.moving

    def draw(self, screen):
        if not self.turned:
            screen.blit(self.face, self.rect)
        else:
            screen.blit(self.back, self.rect)
        self.move_card()

    def turn(self):
        self.turned = not self.turned

    def check_click(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (0,0,0), self.rect.inflate(6, 6), width=5, border_radius=8)
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
    def __init__(self, player_turn):
        self.player_turn = player_turn
        self.current_play_num = 0
        self.num_of_players = 2
        self.played_cards = {}

    def deal(self, deck, player):
        # Pop 3 random cards from the deck
        rand_card_1 = deck.pop(random.choice(list(deck.keys())))
        rand_card_2 = deck.pop(random.choice(list(deck.keys())))
        rand_card_3 = deck.pop(random.choice(list(deck.keys())))

        # Deal the cards
        rand_card_1.set_target_position(player.hand_positions[0])
        rand_card_2.set_target_position(player.hand_positions[1])
        rand_card_3.set_target_position(player.hand_positions[2])

        # Assign cards to player
        player.cards_in_hand = [rand_card_1, rand_card_2, rand_card_3]

    def set_briscola(self, deck):
        rand_card = deck.pop(random.choice(list(deck.keys())))
        return rand_card

    def register_play(self, ):
        # Registers play results
        self.played_cards[self.player_turn] = card

        # Updates turn and play's number
        self.current_play_num = self.current_play_num%self.num_of_players+1
        if self.current_play_num == 1 and self.player_turn == 1:
            self.player_turn = 2
        elif self.current_play_num == 1 and self.player_turn == 2:
            self.player_turn = 1
        elif self.current_play_num == 2:
            self.player_turn = 0
        print("Play results: ", self.played_cards)
        print("Plays num: ", self.current_play_num)

    def get_hand_winner(self, players, briscola):
        # Establish winner
        briscola_seed = briscola.seed
        p1_seed = self.played_cards[1].seed
        p1_value = self.played_cards[1].value
        p2_seed = self.played_cards[2].seed
        p2_value = self.played_cards[2].value
        first_to_play = list(self.played_cards.keys())[0]
        print("p1 number: ", p1_value)
        print("p2 number: ", p2_value)
        if briscola_seed == p1_seed and briscola_seed == p2_seed:       # Both played briscola
            if p1_value > p2_value:
                winner = 1
            else:
                winner = 2
        elif briscola_seed == p1_seed:
            winner = 1
        elif briscola_seed == p2_seed:
            winner = 2
        elif p1_seed != p2_seed:
            winner = first_to_play
        elif p1_value > p2_value:
            winner = 1
        else:
            winner = 2

        self.player_turn = winner
        self.current_play_num = 0

        # Add won cards to the list of won cards of the player
        played_cards_list = list(self.played_cards.values())
        players[winner-1].won_cards += played_cards_list

        # Move the cards from the table to the "won cards deck" of the winner
        played_cards_list[0].set_target_position(players[winner-1].won_cards_position)
        played_cards_list[1].set_target_position(players[winner-1].won_cards_position)

        # Turn the cards
        played_cards_list[0].turn()
        played_cards_list[1].turn()

        # Clean the previous play's results
        self.played_cards = {}

        return winner

class Player:
    def __init__(self, hand_positions, won_cards_position):
        self.cards_in_hand = []
        self.hand_positions = hand_positions

        # Cards played positions
        self.card_played_position_1 = [screen_center[0] - 10, screen_center[1]]
        self.card_played_position_2 = [screen_center[0]+60, screen_center[1]]

        self.card_to_draw_index = -1
        self.won_cards_position = won_cards_position
        self.won_cards = []

    def draw_card(self, deck):
        rand_key = random.choice(list(deck.keys()))
        rand_card = deck.pop(rand_key)
        rand_card.set_target_position(self.hand_positions[self.card_to_draw_index])
        self.cards_in_hand[self.card_to_draw_index] = rand_card

    def play(self, card, card_index, plays_num):
        # If the player is the first to play, the card will be in a certain position,
        # if it is the second it will be in another position

        if plays_num == 1:
            card.set_target_position(self.card_played_position_1)
        else:
            card.set_target_position(self.card_played_position_2)
        # self.cards_in_hand.pop(card_index)
        self.card_to_draw_index = card_index
        # print("Cards in hand: ", self.cards_in_hand)

class DummyDeck:
    def __init__(self, position, path="svg-napoletane/back.png"):
        self.image = pygame.image.load(path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = position

    def draw(self, screen):
        screen.blit(self.image, self.rect)

# Buttons creation
btn_exit = Button('X', (screen_w - 100, 50), 40, 40, border_raduis=30, over_color='#D74B4B')
btn_draw = Button('DRAW', (80, 50), 100, 40, border_raduis=30)

# Cards creation
deck = {}
card_suits = ['B', 'C', 'D', 'S']
suits_index = 0
for i in range(0, 40):
    deck_key = str(i%10+1) + card_suits[i//10]
    print("deck_key: ", deck_key)
    print("Suit index: ", suits_index)
    deck[deck_key] = Card(str(i%10+1)+card_suits[suits_index], [screen_w-200, screen_h//2])
    if (i+1)%10 == 0:
        suits_index += 1
dummy_decks = [DummyDeck([screen_w - 200, screen_h // 2])]

# Dealer and players creation and setup
dealer = Dealer(1)      # Player 1 begins
player1 = Player(hand_positions=[[screen_w // 2 + 110, screen_h - 200], [screen_w // 2 - 10, screen_h - 200], [screen_w // 2 - 130, screen_h - 200]], won_cards_position=[500, screen_h-200])
player2 = Player(hand_positions=[[screen_w // 2 + 110, 200], [screen_w // 2 - 10, 200], [screen_w // 2 - 130, 200]], won_cards_position=[500, 200])
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
        if event.type == Card.DONE_DEALING:
            done_dealing = True

    screen.blit(background, (0, 0))
    pygame.draw.circle(screen, (255,0,0), screen_center, 4) # TODO: remove

    # Button drawing and handling
    btn_exit.draw(screen)
    if btn_exit.check_click():
        running = False
        pygame.quit()
        sys.exit()
    btn_draw.draw(screen)

    # ------------------------------------ Game -------------------------------------- #
    if done_dealing:
        briscola.draw(screen)

    # Draws dummy decks
    # TODO: create dummy decks for the "won cards decks"
    for dummy_deck in dummy_decks:
        dummy_deck.draw(screen)

    # The cards in the players' hands and the won cards are shown, meanwhile we get a boolean variable for when the dealer is done dealing
    # and the cards are not moving anymore.
    for card in player1.cards_in_hand + player2.cards_in_hand + player1.won_cards + player2.won_cards:
        card.draw(screen)

    # Checks for mouse clicks only for the cards of the player whose turn is now.
    # When both players have played the check is performed again only when a new play is ready (
    # result calculated and cards drawn)
    # TODO: creare una o più funzioni per la giocata.
    # print("dealer.player_turn: ", dealer.player_turn)
    print("Done dealing: ", done_dealing)
    if dealer.player_turn > 0 and done_dealing:
        played_card = None
        for i, card in enumerate(players[dealer.player_turn - 1].cards_in_hand):
            card_clicked = card.check_click(screen)
            if card_clicked:
                played_card = card
                print("Card clicked", played_card.number, played_card.seed)
                # print("players[dealer.player_turn-1].cards_in_hand", players[dealer.player_turn-1].cards_in_hand)
                players[dealer.player_turn-1].play(card, card_index=i, plays_num=dealer.current_play_num)
                dealer.register_play()
                card.draw(screen)
    if dealer.current_play_num == 2:
        if not played_card.is_moving():
            winner = dealer.get_hand_winner(players, briscola)
            player1.draw_card(deck)
            player2.draw_card(deck)
            print("Player 1 cards in hand: ", [str(x.number)+x.seed for x in player1.cards_in_hand])
            print("Player 2 cards in hand: ", [str(x.number)+x.seed for x in player2.cards_in_hand])
    # -------------------------------------------------------------------------------- #

    clock.tick(60)
    pygame.display.update()