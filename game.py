import numpy as np
from random import randint
from random import shuffle
import copy
from make_models import make_models

class library:
    def __init__(self, pool=1):
        self.hand = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        self.on_show = []
        self.drop = []
        self.pool = pool
    def refresh(self):
        shuffle(self.hand)
    def place(self):
        draw = self.hand.pop()
        self.on_show.append(draw)
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
        self.currency_before = 4
        self.currency_after = 4
        self.draw_card = draw_card
        self.pool = pool
        self.big = big
        self.bet_decision = False
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
        self.bet_decision = True

def get_break_points(current_player, current_player_matrix, _1_player_matrix, _2_player_matrix, _3_player_matrix, _4_player_matrix, w,x,y,z):
    current_player_draw_or_not_samples = copy.deepcopy(current_player_matrix)
    current_player_discard_samples = copy.deepcopy(current_player_matrix)
    # 抓/翻模型断点
    if randint(0,1) == 1: #draw
        draw_in = deck.drawn()
        current_player.hand.append(draw_in)
        current_player_matrix[6] = 1
        current_player_matrix[7 + current_player.hand[0]] = 1
        current_player_matrix[7 + current_player.hand[1]] = 1
        _1_player_matrix[w] = 1
        _2_player_matrix[x] = 1
        _3_player_matrix[y] = 1
        _4_player_matrix[z] = 1
        current_player.sort()
        # 弃牌选择模型断点
        current_player_discard_option = randint(0,1) #discard
        if current_player_discard_option == 1: #discard big
            current_player_discard_samples = copy.deepcopy(current_player_matrix)
            current_player_matrix[7] = 1
            current_player.discard(big=1)
            current_player_matrix[7 + current_player.hand[0]] = 1
            current_player_matrix[7 + current_player.hand[-1]] = 0
            current_player_matrix[22 + current_player.drop[0]] = -1
        else: #discard small
            current_player_discard_samples = copy.deepcopy(current_player_matrix)
            current_player_matrix[7] = -1
            current_player.discard(big=0)
            current_player_matrix[7 + current_player.hand[0]] = 0
            current_player_matrix[7 + current_player.hand[-1]] = 1
            current_player_matrix[22 + current_player.drop[0]] = -1
    else:
        deck.replace() #replace
        current_player_matrix[101 + current_player.hand[0]] = 1
        for i in deck.drop:
            current_player_matrix[116 + i] = -1
        pass
    if current_player.drop != []:
        _1_player_matrix[41 + current_player.drop[0]] = 1
        _2_player_matrix[41 + current_player.drop[0]] = 1
        _3_player_matrix[41 + current_player.drop[0]] = 1
        _4_player_matrix[41 + current_player.drop[0]] = 1
    else:
        pass
    return current_player_draw_or_not_samples, current_player_discard_samples

