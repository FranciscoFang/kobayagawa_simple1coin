from random import randint
import numpy as np
from random import shuffle
import copy
from make_models import make_draw_model
import time

# p0_draw = 0
# p0_replace = 0
# p0_wins = 0
# p0_replace = 0

def get_break_points(current_player, _1_player, _2_player, _3_player, _4_player, w,x,y,z):
    current_player_draw_or_not_samples = copy.deepcopy(current_player.matrix)
    current_player_discard_samples = copy.deepcopy(current_player.matrix)
    # 抓/翻模型断点
    current_player_draw_option = randint(0,1)
    if current_player_draw_option == 1: #draw
        draw_in = deck.drawn()
        current_player.hand.append(draw_in)
        current_player.matrix[6] = 1
        current_player.matrix[7 + current_player.hand[0]] = 1
        current_player.matrix[7 + current_player.hand[1]] = 1
        _1_player.matrix[w] = 1
        _2_player.matrix[x] = 1
        _3_player.matrix[y] = 1
        _4_player.matrix[z] = 1
        current_player.hand.sort()
        # 弃牌选择模型断点
        current_player_discard_option = randint(0,1) #discard
        if current_player_discard_option == 1: #discard big
            current_player_discard_samples = copy.deepcopy(current_player.matrix)
            current_player.matrix[7] = 1
            current_player.discard(big=1)
            current_player.matrix[7 + current_player.hand[0]] = 1
            current_player.matrix[7 + current_player.hand[-1]] = 0
            current_player.matrix[22 + current_player.drop[0]] = -1
        else: #discard small
            current_player_discard_samples = copy.deepcopy(current_player.matrix)
            current_player.matrix[7] = -1
            current_player.discard(big=0)
            current_player.matrix[7 + current_player.hand[0]] = 0
            current_player.matrix[7 + current_player.hand[-1]] = 1
            current_player.matrix[22 + current_player.drop[0]] = -1
    else:
        deck.replace() #replace
        current_player.matrix[101 + current_player.hand[0]] = 1
        for i in deck.drop:
            current_player.matrix[116 + i] = -1
        pass
    if current_player.drop != []:
        _1_player.matrix[41 + current_player.drop[0]] = 1
        _2_player.matrix[41 + current_player.drop[0]] = 1
        _3_player.matrix[41 + current_player.drop[0]] = 1
        _4_player.matrix[41 + current_player.drop[0]] = 1
    else:
        pass
    return current_player_draw_or_not_samples, current_player_discard_samples

def get_breakp_value(current_player, _1_player, _2_player, _3_player, _4_player, w,x,y,z):
    current_player_draw_or_not_samples = copy.deepcopy(current_player.matrix)
    current_player_discard_samples = copy.deepcopy(current_player.matrix)
    # 抓/翻模型断点
    current_player_draw_option = calc_draw(current_player)
    if current_player_draw_option == 1: #draw
        draw_in = deck.drawn()
        current_player.hand.append(draw_in)
        current_player.matrix[6] = 1
        current_player.matrix[7 + current_player.hand[0]] = 1
        current_player.matrix[7 + current_player.hand[1]] = 1
        _1_player.matrix[w] = 1
        _2_player.matrix[x] = 1
        _3_player.matrix[y] = 1
        _4_player.matrix[z] = 1
        current_player.hand.sort()
        # 弃牌选择模型断点
        current_player_discard_option = randint(0,1) #discard
        if current_player_discard_option == 1: #discard big
            current_player_discard_samples = copy.deepcopy(current_player.matrix)
            current_player.matrix[7] = 1
            current_player.discard(big=1)
            current_player.matrix[7 + current_player.hand[0]] = 1
            current_player.matrix[7 + current_player.hand[-1]] = 0
            current_player.matrix[22 + current_player.drop[0]] = -1
        else: #discard small
            current_player_discard_samples = copy.deepcopy(current_player.matrix)
            current_player.matrix[7] = -1
            current_player.discard(big=0)
            current_player.matrix[7 + current_player.hand[0]] = 0
            current_player.matrix[7 + current_player.hand[-1]] = 1
            current_player.matrix[22 + current_player.drop[0]] = -1
    else:
        deck.replace() #replace
        current_player.matrix[101 + current_player.hand[0]] = 1
        for i in deck.drop:
            current_player.matrix[116 + i] = -1
        pass
    if current_player.drop != []:
        _1_player.matrix[41 + current_player.drop[0]] = 1
        _2_player.matrix[41 + current_player.drop[0]] = 1
        _3_player.matrix[41 + current_player.drop[0]] = 1
        _4_player.matrix[41 + current_player.drop[0]] = 1
    else:
        pass
    return current_player_draw_or_not_samples, current_player_discard_samples

