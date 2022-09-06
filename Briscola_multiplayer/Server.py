import Pyro5.server
import Pyro5.core
import random
import threading
import uuid

import remote_connection_config as conn_cfg

daemon = Pyro5.server.Daemon(host=conn_cfg.server_address['ip'])  # make a Pyro daemon
ns = Pyro5.core.locate_ns()


class Dealer:
    card_suits = ['B', 'C', 'D', 'S']

    def __init__(self):
        self.deck = []
        self.briscola = None
        self.first_player_cards = []
        self.second_player_cards = []

        self.drawn_cards = []

    @Pyro5.server.expose
    def create_deck(self):
        # Cards creation
        suits_index = 0
        for i in range(0, 40):
            self.deck.append(str(i % 10 + 1) + Dealer.card_suits[suits_index])
            if (i + 1) % 10 == 0:
                suits_index += 1

    @Pyro5.server.expose
    def get_deck(self):
        return self.deck

    @Pyro5.server.expose
    def deal(self, first_hand_player):
        print("Thread: ", threading.current_thread())
        if first_hand_player:
            # Pop 3 random cards from the deck
            self.first_player_cards.append(self.deck.pop(random.randint(0, len(self.deck) - 1)))
            self.first_player_cards.append(self.deck.pop(random.randint(0, len(self.deck) - 1)))
            self.first_player_cards.append(self.deck.pop(random.randint(0, len(self.deck) - 1)))
            return self.first_player_cards
        else:
            self.second_player_cards.append(self.deck.pop(random.randint(0, len(self.deck) - 1)))
            self.second_player_cards.append(self.deck.pop(random.randint(0, len(self.deck) - 1)))
            self.second_player_cards.append(self.deck.pop(random.randint(0, len(self.deck) - 1)))
            print("Len second player cards: ", len(self.second_player_cards))
            return self.second_player_cards

    @Pyro5.server.expose
    def get_adversary_cards(self, first_hand_player):
        if not first_hand_player:
            return self.first_player_cards
        print("Second player cardsss: ", self.second_player_cards)
        # Wait for the second player to call the dealer
        if len(self.second_player_cards) == 0:
            return None
        return self.second_player_cards

    @Pyro5.server.expose
    def set_briscola(self):
        rand_value = random.randint(0, len(self.deck) - 1)
        rand_card = self.deck.pop(rand_value)
        self.briscola = rand_card
        return rand_card

    @Pyro5.server.expose
    def get_briscola(self):
        return self.briscola

    @Pyro5.server.expose
    def player_draw(self):
        len_deck = len(self.deck)

        if len_deck != 0:
            drawn_card = self.deck.pop(random.randint(0, len_deck - 1))
            self.drawn_cards.append(drawn_card)
        # At the last hand we have to draw the "briscola" card and notify that the deck is finished
        else:
            drawn_card = self.briscola
            self.drawn_cards.append(drawn_card)
        print("Self.drawn_cards: ", self.drawn_cards)
        return drawn_card

    @Pyro5.server.expose
    def get_drawn_cards(self):
        while len(self.drawn_cards) != 2:
            #print("Waiting for the drawn cards")
            # TODO: sleep
            pass
        drawn_cards = self.drawn_cards
        self.drawn_cards = []
        return drawn_cards


