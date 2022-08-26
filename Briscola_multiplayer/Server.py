import Pyro5.server
import Pyro5.core
import random

@Pyro5.server.expose
class Dealer:
    card_suits = ['B', 'C', 'D', 'S']

    def __init__(self):
        self.deck = []

    def create_deck(self):
        # Cards creation
        suits_index = 0
        for i in range(0, 40):
            deck_key = str(i % 10 + 1) + Dealer.card_suits[i // 10]
            # print("deck_key: ", deck_key)
            # print("Suit index: ", suits_index)
            self.deck.append(str(i % 10 + 1) + Dealer.card_suits[suits_index])
            if (i + 1) % 10 == 0:
                suits_index += 1

    def get_deck(self):
        return self.deck

    def deal(self, player):
        # Pop 3 random cards from the deck
        rand_card_1 = self.deck.pop(random.choice(list(self.deck.keys())))
        rand_card_2 = self.deck.pop(random.choice(list(self.deck.keys())))
        rand_card_3 = self.deck.pop(random.choice(list(self.deck.keys())))

        # Deal the cards
        rand_card_1.set_target_position(player.hand_positions[0], dealing=True)
        rand_card_2.set_target_position(player.hand_positions[1], dealing=True)
        rand_card_3.set_target_position(player.hand_positions[2], dealing=True)

        # Assign cards to player
        player.cards_in_hand = [rand_card_1, rand_card_2, rand_card_3]

    def set_briscola(self):
        rand_value = random.randint(0, len(self.deck)-1)
        rand_card = self.deck.pop(rand_value)
        return rand_card

def main():
    daemon = Pyro5.server.Daemon()  # make a Pyro daemon
    uri = daemon.register(Dealer)
    print("Warehouse uri: \n", uri)

    ns = Pyro5.core.locate_ns()
    ns.register("server.dealer", uri)

    daemon.requestLoop()


if __name__ == '__main__':
    main()