import random
import sys
import Pyro5.client
import Pyro5.server
import pygame
import threading

import remote_connection_config as conn_cfg

sys.excepthook = Pyro5.errors.excepthook

pygame.init()

# PyGame configuration variables
size = (0, 0)

# Sets window to maximum dimension without loosing the taskbar
screen = pygame.display.set_mode(size, pygame.RESIZABLE)
pygame.display.set_caption("Bouncing Ball")

# Gets window dimensions and sets the background
screen_w, screen_h = screen.get_size()
screen_center = (screen_w // 2, screen_h // 2)
background = pygame.image.load("table6.png").convert()
background = pygame.transform.scale(background, (screen_w, screen_h))


class Card:
    card_values = [11, 2, 10.5, 4, 5, 6, 7, 8, 9, 10]
    card_points = [11, 0, 10, 0, 0, 0, 0, 2, 3, 4]

    # Creating events that notify when the the dealer is done dealing and when the cards are moving/stopped
    # Note: adjust the event indexes if needed
    DONE_DEALING = pygame.USEREVENT + 1
    done_dealing_event = pygame.event.Event(DONE_DEALING)

    def __init__(self, card_symbol, position, vel=10):
        self.position = position
        self.number = int(card_symbol[:-1])
        self.suit = card_symbol[-1]
        self.symbol = card_symbol
        self.face = pygame.image.load("svg-napoletane/" + card_symbol + ".png")
        print("Card code nella classe Card: ", card_symbol)
        self.back = pygame.image.load("svg-napoletane/back.png")
        self.rect = self.face.get_rect()
        self.rect.center = position
        self.turned = False
        self.vel = vel

        # Values and points assignment: used to determine the hand winner and the game winner
        self.value = Card.card_values[self.number - 1]
        self.points = Card.card_points[self.number - 1]

        # Variables for checking when the dealing is done
        self.moving = False

        # Variables used to handle the mouse click
        self.pressed = False
        self.click = False

        # Variable use for moving the card
        self.target_position = position

        # It is true when the dealer is dealing the cards
        self.dealing = False

    def set_target_position(self, target_position, dealing=False):
        self.target_position = target_position
        self.dealing = dealing

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
        else:
            self.position[0] = self.target_position[0]
        if self.position[1] < self.target_position[1] - self.vel:
            self.position[1] += self.vel
            card_moved = True
            self.moving = True
        elif self.position[1] > self.target_position[1] + self.vel:
            self.position[1] -= self.vel
            card_moved = True
            self.moving = True
        else:
            self.position[1] = self.target_position[1]

        self.rect.center = self.position

        if not card_moved and self.moving:
            if self.dealing:
                # Posting an event that notifies that the the dealer is done dealing
                pygame.event.post(Card.done_dealing_event)
            self.moving = False

    def is_moving(self):
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
            pygame.draw.rect(screen, (0, 0, 0), self.rect.inflate(6, 6), width=5, border_radius=8)
            if pygame.mouse.get_pressed()[0]:  # checks fot the left button click
                self.pressed = True
            else:
                if self.pressed:  # We consider the button pressed only if the mouse button was pressed and then released
                    self.click = True
                    self.pressed = False
        else:
            self.click = False
            self.pressed = False
        if self.click:
            print("Click")
        return self.click


class Button:
    def __init__(self, text, pos, width, height, elevation=6, border_radius=10, font=pygame.font.Font(None, 30),
                 text_color=(255, 255, 255), top_color='#475F77', bottom_color='#354B5E', over_color='#354B5E'):
        # Core attributes
        self.pressed = False
        self.click = False
        self.elevation = elevation
        self.dynamic_elevation = elevation
        self.original_y_pos = pos[1]
        self.border_radius = border_radius

        # Top rectangle
        position = (pos[0] - width // 2, pos[1] - height // 2)
        self.top_rect = pygame.Rect(position, (width, height))
        self.top_color = top_color
        self.over_color = over_color
        self.saved_color = self.top_color

        # Bottom rectangle
        self.bottom_rect = pygame.Rect(pos, (width, elevation))
        self.bottom_color = bottom_color

        # Text
        self.text_surf = font.render(text, True, text_color)
        self.text_rect = self.text_surf.get_rect(center=self.top_rect.center)

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
            if pygame.mouse.get_pressed()[0]:  # checks fot the left button click
                self.pressed = True
                self.dynamic_elevation = 0
            else:
                self.dynamic_elevation = self.elevation
                if self.pressed:  # We consider the button pressed only if the mouse button was pressed and then released
                    self.click = True
                    self.pressed = False
        else:
            self.click = False
            self.pressed = False
            self.dynamic_elevation = self.elevation
            self.top_color = self.saved_color

        return self.click


class Player:
    # Creating an event that notifies the end of the game
    # Note: adjust the event indexes if needed
    DECK_FINISHED = pygame.USEREVENT + 2
    deck_finished_event = pygame.event.Event(DECK_FINISHED)

    def __init__(self, hand_positions, won_cards_position):
        self.cards_in_hand = []
        self.hand_positions = hand_positions
        print("Initial hand positions: ", self.hand_positions)

        # Cards played positions
        self.card_played_position_1 = [screen_center[0] - 10, screen_center[1]]
        self.card_played_position_2 = [screen_center[0] + 60, screen_center[1]]

        self.card_to_draw_index = None
        self.won_cards_position = won_cards_position

        self.won_cards = []
        self.game_points = 0

    def draw_card(self, deck, briscola):
        """
        Draws a card from the deck
        :param deck: deck of cards
        :param briscola: briscola card, it is drawn when the deck is empty
        """
        if len(deck) != 0:
            drawn_card = deck.pop(random.choice(list(deck.keys())))
        # At the last hand we have to draw the "briscola" card and notify that the deck is finished
        else:
            drawn_card = briscola
            pygame.event.post(Player.deck_finished_event)  # Notify the end of the game

        print("Len deck: ", len(deck))
        hand_position = self.hand_positions[self.card_to_draw_index]
        drawn_card.set_target_position(hand_position)
        self.cards_in_hand[self.card_to_draw_index] = drawn_card

    def play(self, card, card_index, game_turn, player_turn):
        # If the player is the first to play, the card will be in a certain position,
        # if it is the second it will be in another position

        if game_turn == player_turn:
            card.set_target_position(self.card_played_position_1)
        else:
            card.set_target_position(self.card_played_position_2)
        self.card_to_draw_index = card_index
        print("Card to draw index: ", self.card_to_draw_index)

    def waiting_for_card(self):
        """
        :return: True if the drawn card stopped (arrived in hand), False otherwise
        """
        for card in self.cards_in_hand:
            if card.is_moving():
                return True
        return False

    def pop_card_in_hand(self, index):
        self.cards_in_hand.pop(index)

    def get_cards_in_hand_number(self):
        return len(self.cards_in_hand)

    def assign_game_points(self, game_points):
        self.game_points = game_points


class DummyDeck:
    def __init__(self, position=[screen_w - 200, screen_h // 2], path="svg-napoletane/back.png"):
        self.image = pygame.image.load(path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = position

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Game:
    player1: Player
    player2: Player

    player1_hand_positions = [[screen_w // 2 + 110, screen_h - 200], [screen_w // 2 - 10, screen_h - 200],
                            [screen_w // 2 - 130, screen_h - 200]]
    player2_hand_positions = [[screen_w // 2 + 110, 200], [screen_w // 2 - 10, 200],
                                              [screen_w // 2 - 130, 200]]

    def __init__(self, first_hand_player, server_dealer):
        # Players and manager creation
        self.player1 = Player(
            hand_positions=[[screen_w // 2 + 110, screen_h - 200], [screen_w // 2 - 10, screen_h - 200],
                            [screen_w // 2 - 130, screen_h - 200]],
            won_cards_position=[500, screen_h - 200])
        self.player2 = Player(hand_positions=[[screen_w // 2 + 110, 200], [screen_w // 2 - 10, 200],
                                              [screen_w // 2 - 130, 200]], won_cards_position=[500, 200])
        self.players = [self.player1, self.player2]  # Player1 corresponds to the user that is running the client
        self.first_hand_player = first_hand_player

        # Briscola, deck and dummy deck creation
        self.server_dealer = server_dealer
        if first_hand_player:
            self.server_dealer.create_deck()
            briscola_symbol = self.server_dealer.set_briscola()
            self.player_turn = 1
        else:
            briscola_symbol = self.server_dealer.get_briscola()
            self.player_turn = 2
        self.briscola = Card(briscola_symbol, [screen_w - 200, screen_h // 2])
        list_deck = self.server_dealer.get_deck()
        self.deck = self.transform_deck(list_deck)
        self.dummy_decks = [DummyDeck()]

        self.game_turn = 1          # Current game turn

        self.num_of_players = 2
        self.played_cards = {}
        self.game_winner = None

        self.adversary_played_card_symbol = None
        self.adversary_played_card_thread_running = False

    def reset_hand_positions(self):
        self.player1.hand_positions = Game.player1_hand_positions
        self.player2.hand_positions = Game.player2_hand_positions

    @staticmethod
    def transform_deck(deck):
        """
        Transforms the server generated deck in a dictionary populated with Card objects
        :param deck: list of cards'symbols that represent a deck
        :return: dictionary with card symbols as keys and Card objects as values
        """
        transformed_deck = {}
        for card_symbol in deck:
            card_suit = card_symbol[-1]
            card_number = card_symbol[:-1]
            transformed_deck[card_symbol] = Card(card_number + card_suit, [screen_w - 200, screen_h // 2])
        return transformed_deck

    def cards_dealing(self):
        dealt_cards = self.server_dealer.deal(self.first_hand_player)
        player = self.player1
        for index, card_symbol in enumerate(dealt_cards):
            card = self.deck.pop(card_symbol)
            print("Card: ", card)
            hand_position = player.hand_positions[index]
            card.set_target_position(hand_position, dealing=True)
            player.cards_in_hand.append(card)
        print("Cards dealing function, player1.cards_in_hand: ", self.player1.cards_in_hand)
        print(player.cards_in_hand)

    def get_adversary_cards(self):
        adversary_cards = self.server_dealer.get_adversary_cards(self.first_hand_player)
        if adversary_cards == None:
            return 0
        for index, card_symbol in enumerate(adversary_cards):
            hand_position = self.player2.hand_positions[index]
            adversary_card = Card(card_symbol, hand_position)
            adversary_card.turn()
            self.player2.cards_in_hand.append(adversary_card)
        return 1

    def print_turn(self, font=pygame.font.Font(None, 30), text_color=(255, 255, 255)):
        if self.game_turn == self.player_turn:
            text = "È il tuo turno"
        else:
            text = "L'avversario sta giocando"
        text_surf = font.render(text, True, text_color)
        text_rect = text_surf.get_rect()
        text_rect.center = [screen_w // 2 + 310, screen_h - 200]
        screen.blit(text_surf, text_rect)

    @staticmethod
    def print_text_on_screen(text, pos=[screen_w // 2, screen_h // 2], font=pygame.font.Font(None, 30),
                             text_color=(255, 255, 255)):
        text_surf = font.render(text, True, text_color)
        text_rect = text_surf.get_rect()
        text_rect.center = pos
        screen.blit(text_surf, text_rect)

    def register_play(self, played_card):
        # Registers play results
        if self.player_turn == self.game_turn:
            self.played_cards[0] = played_card
        else:
            self.played_cards[1] = played_card
        print("Register play - played card: ", played_card.symbol)

        # Updates turn and play's number
        if self.game_turn == 1:
            self.game_turn = 2
        elif self.game_turn == 2:
            self.game_turn = 0
        print("Play results: ", self.played_cards)

    def get_adversary_played_card(self):
        if self.player_turn == 1:
            return self.played_cards.get(1)
        else:
            return self.played_cards.get(0)

    def calculate_hand_winner(self):
        # Establish winner
        briscola_suit = self.briscola.suit
        p1_suit = self.played_cards.get(0).suit
        p1_value = self.played_cards.get(0).value
        p2_suit = self.played_cards.get(1).suit
        p2_value = self.played_cards.get(1).value
        if briscola_suit == p1_suit and briscola_suit == p2_suit:  # Both played a briscola card
            if p1_value > p2_value:
                winner = 1
            else:
                winner = 2
        elif briscola_suit == p1_suit:
            winner = 1
        elif briscola_suit == p2_suit:
            winner = 2
        elif p1_suit != p2_suit:
            winner = self.player_turn
        elif p1_value > p2_value:
            winner = 1
        else:
            winner = 2

        self.player_turn = winner
        self.game_turn = 1

        # Add won cards to the list of won cards of the player
        played_cards_list = list(self.played_cards.values())
        self.players[winner - 1].won_cards += played_cards_list

        # Move the cards from the table to the "won cards deck" of the winner
        played_cards_list[0].set_target_position(self.players[winner - 1].won_cards_position)
        played_cards_list[1].set_target_position(self.players[winner - 1].won_cards_position)

        # Turn the cards
        played_cards_list[0].turn()
        played_cards_list[1].turn()

        # Clean the previous play's results
        self.played_cards = {}

        return winner

    def calculate_game_winner(self):
        player_points = []
        for i, player in enumerate(self.players):
            player_points.append(0)
            print("Player ", i + 1, " cards: ")
            for card in player.won_cards:
                player_points[i] += card.points
                print(str(card.number) + card.suit, ", ")
            print("Player ", i + 1, " points: ", player_points[i])
            player.assign_game_points(player_points[i])

        print("Set player points: ", set(player_points), ", len(set(player_points)): ", len(set(player_points)))
        if len(set(player_points)) == 1:  # Tie
            return -1
        game_winner = max(range(len(player_points)), key=player_points.__getitem__) + 1
        print("Game winner (get_game_winner): ", game_winner)
        self.game_winner = game_winner
        return game_winner

    def show_won_cards(self, space_between=42):
        print("Show won cards")
        for player in self.players:
            for index, card in enumerate(player.won_cards):
                # print("Card: (", card, "): ", ", target position: ", card.target_position)
                # pos = [card.position[0] + (index*10), card.position[1]]
                card.turn()
                new_position = [50 + index * space_between, card.target_position[1]]
                card.set_target_position(new_position)

    def check_ready_to_assign_the_win(self, deck_finished, game_status):
        """
        Checks if the game winner can be calculated, that is when the sum of the cards in the players' deck sum to 40
        (all the cards are in their won cards deck)
        :return: True if the winner can be calculated, False otherwise
        """
        if not deck_finished:
            return False
        if game_status == GAME_OVER:
            return False
        sum = 0
        for player in self.players:
            sum += len(player.won_cards)
        print("SUM OF WON CARDS: ", sum)
        if sum == 40:
            return True
        return False

    def print_game_winner(self, screen_center, font=pygame.font.Font(None, 50), text_color=(255, 255, 255)):
        text = ""
        # print("Game winner (print_game_winner): ", game_winner)
        if self.game_winner == 1:
            text += "Hai vinto con " + str(self.players[0].game_points) + " punti!"
        elif self.game_winner == -1:
            text += "Pareggio"
        else:
            text += "Hai perso con " + str(self.players[0].game_points) + " punti."

        text_surf = font.render(text, True, text_color)
        text_rect = text_surf.get_rect()
        text_rect.center = screen_center
        screen.blit(text_surf, text_rect)

    def player_draw(self, player_turn):
        # If the winner is the current player, they draw both cards from the server
        p1_drawn_card = None
        p2_drawn_card = None
        if player_turn == 1:
            p1_drawn_card = self.server_dealer.player_draw()
            p2_drawn_card = self.server_dealer.player_draw()
            print(f"Winner! Drawn cards: {p1_drawn_card}, {p2_drawn_card}")
        # If the winner is not the current player, the cards have already been drawn, then they ask for the previously
        # drawn cards
        else:
            drawn_cards = self.server_dealer.get_drawn_cards()
            print("Drawn cards: ", drawn_cards)
            p2_drawn_card = drawn_cards[0]
            p1_drawn_card = drawn_cards[1]
            print(f"Loser! Drawn cards: {p1_drawn_card}, {p2_drawn_card}")

        # Pop the drawn cards from the deck
        if p1_drawn_card == self.briscola.symbol:
            p1_drawn_card = self.briscola
        else:
            p1_drawn_card = self.deck.pop(p1_drawn_card)
        if p2_drawn_card == self.briscola.symbol:
            p2_drawn_card = self.briscola
        else:
            p2_drawn_card = self.deck.pop(p2_drawn_card)
        p2_drawn_card.turn()

        # Check if one of the drawn cards is briscola
        if self.briscola.symbol == p1_drawn_card.symbol:
            p1_drawn_card = self.briscola
            pygame.event.post(Player.deck_finished_event)   # If one of the drawn cards is briscola, then the deck is finished
        elif self.briscola.symbol == p2_drawn_card.symbol:
            p2_drawn_card = self.briscola
            pygame.event.post(Player.deck_finished_event)

        # Set drawn cards position and add them to the plyers' hands
        self.reset_hand_positions()
        self.player2.cards_in_hand[self.player2.card_to_draw_index] = p2_drawn_card
        self.player2.cards_in_hand[self.player2.card_to_draw_index].set_target_position(Game.player2_hand_positions[self.player2.card_to_draw_index])
        self.player1.cards_in_hand[self.player1.card_to_draw_index] = p1_drawn_card
        self.player1.cards_in_hand[self.player1.card_to_draw_index].set_target_position(Game.player1_hand_positions[self.player1.card_to_draw_index])


class PyroConfigurator:

    def __init__(self):
        Game.print_text_on_screen("Connessione al server...")
        self.ns = Pyro5.core.locate_ns(
            conn_cfg.server_address['ip'],
            conn_cfg.server_address['port']
        )

    # Pyro5 configuration and NS connection
    def get_server_match_manager_object(self):
        server_match_manager_object_uri = self.ns.lookup("server.match_manager_object")
        print("Nameserver: ", self.ns)
        print("server_match_manager_object_uri: ", server_match_manager_object_uri)
        with Pyro5.client.Proxy(server_match_manager_object_uri) as server_match_manager_object:
            try:
                server_match_manager_object._pyroBind()
                print("YEP IT IS RUNNING!")
                return server_match_manager_object
            except Pyro5.errors.CommunicationError:
                print("NOPE IT IS NOT REACHABLE!")
                return 0


pyro_config = PyroConfigurator()

game = None

# Game status initialization
CONNECTING_TO_SERVER = 0
WAITING_FOR_PLAYER_ACTION = 1
WAITING_FOR_SECOND_PLAYER = 2
JOIN_GAME_FAILED = 3
NO_SERVER_CONNECTION = 4
PLAYING = 5
GAME_OVER = 6
ADVERSARY_DISCONNECTED = 7
game_status = CONNECTING_TO_SERVER
deck_finished = False  # Needs a different variable because it holds also in the GAME_OVER

# Busy waiting delay factor: delay factor for when we "busy wait" on the server.
# Every increment increases the delay by circa 20ms between server calls.
DELAY_FACTOR = 5

running = True

btn_home_game_over = Button('TORNA ALLA HOME', (screen_w // 2, screen_h // 2 + 90), 250, 40, border_radius=30)

def graphics_update():
    # Global variables
    global game
    global running
    global game_status
    global deck_finished

    # The cards in the players' hands and the won cards are shown, meanwhile we get a boolean variable for when the
    # dealer is done dealing and the cards are not moving anymore.
    if game_status != GAME_OVER:
        for card in game.player1.cards_in_hand + game.player2.cards_in_hand + list(game.played_cards.values()):
            card.draw(screen)
        for index in range(0, min(len(game.player1.won_cards), 3)):
            won_card_index = index+1
            game.player1.won_cards[-won_card_index].draw(screen)
        for index in range(0, min(len(game.player2.won_cards), 3)):
            won_card_index = index + 1
            game.player2.won_cards[-won_card_index].draw(screen)
    if game_status == GAME_OVER:
        for card in game.player1.won_cards + game.player2.won_cards:
            card.draw(screen)
            game.print_game_winner(screen_center)
            btn_home_game_over.draw(screen)
            if btn_home_game_over.check_click():
                game_status = WAITING_FOR_PLAYER_ACTION

    # Draws dummy decks
    for dummy_deck in game.dummy_decks:
        dummy_deck.draw(screen)


def main():

    client_id = None

    # Buttons creation
    btn_exit = Button('X', (screen_w - 100, 50), 40, 40, border_radius=30, over_color='#D74B4B')
    btn_new_game = Button('NUOVA PARTITA', (screen_w // 2, screen_h // 2 - 60), 300, 40, border_radius=30)
    btn_join_game = Button('UNISCITI AD UNA PARTITA', (screen_w // 2, screen_h // 2 + 30), 300, 40, border_radius=30)
    btn_ok = Button('OK', (screen_w // 2, screen_h // 2 - 90), 150, 40, border_radius=30)
    btn_home = Button('TORNA ALLA HOME', (screen_w // 2, screen_h // 2 - 90), 250, 40, border_radius=30)
    btn_cancel = Button('ANNULLA', (screen_w // 2, screen_h // 2 + 90), 150, 40, border_radius=30)

    # Loop management variables
    clock = pygame.time.Clock()

    # Global variables
    global game
    global running
    global game_status
    global deck_finished

    delay_server_match_requests = 0
    delay_server_dealer_request = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == Card.DONE_DEALING:
                game_status = PLAYING
            # Deletes the dummy deck when the game is over
            if event.type == Player.DECK_FINISHED:
                print("DECK FINISHED!!!")
                deck_finished = True
                game.dummy_decks.pop(0)

        screen.blit(background, (0, 0))

        # ----------------------------- SERVER CONNECTION --------------------------- #
        if game_status == CONNECTING_TO_SERVER:
            server_match_manager_object = pyro_config.get_server_match_manager_object()
            print("server_match_manager_object: ----------- ", server_match_manager_object)
            game_status = WAITING_FOR_PLAYER_ACTION
        # --------------------------------------------------------------------------- #

        # --------------------- BUTTON DRAWING AND HANDLING ------------------------- #
        btn_exit.draw(screen)
        if btn_exit.check_click():
            running = False
            try:
                game.server_dealer._pyroRelease()
                server_match_manager_object.remove_active_match(server_match.get_match_id())
                server_match_manager_object.remove_created_match(server_match.get_match_id())
                server_match._pyroRelease()
                server_match_manager_object._pyroRelease()
            except:
                pass
            pygame.quit()
            sys.exit()
        if game_status == WAITING_FOR_PLAYER_ACTION:
            btn_new_game.draw(screen)
            if btn_new_game.check_click():
                screen.blit(background, (0, 0))
                Game.print_text_on_screen("In attesa dell'avversario...")
                btn_cancel.draw(screen)
                if not server_match_manager_object:
                    server_match_manager_object = pyro_config.get_server_match_manager_object()
                if btn_cancel.check_click():
                    server_match_manager_object.remove_created_match(server_match.get_match_id())
                else:
                    pygame.display.update()
                    try:
                        client_id, server_dealer_uri, server_match_uri = server_match_manager_object.new_match()
                        server_dealer = Pyro5.client.Proxy(server_dealer_uri)
                        server_match = Pyro5.client.Proxy(server_match_uri)
                        game = Game(first_hand_player=True, server_dealer=server_dealer)
                        game.cards_dealing()
                        get_adversary_cards_success = game.get_adversary_cards()
                        print("get_adversary_cards_success: ", get_adversary_cards_success)
                        delay_server_dealer_request += 1
                        if get_adversary_cards_success:
                            delay_server_dealer_request = 0
                            game.briscola.set_target_position([screen_w - 200, screen_h // 2 - 140])
                            game_status = PLAYING
                        else:
                            game_status = WAITING_FOR_SECOND_PLAYER
                    except:
                        game_status = NO_SERVER_CONNECTION

        if game_status == WAITING_FOR_PLAYER_ACTION:
            btn_join_game.draw(screen)
            if btn_join_game.check_click():
                screen.blit(background, (0, 0))
                Game.print_text_on_screen("Ricerca giocatori in corso...")
                pygame.display.update()
                if not server_match_manager_object:
                    server_match_manager_object = pyro_config.get_server_match_manager_object()
                try:
                    print("Join match premuto")
                    client_id, server_dealer_uri, server_match_uri = server_match_manager_object.join_match()
                    print(f"client_id: {client_id}, server_dealer_uri: {server_dealer_uri}, server_match_uri: {server_match_uri}")
                    server_dealer = Pyro5.client.Proxy(server_dealer_uri)
                    server_match = Pyro5.client.Proxy(server_match_uri)
                    game = Game(first_hand_player=False, server_dealer=server_dealer)
                    print("Deck giocatore 2: ", game.deck, "\nLen deck: ", len(game.deck))
                    game.cards_dealing()
                    game.get_adversary_cards()
                    print("game.player1.cards_in_hand: ", game.player1.cards_in_hand)
                    print("Server dealer uti: ", server_dealer_uri)
                    game.briscola.set_target_position([screen_w - 200, screen_h // 2 - 140])
                    if not server_dealer_uri is None:
                        game_status = PLAYING
                except Pyro5.errors.CommunicationError:
                    game_status = NO_SERVER_CONNECTION
                except:
                    game_status = JOIN_GAME_FAILED
        if game_status == ADVERSARY_DISCONNECTED:
            Game.print_text_on_screen("Avversario disconnesso", pos=[screen_w // 2, screen_h // 2 - 120])
            btn_home.draw(screen)
            if btn_home.check_click():
                game_status = WAITING_FOR_PLAYER_ACTION
        # ------------------------------------------------------------------------ #

        if game_status == WAITING_FOR_SECOND_PLAYER:
            Game.print_text_on_screen("In attesa dell'avversario...")
            delay_server_dealer_request += 1
            btn_cancel.draw(screen)
            # Make a request to the server every 5 loop iterations
            if delay_server_dealer_request % DELAY_FACTOR == 0:
                get_adversary_cards_success = game.get_adversary_cards()
                print("get_adversary_cards_success nell'if: ", get_adversary_cards_success)
            if get_adversary_cards_success:
                delay_server_dealer_request = 0
                game.briscola.set_target_position([screen_w - 200, screen_h // 2 - 140])
                game_status = PLAYING
            if btn_cancel.check_click():
                game_status = WAITING_FOR_PLAYER_ACTION
                server_match_manager_object.remove_created_match(server_match.get_match_id())

        if game_status == JOIN_GAME_FAILED:
            screen.blit(background, (0, 0))
            Game.print_text_on_screen("Non sono presenti partite avviate.", pos=[screen_w // 2, screen_h // 2 - 140])
            Game.print_text_on_screen("Avviarne una nuova o ritentare più tardi.", pos=[screen_w // 2, screen_h // 2 - 120])
            btn_ok.draw(screen)
            if btn_ok.check_click():
                game_status = WAITING_FOR_PLAYER_ACTION

        if game_status == NO_SERVER_CONNECTION:
            screen.blit(background, (0, 0))
            Game.print_text_on_screen("Impossibile contattare il server.", pos=[screen_w // 2, screen_h // 2 - 140])
            Game.print_text_on_screen("Ritentare più tardi.", pos=[screen_w // 2, screen_h // 2 - 120])
            btn_ok.draw(screen)
            if btn_ok.check_click():
                game_status = CONNECTING_TO_SERVER

        if game_status == GAME_OVER:
            graphics_update()

        if not game_status == WAITING_FOR_PLAYER_ACTION:
            # ------------------------------------ Game -------------------------------------- #
            if game_status == PLAYING:
                game.briscola.draw(screen)
                graphics_update()

                # Check if the other player left
                try:
                    game_alive = server_match_manager_object.is_alive(server_match.get_match_id())
                    if not game_alive:
                        print("Game alive, game_status: ", game_status)
                        game_status = ADVERSARY_DISCONNECTED
                except:
                    game_status = NO_SERVER_CONNECTION

                # Checks for mouse clicks only for the cards of the player whose turn is now.
                # When both players have played the check is performed again only when a new play is ready (
                # result calculated and cards drawn)
                if not game.player1.waiting_for_card() and not game.player2.waiting_for_card():
                    game.print_turn()
                    played_card = None
                    # print("Player turnn: ", game.player_turn, " - game turn: ", game.game_turn)
                    if game.game_turn == game.player_turn:
                        for i, card in enumerate(game.player1.cards_in_hand):
                            card_clicked = card.check_click(screen)
                            if card_clicked:
                                played_card = card
                                current_player = game.player1
                                print("Played_card: ", played_card)
                                current_player.play(card, card_index=i, game_turn=game.game_turn, player_turn=game.player_turn)
                                game.register_play(played_card)
                                print("Played card number: ", played_card.number)
                                server_match.register_play(played_card.symbol, client_id)
                                card.draw(screen)
                                if deck_finished:
                                    current_player.pop_card_in_hand(index=i)
                    else:
                        adversary_played_card_symbol = None
                        delay_server_match_requests += 1
                        # Make a request every "DELAY_FACTOR" iterations of the loop
                        if delay_server_match_requests % DELAY_FACTOR == 0:
                            adversary_played_card_symbol = server_match.get_adversary_played_card(client_id)
                        if adversary_played_card_symbol is None:
                            pass
                        else:
                            delay_server_match_requests == 0
                            index = None
                            for i, card in enumerate(game.player2.cards_in_hand):
                                print("Card symbol: ", adversary_played_card_symbol, " - card in hand: ", card.symbol)
                                if card.symbol == adversary_played_card_symbol:
                                    adversary_played_card = card
                                    adversary_played_card.turn()
                                    index = i
                            game.player2.play(adversary_played_card, card_index=index, game_turn=game.game_turn, player_turn=game.player_turn)
                            game.register_play(adversary_played_card)
                            game.adversary_played_card_symbol = None
                            # Update shown cards
                            for card in game.player1.cards_in_hand + game.player2.cards_in_hand + list(
                                    game.played_cards.values()):
                                card.draw(screen)
                if game.game_turn == 0 and len(game.played_cards) == 2:
                    if not adversary_played_card.is_moving() and (played_card is None or not played_card.is_moving()):
                        pygame.time.delay(100)
                        print("Calculate hand winner")
                        game.calculate_hand_winner()
                        if not deck_finished:
                            game.reset_hand_positions()
                            game.player_draw(game.player_turn)

            # The game is over when neither of the players have any card in their hand
            if not game_status == JOIN_GAME_FAILED\
                    and not game_status == NO_SERVER_CONNECTION \
                    and not game_status == CONNECTING_TO_SERVER \
                    and game.check_ready_to_assign_the_win(deck_finished, game_status):
                game_status = GAME_OVER
                game.show_won_cards()
                game.calculate_game_winner()
                print("Releasing resources...")
                game.server_dealer._pyroRelease()
                server_match._pyroRelease()
                server_match_manager_object._pyroRelease()
                print("After releasing, game_status = ", game_status)
            # -------------------------------------------------------------------------------- #

        clock.tick(60)
        pygame.display.update()


if __name__ == "__main__":
    # TODO: direi che si possa eliminare il threading
    main_thread = threading.Thread(target=main())
    main_thread.start()