def public_info(player_0_matrix, player_1_matrix, player_2_matrix, player_3_matrix, player_4_matrix): 
    # 汇总场上所有的公开信息给所有人
    # （小早川牌、小早川弃牌堆、所有人弃牌堆）
    player_0_matrix[101 + deck.on_show[0]] = 1
    player_1_matrix[101 + deck.on_show[0]] = 1
    player_2_matrix[101 + deck.on_show[0]] = 1
    player_3_matrix[101 + deck.on_show[0]] = 1
    player_4_matrix[101 + deck.on_show[0]] = 1
    if deck.drop != []:
        for x in deck.drop:
            player_0_matrix[116 + x] = -1
            player_1_matrix[116 + x] = -1
            player_2_matrix[116 + x] = -1
            player_3_matrix[116 + x] = -1
            player_4_matrix[116 + x] = -1
    if player_0.drop != []:
        player_1_matrix[38] = -1
        player_2_matrix[38] = -1
        player_3_matrix[38] = -1
        player_4_matrix[38] = -1
        for y in player_0.drop:
            player_1_matrix[116 + y] = -1
            player_2_matrix[116 + y] = -1
            player_3_matrix[116 + y] = -1
            player_4_matrix[116 + y] = -1
    if player_1.drop != []:
        player_0_matrix[38] = -1
        player_2_matrix[39] = -1
        player_3_matrix[39] = -1
        player_4_matrix[39] = -1
        for y in player_0.drop:
            player_0_matrix[116 + y] = -1
            player_2_matrix[116 + y] = -1
            player_3_matrix[116 + y] = -1
            player_4_matrix[116 + y] = -1
    if player_2.drop != []:
        player_0_matrix[39] = -1
        player_1_matrix[39] = -1
        player_3_matrix[40] = -1
        player_4_matrix[40] = -1
        for y in player_0.drop:
            player_0_matrix[116 + y] = -1
            player_1_matrix[116 + y] = -1
            player_3_matrix[116 + y] = -1
            player_4_matrix[116 + y] = -1
    if player_3.drop != []:
        player_0_matrix[40] = -1
        player_1_matrix[40] = -1
        player_2_matrix[40] = -1
        player_4_matrix[41] = -1
        for y in player_0.drop:
            player_0_matrix[116 + y] = -1
            player_1_matrix[116 + y] = -1
            player_2_matrix[116 + y] = -1
            player_4_matrix[116 + y] = -1
    if player_4.drop != []:
        player_0_matrix[41] = -1
        player_1_matrix[41] = -1
        player_2_matrix[41] = -1
        player_3_matrix[41] = -1
        for y in player_0.drop:
            player_0_matrix[116 + y] = -1
            player_1_matrix[116 + y] = -1
            player_2_matrix[116 + y] = -1
            player_3_matrix[116 + y] = -1
    # 计算每个人的牌库推测
def library_assumption(player_0, player_0_matrix,  player_1, player_2, player_3, player_4):
    player_0_matrix[131 + player_0.hand[0]] =  1 #0
    player_0_matrix[131 + deck.on_show[0]] = 1 #0
    if deck.drop != []:
        for x in range(len(deck.drop)):
            player_0_matrix[131 + deck.drop[x]] = -1 #-1
    if player_0.drop != []: player_0_matrix[131 + player_0.drop[0]] = -1
    if player_1.drop != []: player_0_matrix[131 + player_1.drop[0]] = -1
    if player_2.drop != []: player_0_matrix[131 + player_2.drop[0]] = -1
    if player_3.drop != []: player_0_matrix[131 + player_3.drop[0]] = -1
    if player_4.drop != []: player_0_matrix[131 + player_4.drop[0]] = -1
    return player_0_matrix

def process_final_open(final_open):
    if len(final_open) == 0:
        return None
    elif len(final_open) == 1:
        return None
    else:
        min_player_key = min(final_open, key=lambda k: final_open[k])
        max_player_key = max(final_open, key=lambda k: final_open[k])
        min_player_value = final_open[min_player_key]
        max_player_value = final_open[max_player_key]
        if min_player_value + deck.on_show[0] >= max_player_value:
            return min_player_key
        else:
            return max_player_key