def calc_draw(current_player):
    # global p0_draw
    # global p0_replace
    current_player_matrix_0 = copy.deepcopy(current_player.matrix)
    current_player_matrix_1 = copy.deepcopy(current_player.matrix)
    current_player_matrix_0[6] = 0
    current_player_matrix_1[6] = 1
    pred_0 = 0
    pred_1 = 0
    #0 部分采样 10
    # print ([current_player_matrix_0])
    # for i in range(8,23):
    #     if current_player_matrix_0[i] == 1:
    #         print ("current hand:", i-7)
    # for i in range(102,117):
    #     if current_player_matrix_0[i] == 1:
    #         print ("current on show:", i-101)
    prediction_draw_0 = model_draw.predict([current_player_matrix_0])
    pred_0 += prediction_draw_0[0]
    prediction_draw_1 = model_draw.predict([current_player_matrix_1])
    pred_1 += prediction_draw_1[0]
    print (pred_0[0])
    print (pred_1[0])
    if pred_1>=pred_0: 
        print(current_player.name, " should draw.")
        # p0_draw += 1
        return 1
    else: 
        print(current_player.name, " should replace.")
        # p0_replace += 1
        return 0

def first_card(player_0):
    player_0.matrix[101 + deck.on_show[0]] = 1

def public_info(player_0, player_1, player_2, player_3, player_4, w, x, y, z): 
    # 汇总场上所有的公开信息给所有人
    # （小早川牌、小早川弃牌堆、所有人弃牌堆）
    player_0.matrix[101 + deck.on_show[0]] = 1
    if deck.drop != []:
        for x in deck.drop:
            player_0.matrix[116 + x] = -1
    if player_0.drop != []:
        player_1.matrix[w] = -1
        player_2.matrix[x] = -1
        player_3.matrix[y] = -1
        player_4.matrix[z] = -1
        for loc_ in player_0.drop:
            player_1.matrix[116 + loc_] = -1
            player_2.matrix[116 + loc_] = -1
            player_3.matrix[116 + loc_] = -1
            player_4.matrix[116 + loc_] = -1
    # 计算每个人的牌库推测
def library_assumption(player_0, player_1, player_2, player_3, player_4):
    player_0.matrix[131 + player_0.hand[0]] =  1 #0
    player_0.matrix[131 + deck.on_show[0]] = 1 #0
    if deck.drop != []:
        for x in range(len(deck.drop)):
            player_0.matrix[131 + deck.drop[x]] = -1 #-1
    if player_0.drop != []: player_0.matrix[131 + player_0.drop[0]] = -1
    if player_1.drop != []: player_0.matrix[131 + player_1.drop[0]] = -1
    if player_2.drop != []: player_0.matrix[131 + player_2.drop[0]] = -1
    if player_3.drop != []: player_0.matrix[131 + player_3.drop[0]] = -1
    if player_4.drop != []: player_0.matrix[131 + player_4.drop[0]] = -1
    
def bet_step(player_0, player_1, player_2, player_3, player_4, blind, w, x, y, z):
    if randint(0,1) == 1:
        player_0.bet()
        player_0.bet_decision == True
        player_0.currency_after -= blind
        deck.pool += blind
        player_0.matrix[147] = blind
        player_1.matrix[w] = blind
        player_2.matrix[x] = blind
        player_3.matrix[y] = blind
        player_4.matrix[z] = blind
        # print ("", player_0.name, "bets.")
        # print (player_0.matrix[147])
    else:
        pass

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