class Match:

    def __init__(self, first_player_id, dealer, dealer_uri):
        # TODO: controllare se queste variabili sono tutte utili
        self.first_player_id = first_player_id
        self.second_player_id = None
        self.dealer = dealer
        self.dealer_uri = dealer_uri

        #self.first_player_game_object = Pyro5.client.Proxy("PYRONAME:client.game." + str(self.first_player_id))
        #self.second_player_game_object = None

        self.second_player_played_card = None
        self.first_player_played_card = None

        # Synchronization variables
        self.p1_played_card_lock = threading.Lock()
        self.p2_played_card_lock = threading.Lock()

    def set_second_player_id(self, second_player_id):
        self.second_player_id = second_player_id

    #def set_second_player_register_play_proxy(self):
    #    self.second_player_game_object = Pyro5.client.Proxy("PYRONAME:client.game." + str(self.second_player_id))

    @Pyro5.server.expose
    def register_play(self, card_symbol, client_id):
        print("Thread: ", threading.current_thread())
        print("Carta giocata: ", card_symbol)
        if client_id == self.first_player_id:
            with self.p1_played_card_lock:
                self.first_player_played_card = card_symbol
                #self.second_player_game_object._pyroClaimOwnership()
                #print("Ownership claimed")
                #self.second_player_game_object(card_symbol)
        elif client_id == self.second_player_id:
            with self.p2_played_card_lock:
                self.second_player_played_card = card_symbol
                #self.first_player_game_object._pyroClaimOwnership()
                #self.first_player_game_object(card_symbol)
        print("FINE")

    @Pyro5.server.expose
    def get_adversary_played_card(self, client_id):
        if client_id == self.first_player_id:
            #while self.second_player_played_card is None:
            #    print("Waiting for second player's card")
            #    pass
            with self.p2_played_card_lock:
                second_player_played_card = self.second_player_played_card
                print("Second player played card: ", self.second_player_played_card)
                self.second_player_played_card = None
            return second_player_played_card
        elif client_id == self.second_player_id:
            with self.p1_played_card_lock:
                first_player_played_card = self.first_player_played_card
                print("First player played card: ", self.first_player_played_card)
                self.first_player_played_card = None
            return first_player_played_card

    @Pyro5.server.expose
    def get_match_id(self):
        # We consider the match ID as the id of the client that created it
        return self.first_player_id


   # @Pyro5.server.expose
   # def get_adversary_played_card(self, client_id):
   #     if client_id == self.first_player_id:
   #         while self.second_player_played_card is None:
   #             print("Waiting for second player card")
   #             pass
   #         print("Second player card arrived")
   #         return self.second_player_played_card
   #     else:



class MatchManager:

    def __init__(self):
        # List of the active matches
        self.created_matches = {}
        self.active_matches = {}

    @Pyro5.server.expose
    def new_match(self):
        """
        Creates a new Match object to which it passes a newly created Dealer object.
        :param client_id: id of the player (client) creating the new match
        """
        dealer = Dealer()
        dealer_uri = daemon.register(dealer)
        client_id = str(uuid.uuid4())
        match = Match(client_id, dealer, dealer_uri)
        print("new match object: ", match)
        match_uri = daemon.register(match)
        self.created_matches[client_id] = match
        print("Matches new match: ", self.created_matches)
        return client_id, dealer_uri, match_uri

    @Pyro5.server.expose
    def remove_created_match(self, match_id):
        print("self.created_matches: ", self.created_matches)
        print("MATCH: ", self.created_matches[match_id])
        del self.created_matches[match_id].dealer
        created_match = self.created_matches.pop(match_id)
        del created_match
        print("match deleted, self.created_matches: ", self.created_matches)

    @Pyro5.server.expose
    def remove_active_match(self, match_id):
        print("self.active_matches: ", self.active_matches)
        print("MATCH: ", self.active_matches[match_id])
        del self.active_matches[match_id].dealer
        active_match = self.active_matches.pop(match_id)
        del active_match
        print("match deleted, self.active_matches: ", self.active_matches)

    @Pyro5.server.expose
    def join_match(self):
        print("Join match method, created_matches: ", self.created_matches, ", len(self.created_matches): ", len(self.created_matches))
        if not len(self.created_matches) == 0:
            match = self.created_matches.pop(list(self.created_matches.keys())[0])
            print("Created matches: ", self.created_matches)
            print("Match: ", match)
            self.active_matches[match.first_player_id] = match
            client_id = str(uuid.uuid4())
            match.set_second_player_id(client_id)
            return client_id, match.dealer_uri, daemon.uriFor(match)
        else:
            print("ELSE")
            return None

    @Pyro5.server.expose
    def is_alive(self, match_id):
        if self.active_matches.get(match_id, False) == False:
            return False
        return True


match_manager = MatchManager()


def main():
    # dealer_uri = daemon.register(Dealer)
    # match_uri = daemon.register(Match)
    Pyro5.server.serve(
        {
            # Dealer: "server.dealer",
            match_manager: "server.match_manager_object",
        },
        daemon=daemon,
        use_ns=True,
        verbose=True,
    )
    # print("Warehouse uri: \n", dealer_uri)
    #
    # ns = Pyro5.core.locate_ns()
    # ns.register("server.dealer", dealer_uri)
    # ns.register("server.match", match_uri)

    # daemon.requestLoop()


if __name__ == '__main__':
    main()