if __name__ == '__main__':
    rounds = 0
    draw_or_not_samples = []
    discard_samples = []
    bet_or_not_samples = []
    net_incomes = []
    while rounds< 1000:
        rounds += 1
        blind = 1
        player_0 = player()
        player_1 = player()
        player_2 = player()
        player_3 = player()
        player_4 = player()
        # initialize game
        deck = library(pool = 1)
        deck.refresh()
        # set the matrice
        player_0_matrix = [0 for i in range(153)]
        player_1_matrix = [0 for i in range(153)]
        player_2_matrix = [0 for i in range(153)]
        player_3_matrix = [0 for i in range(153)]
        player_4_matrix = [0 for i in range(153)]
        # self order: 0~4, change or not: 5, draw or not: 6, self discard: 7, hand: 8~22
        # discard: 23~37, others draw or not: 38~41, others discard: 42~56, 57~71, 72~86, 87~101
        # public card: 102~116, public discard: 117~131, library left: 132~146 self bet or not: 147
        # others bet or not: 148~151 #games left:152
        # start to play
        player_0_matrix[0] = 1
        player_1_matrix[1] = 1
        player_2_matrix[2] = 1
        player_3_matrix[3] = 1
        player_4_matrix[4] = 1
        print ("开始游戏")
        deck.place()
        player_0_matrix[101 + deck.on_show[0]] = 1
        player_1_matrix[101 + deck.on_show[0]] = 1
        player_2_matrix[101 + deck.on_show[0]] = 1
        player_3_matrix[101 + deck.on_show[0]] = 1
        player_4_matrix[101 + deck.on_show[0]] = 1
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
        player_0_draw_or_not_samples, player_0_discard_samples = get_break_points(player_0, player_0_matrix, player_1_matrix, player_2_matrix, player_3_matrix, player_4_matrix, 38, 38, 38, 38)
        player_1_draw_or_not_samples, player_1_discard_samples = get_break_points(player_1, player_1_matrix, player_0_matrix, player_2_matrix, player_3_matrix, player_4_matrix, 38, 39, 39, 39)
        player_2_draw_or_not_samples, player_2_discard_samples = get_break_points(player_2, player_2_matrix, player_0_matrix, player_1_matrix, player_3_matrix, player_4_matrix, 39, 39, 40, 40)
        player_3_draw_or_not_samples, player_3_discard_samples = get_break_points(player_3, player_3_matrix, player_0_matrix, player_1_matrix, player_2_matrix, player_4_matrix, 40, 40, 40, 41)
        player_4_draw_or_not_samples, player_4_discard_samples = get_break_points(player_4, player_4_matrix, player_0_matrix, player_1_matrix, player_2_matrix, player_3_matrix, 41, 41, 41, 41)
        print ("牌库剩余：", deck.hand)
        print ("总弃牌堆：", deck.drop)
        # 汇总场上所有的公开信息给所有人 （小早川牌、小早川弃牌堆、所有人弃牌堆）
        # 计算每个人的牌库推测
        public_info(player_0_matrix, player_1_matrix, player_2_matrix, player_3_matrix, player_4_matrix)
        player_0_library_assumption = library_assumption(player_0, player_0_matrix,  player_1, player_2, player_3, player_4)
        player_1_library_assumption = library_assumption(player_1, player_1_matrix,  player_0, player_2, player_3, player_4)
        player_2_library_assumption = library_assumption(player_2, player_2_matrix,  player_0, player_1, player_3, player_4)
        player_3_library_assumption = library_assumption(player_3, player_3_matrix,  player_0, player_1, player_2, player_4)
        player_4_library_assumption = library_assumption(player_4, player_4_matrix,  player_0, player_1, player_2, player_3)
        player_0_matrix = copy.deepcopy(player_0_library_assumption)
        player_1_matrix = copy.deepcopy(player_1_library_assumption)
        player_2_matrix = copy.deepcopy(player_2_library_assumption)
        player_3_matrix = copy.deepcopy(player_3_library_assumption)
        player_4_matrix = copy.deepcopy(player_4_library_assumption)
        # player 0 bet or not
        # print (blind)
        if randint(0,1) == 1: #bet
            player_0.bet()
            # print ("player_0: bet")
            player_0.currency_after -= blind
            deck.pool += blind
            player_0_matrix[147] = blind
            player_1_matrix[148] = blind
            player_2_matrix[148] = blind
            player_3_matrix[148] = blind
            player_4_matrix[148] = blind
        else:
            pass
        player_0_bet_or_not_samples = copy.deepcopy(player_0_matrix)
        # player 1 bet or not
        if randint(0,1) == 1: #bet
            player_1.bet()
            player_1.currency_after -= blind
            deck.pool += blind
            player_1_matrix[147] = blind
            player_0_matrix[148] = blind
            player_2_matrix[149] = blind
            player_3_matrix[149] = blind
            player_4_matrix[149] = blind
        else:
            pass
        player_1_bet_or_not_samples = copy.deepcopy(player_1_matrix)
        # player 2 bet or not
        if randint(0,1) == 1: #bet
            player_2.bet()
            player_2.currency_after -= blind
            deck.pool += blind
            player_2_matrix[147] = blind
            player_0_matrix[149] = blind
            player_1_matrix[149] = blind
            player_3_matrix[150] = blind
            player_4_matrix[150] = blind
        else:
            pass
        player_2_bet_or_not_samples = copy.deepcopy(player_2_matrix)
        #player 3 
        if randint(0,1) == 1: #bet
            player_3.bet()
            player_3.currency_after -= blind
            deck.pool += blind
            player_3_matrix[147] = blind
            player_0_matrix[150] = blind
            player_1_matrix[150] = blind
            player_2_matrix[150] = blind
            player_4_matrix[151] = blind
        else:
            pass
        player_3_bet_or_not_samples = copy.deepcopy(player_3_matrix)
        # player 4
        if randint(0,1) == 1: #bet
            player_4.bet()
            player_4.currency_after -= blind
            deck.pool += blind
            player_4_matrix[147] = blind
            player_0_matrix[151] = blind
            player_1_matrix[151] = blind
            player_2_matrix[151] = blind
            player_3_matrix[151] = blind
        else:
            pass
        player_4_bet_or_not_samples = copy.deepcopy(player_4_matrix)
        # 下注逻辑
        # 下注模型断点
        final_open = {}
        # print (player_0.hand[0])
        if player_0.bet_decision == True:
            final_open['player_0'] = player_0.hand[0]
        if player_1.bet_decision == True:
            final_open['player_1'] = player_1.hand[0]
        if player_2.bet_decision == True:
            final_open['player_2'] = player_2.hand[0]
        if player_3.bet_decision == True:
            final_open['player_3'] = player_3.hand[0]
        if player_4.bet_decision == True:
            final_open['player_4'] = player_4.hand[0]
        result = process_final_open(final_open)
        if result is None:
            player_0.currency_after = player_0.currency_before
            player_1.currency_after = player_1.currency_before
            player_2.currency_after = player_2.currency_before
            player_3.currency_after = player_3.currency_before
            player_4.currency_after = player_4.currency_before
        elif result == 'player_0':
            player_0.currency_after += deck.pool
        elif result == 'player_1':
            player_1.currency_after += deck.pool
        elif result == 'player_2':
            player_2.currency_after += deck.pool
        elif result == 'player_3':
            player_3.currency_after += deck.pool
        elif result == 'player_4':
            player_4.currency_after += deck.pool
        player_0_net_income = player_0.currency_after - player_0.currency_before
        player_1_net_income = player_1.currency_after - player_1.currency_before
        player_2_net_income = player_2.currency_after - player_2.currency_before
        player_3_net_income = player_3.currency_after - player_3.currency_before
        player_4_net_income = player_4.currency_after - player_4.currency_before
        player_0.currency_before == player_0.currency_after
        player_1.currency_before == player_1.currency_after
        player_2.currency_before == player_2.currency_after
        player_3.currency_before == player_3.currency_after
        player_4.currency_before == player_4.currency_after
        draw_or_not_samples.append(player_0_draw_or_not_samples)
        discard_samples.append(player_0_discard_samples)
        bet_or_not_samples.append(player_0_bet_or_not_samples)
        net_incomes.append(player_0_net_income)
        draw_or_not_samples.append(player_1_draw_or_not_samples)
        discard_samples.append(player_1_discard_samples)
        bet_or_not_samples.append(player_1_bet_or_not_samples)
        net_incomes.append(player_1_net_income)
        draw_or_not_samples.append(player_2_draw_or_not_samples)
        discard_samples.append(player_2_discard_samples)
        bet_or_not_samples.append(player_2_bet_or_not_samples)
        net_incomes.append(player_2_net_income)
        draw_or_not_samples.append(player_3_draw_or_not_samples)
        discard_samples.append(player_3_discard_samples)
        bet_or_not_samples.append(player_3_bet_or_not_samples)
        net_incomes.append(player_3_net_income)
        draw_or_not_samples.append(player_4_draw_or_not_samples)
        discard_samples.append(player_4_discard_samples)
        bet_or_not_samples.append(player_4_bet_or_not_samples)
        net_incomes.append(player_4_net_income)
    print("start train.")
    model_draw, model_discard, model_bet = make_models()
    model_draw.fit(draw_or_not_samples, net_incomes, epochs=200, verbose=0)
    model_discard.fit(discard_samples, net_incomes, epochs=200, verbose=0)
    model_bet.fit(bet_or_not_samples, net_incomes, epochs=200, verbose=0)
    print("end train.")