def bet_summary(player):
    if player.bet_decision == True: final_open[player.name] = player.hand[0]
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

    # self order*abandoned: 0~4, change or not: 5, draw or not: 6, self discard: 7, hand: 8~22
    # discard: 23~37, others keep or not: 38~41, others discard: 42~56, 57~71, 72~86, 87~101
    # public card: 102~116, public discard: 117~131, library left: 132~146 self bet or not: 147
    # others bet or not: 148~151 #games left:152
    # start to play
class player():
    def __init__(self, draw_card = -1, pool = 0, big:int = -2, name_=''):
        self.hand = []
        self.drop = []
        self.currency_before = 4
        self.currency_after = 4
        self.draw_card = draw_card
        self.pool = pool
        self.big = big
        self.bet_decision = False
        self.matrix = [0 for i in range(153)]
        self.name = name_
        self.net_income = self.currency_after - self.currency_before
    def draw(self, draw_card: int):
        self.hand.append(draw_card)
        self.matrix[7 + self.hand[0]] = 1
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
    def order(self, number: int):
        self.matrix[number] = 1
    def draw_game(self):
        self.currency_after = self.currency_before
    def temp_reset(self):
        self.currency_before = self.currency_after

if __name__ == '__main__':
    rounds = 0
    random_samples = False
    model_draw = make_draw_model()
    print("model made.")
    p0w = 0
    p1w = 0
    p2w = 0
    p3w = 0
    p4w = 0
    p0_draw_or_not_samples = []
    p0_discard_samples = []
    p0_bet_or_not_samples = []
    p0_net_incomes = []
    p1_draw_or_not_samples = []
    p1_discard_samples = []
    p1_bet_or_not_samples = []
    p1_net_incomes = []
    p2_draw_or_not_samples = []
    p2_discard_samples = []
    p2_bet_or_not_samples = []
    p2_net_incomes = []
    p3_draw_or_not_samples = []
    p3_discard_samples = []
    p3_bet_or_not_samples = []
    p3_net_incomes = []
    p4_draw_or_not_samples = []
    p4_discard_samples = []
    p4_bet_or_not_samples = []
    p4_net_incomes = []
    winner_draw_or_not_samples = []
    winner_discard_samples = []
    winner_bet_or_not_samples = []
    winner_net_incomes = []
    while rounds< 10100:
        # while winner_draw_or_not_samples == []:
        rounds += 1
        blind = 1
        player_0 = player(name_='player_0')
        player_1 = player(name_='player_1')
        player_2 = player(name_='player_2')
        player_3 = player(name_='player_3')
        player_4 = player(name_='player_4')
        # initialize game
        deck = library(pool = 1)
        deck.refresh()
        # set the matrice
        # start to play
        # player_0.order(0)
        # player_1.order(1)
        # player_2.order(2)
        # player_3.order(3)
        # player_4.order(4)
        # print ("开始游戏")
        deck.place()
        first_card(player_0)
        first_card(player_1)
        first_card(player_2)
        first_card(player_3)
        first_card(player_4)
        player_0.draw(deck.drawn())
        player_1.draw(deck.drawn())
        player_2.draw(deck.drawn())
        player_3.draw(deck.drawn())
        player_4.draw(deck.drawn())
        if random_samples == False: #rounds <= 1000 or 
            player_0_draw_or_not_samples, player_0_discard_samples = get_break_points(player_0, player_1, player_2, player_3, player_4, 38, 38, 38, 38)
            player_1_draw_or_not_samples, player_1_discard_samples = get_break_points(player_1, player_0, player_2, player_3, player_4, 38, 39, 39, 39)
            player_2_draw_or_not_samples, player_2_discard_samples = get_break_points(player_2, player_0, player_1, player_3, player_4, 39, 39, 40, 40)
            player_3_draw_or_not_samples, player_3_discard_samples = get_break_points(player_3, player_0, player_1, player_2, player_4, 40, 40, 40, 41)
            player_4_draw_or_not_samples, player_4_discard_samples = get_break_points(player_4, player_0, player_1, player_2, player_3, 41, 41, 41, 41)
        elif rounds > 1001 and rounds <= 10000 and random_samples == True:
            player_0_draw_or_not_samples, player_0_discard_samples = get_breakp_value(player_0, player_1, player_2, player_3, player_4, 38, 38, 38, 38)
            player_1_draw_or_not_samples, player_1_discard_samples = get_breakp_value(player_1, player_0, player_2, player_3, player_4, 38, 39, 39, 39)
            player_2_draw_or_not_samples, player_2_discard_samples = get_breakp_value(player_2, player_0, player_1, player_3, player_4, 39, 39, 40, 40)
            player_3_draw_or_not_samples, player_3_discard_samples = get_breakp_value(player_3, player_0, player_1, player_2, player_4, 40, 40, 40, 41)
            player_4_draw_or_not_samples, player_4_discard_samples = get_breakp_value(player_4, player_0, player_1, player_2, player_3, 41, 41, 41, 41)
        else:
            player_0_draw_or_not_samples, player_0_discard_samples = get_breakp_value(player_0, player_1, player_2, player_3, player_4, 38, 38, 38, 38)
            player_1_draw_or_not_samples, player_1_discard_samples = get_break_points(player_1, player_0, player_2, player_3, player_4, 38, 39, 39, 39)
            player_2_draw_or_not_samples, player_2_discard_samples = get_break_points(player_2, player_0, player_1, player_3, player_4, 39, 39, 40, 40)
            player_3_draw_or_not_samples, player_3_discard_samples = get_break_points(player_3, player_0, player_1, player_2, player_4, 40, 40, 40, 41)
            player_4_draw_or_not_samples, player_4_discard_samples = get_break_points(player_4, player_0, player_1, player_2, player_3, 41, 41, 41, 41)
        # print ("牌库剩余：", deck.hand)
        # print ("总弃牌堆：", deck.drop)
        # 汇总场上所有的公开信息给所有人 （小早川牌、小早川弃牌堆、所有人弃牌堆）
        # 计算每个人的牌库推测
        public_info(player_0, player_1, player_2, player_3, player_4, 38, 38, 38, 38)
        public_info(player_1, player_0, player_2, player_3, player_4, 38, 39, 39, 39)
        public_info(player_2, player_0, player_1, player_3, player_4, 39, 39, 40, 40)
        public_info(player_3, player_0, player_1, player_2, player_4, 40, 40, 40, 41)
        public_info(player_4, player_0, player_1, player_2, player_3, 41, 41, 41, 41)
        library_assumption(player_0, player_1, player_2, player_3, player_4)
        library_assumption(player_1, player_0, player_2, player_3, player_4)
        library_assumption(player_2, player_0, player_1, player_3, player_4)
        library_assumption(player_3, player_0, player_1, player_2, player_4)
        library_assumption(player_4, player_0, player_1, player_2, player_3)
        # player 0 bet or not
        bet_step(player_0, player_1, player_2, player_3, player_4, blind, 148, 148, 148, 148)
        player_0_bet_or_not_samples = copy.deepcopy(player_0.matrix)
        bet_step(player_1, player_0, player_2, player_3, player_4, blind, 148, 149, 149, 149)
        player_1_bet_or_not_samples = copy.deepcopy(player_1.matrix)
        bet_step(player_2, player_0, player_1, player_3, player_4, blind, 149, 149, 150, 150)
        player_2_bet_or_not_samples = copy.deepcopy(player_2.matrix)
        bet_step(player_3, player_0, player_1, player_2, player_4, blind, 150, 150, 150, 151)
        player_3_bet_or_not_samples = copy.deepcopy(player_3.matrix)
        bet_step(player_4, player_0, player_1, player_2, player_3, blind, 151, 151, 151, 151)
        player_4_bet_or_not_samples = copy.deepcopy(player_4.matrix)
        # 下注逻辑
        # 下注模型断点
        final_open = {}
        bet_summary(player_0)
        bet_summary(player_1)
        bet_summary(player_2)
        bet_summary(player_3)
        bet_summary(player_4)
        result = process_final_open(final_open)
        if result is None:
            player_0.draw_game()
            player_1.draw_game()
            player_2.draw_game()
            player_3.draw_game()
            player_4.draw_game()
        elif result == 'player_0':
            player_0.currency_after += deck.pool
            p0w += 1
        elif result == 'player_1':
            player_1.currency_after += deck.pool
            p1w += 1
        elif result == 'player_2':
            player_2.currency_after += deck.pool
            p2w += 1
        elif result == 'player_3':
            player_3.currency_after += deck.pool
            p3w += 1
        elif result == 'player_4':
            player_4.currency_after += deck.pool
            p4w += 1
        player_0_net_income = player_0.currency_after - player_0.currency_before
        player_1_net_income = player_1.currency_after - player_1.currency_before
        player_2_net_income = player_2.currency_after - player_2.currency_before
        player_3_net_income = player_3.currency_after - player_3.currency_before
        player_4_net_income = player_4.currency_after - player_4.currency_before
        player_0.temp_reset()
        player_1.temp_reset()
        player_2.temp_reset()
        player_3.temp_reset()
        player_4.temp_reset()
        p0_draw_or_not_samples.append(player_0_draw_or_not_samples)
        p0_discard_samples.append(player_0_discard_samples)
        p0_bet_or_not_samples.append(player_0_bet_or_not_samples)
        p0_net_incomes.append(player_0_net_income)
        p1_draw_or_not_samples.append(player_1_draw_or_not_samples)
        p1_discard_samples.append(player_1_discard_samples)
        p1_bet_or_not_samples.append(player_1_bet_or_not_samples)
        p1_net_incomes.append(player_1_net_income)
        p2_draw_or_not_samples.append(player_2_draw_or_not_samples)
        p2_discard_samples.append(player_2_discard_samples)
        p2_bet_or_not_samples.append(player_2_bet_or_not_samples)
        p2_net_incomes.append(player_2_net_income)
        p3_draw_or_not_samples.append(player_3_draw_or_not_samples)
        p3_discard_samples.append(player_3_discard_samples)
        p3_bet_or_not_samples.append(player_3_bet_or_not_samples)
        p3_net_incomes.append(player_3_net_income)
        p4_draw_or_not_samples.append(player_4_draw_or_not_samples)
        p4_discard_samples.append(player_4_discard_samples)
        p4_bet_or_not_samples.append(player_4_bet_or_not_samples)
        p4_net_incomes.append(player_4_net_income)
        if rounds < 1001 and rounds%100 == 0:
            print("first 1000", p0w, p1w, p2w, p3w, p4w, rounds)
            if p0w >= 19 and p0w>=p1w and p0w>=p4w and p0w>=p2w and p0w>=p3w:
                print ("player_0 最多胜")
                winner_draw_or_not_samples += p0_draw_or_not_samples
                winner_discard_samples += p0_discard_samples
                winner_bet_or_not_samples += p0_bet_or_not_samples
                winner_net_incomes += p0_net_incomes
            if p1w >= 19 and p1w>= p0w and p1w>= p2w and p1w>= p3w and p1w>= p4w:
                print ("player_1 最多胜")
                winner_draw_or_not_samples += p1_draw_or_not_samples
                winner_discard_samples += p1_discard_samples
                winner_bet_or_not_samples += p1_bet_or_not_samples
                winner_net_incomes += p1_net_incomes
            if p2w >= 19 and p2w>= p0w and p2w>= p1w and p2w>= p3w and p2w>= p4w:
                print ("player_2 最多胜")
                winner_draw_or_not_samples += p2_draw_or_not_samples
                winner_discard_samples += p2_discard_samples
                winner_bet_or_not_samples += p2_bet_or_not_samples
                winner_net_incomes += p2_net_incomes
            if p3w >= 19 and p3w>= p0w and p3w>= p1w and p3w>= p2w and p3w>= p4w:
                print ("player_3 最多胜")
                winner_draw_or_not_samples += p3_draw_or_not_samples
                winner_discard_samples += p3_discard_samples
                winner_bet_or_not_samples += p3_bet_or_not_samples
                winner_net_incomes += p3_net_incomes
            if p4w >= 19 and p4w>= p0w and p4w>= p3w and p4w>= p2w and p4w>= p1w:
                print ("player_4 最多胜")
                winner_draw_or_not_samples += p4_draw_or_not_samples
                winner_discard_samples += p4_discard_samples
                winner_bet_or_not_samples += p4_bet_or_not_samples
                winner_net_incomes += p4_net_incomes
            if rounds == 1000:
                print (len(winner_draw_or_not_samples))# rounds % 10000 == 0:
                if  winner_draw_or_not_samples != []: 
                    print ("got proper results.")
                    random_samples = True
                    print ("training.")
                    model_draw.fit(winner_draw_or_not_samples, winner_net_incomes, epochs=2, verbose=1)
                    print ("done.")
                else:
                    print ("random no proper results.")
                    random_samples = False
                    pass
                p0_draw_or_not_samples = [] # clear the cache
                p0_discard_samples = []
                p0_bet_or_not_samples = []
                p0_net_incomes = []
                p1_draw_or_not_samples = []
                p1_discard_samples = []
                p1_bet_or_not_samples = []
                p1_net_incomes = []
                p2_draw_or_not_samples = []
                p2_discard_samples = []
                p2_bet_or_not_samples = []
                p2_net_incomes = []
                p3_draw_or_not_samples = []
                p3_discard_samples = []
                p3_bet_or_not_samples = []
                p3_net_incomes = []
                p4_draw_or_not_samples = []
                p4_discard_samples = []
                p4_bet_or_not_samples = []
                p4_net_incomes = []
                winner_draw_or_not_samples = []
                winner_discard_samples = []
                winner_bet_or_not_samples = []
                winner_net_incomes = []
                p0w = 0
                p1w = 0
                p2w = 0
                p3w = 0
                p4w = 0
                # break 
            # model_discard.fit(discard_samples, net_incomes, epochs=200, verbose=0)
            # model_bet.fit(bet_or_not_samples, net_incomes, epochs=200, verbose=0)
        elif rounds > 1001 and rounds < 10000 and rounds% 100 == 0:
            print("newest 100", p0w, p1w, p2w, p3w, p4w, rounds)
            if p0w >= 19 and p0w>= p1w and p0w>=p1w and p0w>=p2w and p0w>=p3w:
                print ("player_0 最多胜")
                winner_draw_or_not_samples += p0_draw_or_not_samples
                winner_discard_samples += p0_discard_samples
                winner_bet_or_not_samples += p0_bet_or_not_samples
                winner_net_incomes += p0_net_incomes
            if p1w >= 19 and p1w>= p0w and p1w>= p2w and p1w>= p3w and p1w>= p4w:
                print ("player_1 最多胜")
                winner_draw_or_not_samples += p1_draw_or_not_samples
                winner_discard_samples += p1_discard_samples
                winner_bet_or_not_samples += p1_bet_or_not_samples
                winner_net_incomes += p1_net_incomes
            if p2w >= 19 and p2w>= p0w and p2w>= p1w and p2w>= p3w and p2w>= p4w:
                print ("player_2 最多胜")
                winner_draw_or_not_samples += p2_draw_or_not_samples
                winner_discard_samples += p2_discard_samples
                winner_bet_or_not_samples += p2_bet_or_not_samples
                winner_net_incomes += p2_net_incomes
            if p3w >= 19 and p3w>= p0w and p3w>= p1w and p3w>= p2w and p3w>= p4w:
                print ("player_3 最多胜")
                winner_draw_or_not_samples += p3_draw_or_not_samples
                winner_discard_samples += p3_discard_samples
                winner_bet_or_not_samples += p3_bet_or_not_samples
                winner_net_incomes += p3_net_incomes
            if p4w >= 19 and p4w>= p0w and p4w>= p3w and p4w>= p2w and p4w>= p1w:
                print ("player_4 最多胜")
                winner_draw_or_not_samples += p4_draw_or_not_samples
                winner_discard_samples += p4_discard_samples
                winner_bet_or_not_samples += p4_bet_or_not_samples
                winner_net_incomes += p4_net_incomes
            if rounds % 1000 == 0 and winner_draw_or_not_samples != []: 
                print ("training.")
                model_draw.fit(winner_draw_or_not_samples, winner_net_incomes, epochs=2, verbose=1)
                print ("done.")
                p0_draw_or_not_samples = [] # clear the cache
                p0_discard_samples = []
                p0_bet_or_not_samples = []
                p0_net_incomes = []
                p1_draw_or_not_samples = []
                p1_discard_samples = []
                p1_bet_or_not_samples = []
                p1_net_incomes = []
                p2_draw_or_not_samples = []
                p2_discard_samples = []
                p2_bet_or_not_samples = []
                p2_net_incomes = []
                p3_draw_or_not_samples = []
                p3_discard_samples = []
                p3_bet_or_not_samples = []
                p3_net_incomes = []
                p4_draw_or_not_samples = []
                p4_discard_samples = []
                p4_bet_or_not_samples = []
                p4_net_incomes = []
                winner_draw_or_not_samples = []
                winner_discard_samples = []
                winner_bet_or_not_samples = []
                winner_net_incomes = []
                p0w = 0
                p1w = 0
                p2w = 0
                p3w = 0
                p4w = 0
                # break 
        elif rounds% 100 == 0:
            print("newest 100", p0w, p1w, p2w, p3w, p4w, rounds)
            if p0w>=p1w and p0w>=p1w and p0w>=p2w and p0w>=p3w:
                print ("player_0 最多胜")
                winner_draw_or_not_samples += p0_draw_or_not_samples
                winner_discard_samples += p0_discard_samples
                winner_bet_or_not_samples += p0_bet_or_not_samples
                winner_net_incomes += p0_net_incomes
            if p1w>= p0w and p1w>= p2w and p1w>= p3w and p1w>= p4w:
                print ("player_1 最多胜")
                winner_draw_or_not_samples += p1_draw_or_not_samples
                winner_discard_samples += p1_discard_samples
                winner_bet_or_not_samples += p1_bet_or_not_samples
                winner_net_incomes += p1_net_incomes
            if p2w>= p0w and p2w>= p1w and p2w>= p3w and p2w>= p4w:
                print ("player_2 最多胜")
                winner_draw_or_not_samples += p2_draw_or_not_samples
                winner_discard_samples += p2_discard_samples
                winner_bet_or_not_samples += p2_bet_or_not_samples
                winner_net_incomes += p2_net_incomes
            if p3w>= p0w and p3w>= p1w and p3w>= p2w and p3w>= p4w:
                print ("player_3 最多胜")
                winner_draw_or_not_samples += p3_draw_or_not_samples
                winner_discard_samples += p3_discard_samples
                winner_bet_or_not_samples += p3_bet_or_not_samples
                winner_net_incomes += p3_net_incomes
            if p4w>= p0w and p4w>= p3w and p4w>= p2w and p4w>= p1w:
                print ("player_4 最多胜")
                winner_draw_or_not_samples += p4_draw_or_not_samples
                winner_discard_samples += p4_discard_samples
                winner_bet_or_not_samples += p4_bet_or_not_samples
                winner_net_incomes += p4_net_incomes
            p0_draw_or_not_samples = [] # clear the cache
            p0_discard_samples = []
            p0_bet_or_not_samples = []
            p0_net_incomes = []
            p1_draw_or_not_samples = []
            p1_discard_samples = []
            p1_bet_or_not_samples = []
            p1_net_incomes = []
            p2_draw_or_not_samples = []
            p2_discard_samples = []
            p2_bet_or_not_samples = []
            p2_net_incomes = []
            p3_draw_or_not_samples = []
            p3_discard_samples = []
            p3_bet_or_not_samples = []
            p3_net_incomes = []
            p4_draw_or_not_samples = []
            p4_discard_samples = []
            p4_bet_or_not_samples = []
            p4_net_incomes = []
            winner_draw_or_not_samples = []
            winner_discard_samples = []
            winner_bet_or_not_samples = []
            winner_net_incomes = []
            p0w = 0
            p1w = 0
            p2w = 0
            p3w = 0
            p4w = 0
    print("到这为止正常。")
    # print ("p0_draw_sum: ", p0_draw)
    # print ("p0_replace_sum:", p0_replace)
    print("start train.")
    # model_draw.fit(draw_or_not_samples, net_incomes, epochs=200, verbose=0)
    # model_discard.fit(discard_samples, net_incomes, epochs=200, verbose=0)
    # model_bet.fit(bet_or_not_samples, net_incomes, epochs=200, verbose=0)
    print("end train.")