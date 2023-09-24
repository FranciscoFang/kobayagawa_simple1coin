import numpy as np
from random import randint
from random import shuffle
import copy

class library:
    def __init__(self):
        self.hand = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        self.on_show = []
        self.drop = []
    def refresh(self):
        shuffle(self.hand)
    def place(self):
        draw = self.hand.pop()
        self.on_show.append(draw)
        return self.on_show
    def replace(self):
        draw = self.hand.pop()
        self.drop.append(self.on_show.pop())
        self.on_show.append(draw)
    def drawn(self):
        return self.hand.pop()

class player():
    def __init__(self, draw_card = -1, pool = 0, big:int = -2):
        self.hand = []
        self.drop = []
        self.currency_before = 8
        self.currency_after = 8
        self.draw_card = draw_card
        self.pool = pool
        self.big = big
    def draw(self, draw_card):
        self.hand.append(draw_card)
    def sort(self):
        self.hand.sort()
    def discard(self, big:int):
        if big == 1:
            _return = self.hand.pop(-1)
            self.drop.append(_return)
            return _return
        else:
            _return = self.hand.pop(0)
            self.drop.append(_return)
            return _return
    def replace_hand(self, big:int):
        self.draw()
        self.discard(big)
    def bet(self):
        self.currency_after -= 1
    def lost(self):
        self.currency_before = self.currency_after
    def win(self, pool):
        self.currency_after += pool
    def organize_net_income(self):
        self.net_income = self.currency_after - self.currency_before
        self.currency_before = self.currency_after
        return self.net_income

def get_break_points(current_player, current_player_matrix, _1_player_matrix, _2_player_matrix, _3_player_matrix, _4_player_matrix):
    current_player_draw_or_not_samples = copy.deepcopy(current_player_matrix)
    current_player_discard_samples = []
    # 抓/翻模型断点
    if randint(0,1) == 1: #draw
        draw_in = deck.drawn()
        current_player.hand.append(draw_in)
        current_player_matrix[6] = 1
        current_player_matrix[7 + current_player.hand[0]] = 1
        current_player_matrix[7 + current_player.hand[1]] = 1
        current_player_discard_samples = copy.deepcopy(current_player_matrix)
        current_player.sort()
        # 弃牌选择模型断点
        current_player_discard_option = randint(0,1) #discard
        if current_player_discard_option == 1: #discard big
            current_player_matrix[7] = 1
            current_player_matrix[7 + current_player.hand[0]] = 1
            current_player_matrix[7 + current_player.hand[-1]] = 0
            current_player.discard(big=1)
            current_player_matrix[22 + current_player.drop[0]] = -1
        else: #discard small
            current_player_matrix[7] = -1
            current_player_matrix[7 + current_player.hand[0]] = 0
            current_player_matrix[7 + current_player.hand[-1]] = 1
            current_player.discard(big=0)
            current_player_matrix[22 + current_player.drop[0]] = -1
    else:
        deck.replace() #replace
        current_player_matrix[101 + current_player.hand[0]] = 1
        for i in deck.drop:
            current_player_matrix[116 + i] = -1
        pass
    if current_player.drop != []:
        _1_player_matrix[38] = 1
        _2_player_matrix[38] = 1
        _3_player_matrix[38] = 1
        _4_player_matrix[38] = 1
        _1_player_matrix[41 + current_player.drop[0]] = 1
        _2_player_matrix[41 + current_player.drop[0]] = 1
        _3_player_matrix[41 + current_player.drop[0]] = 1
        _4_player_matrix[41 + current_player.drop[0]] = 1
    else:
        _1_player_matrix[38] = 0
        _2_player_matrix[38] = 0
        _3_player_matrix[38] = 0
        _4_player_matrix[38] = 0
    print ("当前的小早川牌是:", deck.on_show[0])
    return current_player_draw_or_not_samples, current_player_discard_samples

if __name__ == '__main__':
    player_0 = player()
    player_1 = player()
    player_2 = player()
    player_3 = player()
    player_4 = player()
    # initialize game
    deck = library()
    deck.refresh()
    # set the matrice
    player_0_matrix = [0 for i in range(146)]
    player_1_matrix = [0 for i in range(146)]
    player_2_matrix = [0 for i in range(146)]
    player_3_matrix = [0 for i in range(146)]
    player_4_matrix = [0 for i in range(146)]
    player_0_matrix[0] = 1
    player_1_matrix[1] = 1
    player_2_matrix[2] = 1
    player_3_matrix[3] = 1
    player_4_matrix[4] = 1
    # self order: 0~4, change or not: 5, draw or not: 6, self discard: 7, hand: 8~22
    # discard: 23~37, others keep or not: 38~41, others discard: 42~56, 57~71, 72~86, 87~101
    # public card: 102~116, public discard: 117~131, library left: 132~146
    # start to play
    print ("开始游戏")
    public_card = deck.place()
    player_0_matrix[101 + public_card[0]] = 1
    player_1_matrix[101 + public_card[0]] = 1
    player_2_matrix[101 + public_card[0]] = 1
    player_3_matrix[101 + public_card[0]] = 1
    player_4_matrix[101 + public_card[0]] = 1
    player_0.draw(deck.drawn())
    player_1.draw(deck.drawn())
    player_2.draw(deck.drawn())
    player_3.draw(deck.drawn())
    player_4.draw(deck.drawn())
    player_0_matrix[7 + player_0.hand[0]] = 1
    player_1_matrix[7 + player_1.hand[0]] = 1
    player_2_matrix[7 + player_2.hand[0]] = 1
    player_3_matrix[7 + player_3.hand[0]] = 1
    player_4_matrix[7 + player_4.hand[0]] = 1
    player_0_draw_or_not_samples, player_0_discard_samples = get_break_points(player_0, player_0_matrix, player_1_matrix, player_2_matrix, player_3_matrix, player_4_matrix)
    player_1_draw_or_not_samples, player_1_discard_samples = get_break_points(player_1, player_1_matrix, player_0_matrix, player_2_matrix, player_3_matrix, player_4_matrix)
    player_2_draw_or_not_samples, player_2_discard_samples = get_break_points(player_2, player_2_matrix, player_0_matrix, player_1_matrix, player_3_matrix, player_4_matrix)
    player_3_draw_or_not_samples, player_3_discard_samples = get_break_points(player_3, player_3_matrix, player_0_matrix, player_1_matrix, player_2_matrix, player_4_matrix)
    player_4_draw_or_not_samples, player_4_discard_samples = get_break_points(player_4, player_4_matrix, player_0_matrix, player_1_matrix, player_2_matrix, player_3_matrix)
    print ("牌库剩余：", deck.hand)
    print ("总弃牌堆：", deck.drop)
    
    # 汇总场上所有的公开信息给所有人
    # （小早川牌、小早川弃牌堆、所有人弃牌堆）
    # 计算每个人的牌库推测
    
    # 下注逻辑
    # 下注模型断点
    
    # player_0
    # player_1
    # player_2
    # player_3
    # player_4

    # 开牌
    # 计算收益并汇总成训练样本