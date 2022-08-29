import Pyro5.server
import Pyro5.core
import Pyro5.client
import random


daemon = Pyro5.server.Daemon()  # make a Pyro daemon
ns = Pyro5.core.locate_ns()


@Pyro5.server.expose
class Dealer:
    card_suits = ['B', 'C', 'D', 'S']

    def __init__(self):
        self.deck = []
        self.briscola = None
        self.first_player_cards = []
        self.second_player_cards = []

    def create_deck(self):
        # Cards creation
        suits_index = 0
        for i in range(0, 40):
            self.deck.append(str(i % 10 + 1) + Dealer.card_suits[suits_index])
            if (i + 1) % 10 == 0:
                suits_index += 1

    def get_deck(self):
        return self.deck

    def deal(self, first_hand_player):

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

    def get_adversary_cards(self, first_hand_player):
        if not first_hand_player:
            return self.first_player_cards

        # Wait for the second player to call the dealer
        while len(self.second_player_cards) == 0:
            print("Waiting")
        return self.second_player_cards

    def set_briscola(self):
        rand_value = random.randint(0, len(self.deck) - 1)
        rand_card = self.deck.pop(rand_value)
        self.briscola = rand_card
        return rand_card

    def get_briscola(self):
        return self.briscola


class Match:

    def __init__(self, first_player_id, dealer, dealer_uri):
        self.first_player_id = first_player_id
        self.second_player_id = None
        self.dealer = dealer
        self.dealer_uri = dealer_uri


class MatchManager:

    def __init__(self):
        # List of the active matches
        self.matches = []

    @Pyro5.server.expose
    def new_match(self, client_id):
        """
        Creates a new Match object to which it passes a newly created Dealer object.
        :param client_id: id of the player (client) creating the new match
        """
        print("new match object: ", self)
        dealer = Dealer()
        print("Matches new match: ", self.matches)
        dealer_uri = daemon.register(dealer)
        match = Match(client_id, dealer, dealer_uri)
        self.matches.append(match)
        return dealer_uri
        # Pyro5.server.serve(
        #     {
        #         dealer: "server.dealer.1",
        #     },
        #     daemon=daemon,
        #     use_ns=True,
        #     verbose=True,
        # )
        print("After serve")

    @Pyro5.server.expose
    def remove_match(self, client_id):
        self.matches.remove(client_id)

    @Pyro5.server.expose
    def join_match(self):
        print("join match object: ", self)
        print("Matches: ", self.matches)
        if not len(self.matches) == 0:
            match = self.matches.pop(0)
            print("Match: ", match, "\n Dealer: ", match.dealer)
            return match.dealer_uri
        else:
            print("Errore: non ci sono match disponibili")
            # TODO: far tornare indietro il programma


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
