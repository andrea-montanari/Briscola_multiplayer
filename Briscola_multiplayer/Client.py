import random
import sys

import Pyro5.client
import Pyro5.server
import pygame

sys.excepthook = Pyro5.errors.excepthook

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
screen_center = (screen_w // 2, screen_h // 2)
background = pygame.image.load("table6.png").convert()
background = pygame.transform.scale(background, (screen_w, screen_h))


class Card:
    card_values = [11, 2, 10.5, 4, 5, 6, 7, 8, 9, 10]
    card_points = [11, 0, 10, 0, 0, 0, 0, 2, 3, 4]

    # Creating events that notify when the the dealer is done dealing and when the cards are moving/stopped
    # Note: adjust the event indexes if needed
    DONE_DEALING = pygame.USEREVENT + 1
    CARDS_MOVING = pygame.USEREVENT + 2
    CARDS_STOPPED = pygame.USEREVENT + 3
    done_dealing_event = pygame.event.Event(DONE_DEALING)
    cards_moving_event = pygame.event.Event(CARDS_MOVING)
    cards_stopped_event = pygame.event.Event(CARDS_STOPPED)

    def __init__(self, card_code, position, vel=10):
        self.position = position
        self.number = int(card_code[:-1])
        self.suit = card_code[-1]
        self.face = pygame.image.load("svg-napoletane/" + card_code + ".png")
        print("Card code nella classe Card: ", card_code)
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
        print("Target position: ", self.target_position)
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
        if self.position[1] < self.target_position[1] - self.vel:
            self.position[1] += self.vel
            card_moved = True
            self.moving = True
        elif self.position[1] > self.target_position[1] + self.vel:
            self.position[1] -= self.vel
            card_moved = True
            self.moving = True

        # print("card's target position: ", self.target_position[0], ", ", self.target_position[1])
        # print("Card's position: ", self.position[0], ", ", self.position[1])

        self.rect.center = self.position

        # if self.moving:
        #     pygame.event.post(Card.cards_moving_event)
        # else:
        #     pygame.event.post(Card.cards_stopped_event)

        if not card_moved and self.moving:
            if self.dealing:
                # Posting an event that notifies that the the dealer is done dealing
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

    # TODO: stato della carta (in mazzo, in mano, in quale mano, ...)


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
    DECK_FINISHED = pygame.USEREVENT + 4
    deck_finished_event = pygame.event.Event(DECK_FINISHED)

    def __init__(self, hand_positions, won_cards_position):
        self.cards_in_hand = []
        self.hand_positions = hand_positions

        # Cards played positions
        self.card_played_position_1 = [screen_center[0] - 10, screen_center[1]]
        self.card_played_position_2 = [screen_center[0] + 60, screen_center[1]]

        self.card_to_draw_index = -1
        self.won_cards_position = won_cards_position

        # TODO: make it more efficient assigning the points directly or both cards and points
        #       (afterwards you'd need to modify the winner calculation as well)
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
        drawn_card.set_target_position(self.hand_positions[self.card_to_draw_index])
        self.cards_in_hand[self.card_to_draw_index] = drawn_card

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


@Pyro5.server.expose
class Game:
    player1: Player
    player2: Player

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
        else:
            briscola_symbol = self.server_dealer.get_briscola()
        self.briscola = Card(briscola_symbol, [screen_w - 200, screen_h // 2])
        list_deck = self.server_dealer.get_deck()
        self.deck = self.transform_deck(list_deck)
        self.dummy_decks = [DummyDeck()]

        if first_hand_player:
            self.player_turn = 1
        else:
            self.player_turn = 2
        self.current_play_num = 0
        self.num_of_players = 2
        self.played_cards = {}
        self.game_winner = None

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
            card.set_target_position(player.hand_positions[index], dealing=True)
            print("player.hand_positions[index]: ", player.hand_positions[index])
            player.cards_in_hand.append(card)
        print("Cards dealing function, player1.cards_in_hand: ", self.player1.cards_in_hand)
        print(player.cards_in_hand)

    def get_adversary_cards(self):
        adversary_cards = self.server_dealer.get_adversary_cards(self.first_hand_player)
        for index, card_symbol in enumerate(adversary_cards):
            self.player2.cards_in_hand.append(Card(card_symbol, self.player2.hand_positions[index]))

    def print_turn(self, font=pygame.font.Font(None, 30), text_color=(255, 255, 255)):
        if self.player_turn == 1:
            text = "È il tuo turno"
        else:
            text = "L'avversario sta giocando"
        text_surf = font.render(text, True, text_color)
        text_rect = text_surf.get_rect()
        text_rect.center = [screen_w // 2 + 310, screen_h - 200]
        screen.blit(text_surf, text_rect)

    def print_text_on_screen(self, text, pos=[screen_w // 2, screen_h // 2], font=pygame.font.Font(None, 30), text_color=(255, 255, 255)):
        text_surf = font.render(text, True, text_color)
        text_rect = text_surf.get_rect()
        text_rect.center = pos
        screen.blit(text_surf, text_rect)

    def register_play(self):
        # TODO: evaluate moving this method to the game manager class

        # Registers play results
        self.played_cards[self.player_turn] = card

        # Updates turn and play's number
        self.current_play_num = self.current_play_num % self.num_of_players + 1
        if self.current_play_num == 1 and self.player_turn == 1:
            self.player_turn = 2
        elif self.current_play_num == 1 and self.player_turn == 2:
            self.player_turn = 1
        elif self.current_play_num == 2:
            self.player_turn = 0
        print("Play results: ", self.played_cards)
        print("Plays num: ", self.current_play_num)

    def calculate_hand_winner(self, players, briscola):
        # TODO: evaluate moving this method to the game manager class

        # Establish winner
        briscola_suit = briscola.suit
        p1_suit = self.played_cards[1].suit
        p1_value = self.played_cards[1].value
        p2_suit = self.played_cards[2].suit
        p2_value = self.played_cards[2].value
        first_to_play = list(self.played_cards.keys())[0]
        print("p1 number: ", p1_value)
        print("p2 number: ", p2_value)
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
            winner = first_to_play
        elif p1_value > p2_value:
            winner = 1
        else:
            winner = 2

        self.player_turn = winner
        self.current_play_num = 0

        # Add won cards to the list of won cards of the player
        played_cards_list = list(self.played_cards.values())
        players[winner - 1].won_cards += played_cards_list

        # Move the cards from the table to the "won cards deck" of the winner
        played_cards_list[0].set_target_position(players[winner - 1].won_cards_position)
        played_cards_list[1].set_target_position(players[winner - 1].won_cards_position)

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

    def show_won_cards(self, space_between=40):
        for player in self.players:
            for index, card in enumerate(player.won_cards):
                # print("Card: (", card, "): ", ", target position: ", card.target_position)
                # pos = [card.position[0] + (index*10), card.position[1]]
                card.turn()
                new_position = [50 + index * space_between, card.target_position[1]]
                card.set_target_position(new_position)

    def check_ready_to_assign_the_win(self):
        """
        Checks if the game winner can be calculated, that is when the sum of the cards in the players' deck sum to 40
        (all the cards are in their won cards deck)
        :return: True if the winner can be calculated, False otherwise
        """
        sum = 0
        for player in self.players:
            sum += len(player.won_cards)
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


# Pyro5 server
server_match_manager_object = Pyro5.client.Proxy("PYRONAME:server.match_manager_object")
daemon = Pyro5.server.Daemon()
uri = daemon.register(Game)
ns = Pyro5.core.locate_ns()
ns.register("client.game", uri)

game = None
# game = Game(first_hand_player=1)    # TODO: modify this to be the player that created the game on the server

# print("Len deck: ", len(game.deck))
# print("Deck: ", game.deck.keys()),
# print("Briscola: ", str(game.briscola.number) + game.briscola.suit)

# Buttons creation
btn_exit = Button('X', (screen_w - 100, 50), 40, 40, border_radius=30, over_color='#D74B4B')
btn_new_game = Button('NEW GAME', (screen_w // 2, screen_h // 2 - 60), 150, 40, border_radius=30)
btn_join_game = Button('JOIN GAME', (screen_w // 2, screen_h // 2 + 30), 150, 40, border_radius=30)

# Loop management variables
running = True
clock = pygame.time.Clock()
done_dealing = False
cards_moving = True

# Game status initialization
WAITING = 0
PREPARING = 1
PLAYING = 2
GAME_OVER = 3
game_status = WAITING
deck_finished = False  # Needs a different variable because it holds also in the GAME_OVER status

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        if event.type == Card.DONE_DEALING:
            game_status = PLAYING
            print("DONE DEALING EVENT")
        if event.type == Card.CARDS_MOVING:
            cards_moving = True
            # print("Cards MOVING event!!!")
        if event.type == Card.CARDS_STOPPED:
            cards_moving = False
            # print("Cards NOT MOVING event!!!")
        # Delete the dummy deck whe the game is over
        if event.type == Player.DECK_FINISHED:
            print("DECK FINISHED!!!")
            deck_finished = True
            game.dummy_decks.pop(0)

    screen.blit(background, (0, 0))
    pygame.draw.circle(screen, (255, 0, 0), screen_center, 4)  # TODO: remove

    # Button drawing and handling
    btn_exit.draw(screen)
    if btn_exit.check_click():
        running = False
        pygame.quit()
        sys.exit()
    if game_status == WAITING:
        btn_new_game.draw(screen)
        if btn_new_game.check_click():
            server_dealer_uri = server_match_manager_object.new_match(1)
            server_dealer = Pyro5.client.Proxy(server_dealer_uri)
            print("Server dealer uri: ", server_dealer)
            game = Game(first_hand_player=True, server_dealer=server_dealer)
            screen.blit(background, (0, 0))
            game.print_text_on_screen("Attendere l'avversario...")
            pygame.display.update()
            print("Deck giocatore 1: ", game.deck, "\nLen deck: ", len(game.deck))
            print("server_match_manager_object giocatore 1: ", server_match_manager_object)
            game.cards_dealing()
            game.get_adversary_cards()
            print("game.player1.cards_in_hand: ", game.player1.cards_in_hand)
            game_status = PLAYING
        btn_join_game.draw(screen)
        if btn_join_game.check_click():
            print("server_match_manager_object giocatore 2: ", server_match_manager_object)
            server_dealer_uri = server_match_manager_object.join_match()
            server_dealer = Pyro5.client.Proxy(server_dealer_uri)
            game = Game(first_hand_player=False, server_dealer=server_dealer)
            print("Deck giocatore 2: ", game.deck, "\nLen deck: ", len(game.deck))
            game.cards_dealing()
            game.get_adversary_cards()
            print("game.player1.cards_in_hand: ", game.player1.cards_in_hand)
            game_status = PLAYING

    # If the server creates a Game object, it means that the game is ready and the clients can play
    if not game is None:
        game_status = PLAYING

    if not game_status == WAITING:
        # ------------------------------------ Game -------------------------------------- #
        if game_status == PLAYING:
            game.briscola.draw(screen)

        # Draws dummy decks
        # TODO: create dummy decks for the "won cards decks"
        for dummy_deck in game.dummy_decks:
            dummy_deck.draw(screen)

        # The cards in the players' hands and the won cards are shown, meanwhile we get a boolean variable for when the dealer is done dealing
        # and the cards are not moving anymore.
        if game_status != GAME_OVER:
            for card in game.player1.cards_in_hand + game.player2.cards_in_hand + game.player1.won_cards + game.player2.won_cards + \
                        list(game.played_cards.values()):
                card.draw(screen)
        if game_status == GAME_OVER:
            # print("STAMPO CARTE VINTE")
            for card in game.player1.won_cards + game.player2.won_cards:
                # print("Posizione carta vinta (", card, "): ", card.target_position)
                card.draw(screen)
                game.print_game_winner(screen_center)

        # Checks for mouse clicks only for the cards of the player whose turn is now.
        # When both players have played the check is performed again only when a new play is ready (
        # result calculated and cards drawn)
        # TODO: creare una o più funzioni per la giocata.
        # print("dealer.player_turn: ", dealer.player_turn)
        # print("Done dealing: ", done_dealing)
        if game_status == PLAYING and game.player_turn > 0 and not game.player1.waiting_for_card() and not game.player2.waiting_for_card():
            game.print_turn()
            played_card = None
            for i, card in enumerate(game.players[game.player_turn - 1].cards_in_hand):
                card_clicked = card.check_click(screen)
                if card_clicked:
                    played_card = card
                    current_player = game.players[game.player_turn - 1]
                    # print("Card clicked", played_card.number, played_card.suit)
                    # print("players[dealer.player_turn-1].cards_in_hand", players[dealer.player_turn-1].cards_in_hand)
                    current_player.play(card, card_index=i, plays_num=game.current_play_num)
                    game.register_play()
                    card.draw(screen)
                    if deck_finished:
                        current_player.pop_card_in_hand(index=i)

        if game.current_play_num == 2:
            if not played_card.is_moving():
                winner = game.calculate_hand_winner(game.players, game.briscola)
                if not deck_finished:
                    game.players[winner - 1].draw_card(game.deck, game.briscola)  # The winner draws first
                    print("Winner: ", winner, "winner % 2 + 1: ", winner % 2 + 1)
                    game.players[winner % 2].draw_card(game.deck, game.briscola)
                # print("Player 1 cards in hand: ", [str(x.number)+x.suit for x in player1.cards_in_hand])
                # print("Player 2 cards in hand: ", [str(x.number)+x.suit for x in player2.cards_in_hand])

        # The game is over when neither of the players have any card in their hand
        # print("---\n\nGame status: ", game_status, "\n\n---")
        if deck_finished and game.player1.get_cards_in_hand_number() == 0 and game.player2.get_cards_in_hand_number() == 0 \
                and game.check_ready_to_assign_the_win() and not game_status == GAME_OVER:
            game_status = GAME_OVER
            game.show_won_cards()
            game_winner = game.calculate_game_winner()
        # -------------------------------------------------------------------------------- #

    clock.tick(60)
    pygame.display.update()
