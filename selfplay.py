from random import randint
import numpy as np
from random import shuffle
import copy
from make_models import make_draw_model, make_discard_model, make_bet_model
import tensorflow as tf
import time

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
    def __init__(self, draw_card = -1, pool = 0, big:int = -2, name_=''):
        self.hand = []
        self.drop = []
        self.currency_before = 4
        self.currency_after = 4
        self.draw_card = draw_card
        self.pool = pool
        self.big = big
        self.bet_decision = False
        self.matrix = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0]
        self.name = name_
        # 0: draw(1) or change(0)
        # 1: discard big(1) or small(-1)
        # 2~16: current player hand: -1:will never appear(discarded); 1:in hand 0:library or other's hand
        # 17~20: other players draw(1) or change(0)
        ############################################# 21~35: public card(1)
        # 21: current player bet(1) or not(0)
        # 22~25 : others bet(1) or not(0)
        # 26: pool
        # 27: games left
        self.draw_or_not_samples = []
        # self.dons_sum = [] #len(self.draw_or_not_samples)
        self.discard_samples = []
        # self.disc_sum = len(self.discard_samples)
        self.bet_or_not_samples = []
        # self.bons_sum = len(self.bet_or_not_samples)
        self.net_income = 0
        # self.neti_sum = []
        # self.neti_sum = len(self.net_incomes)
    def draw(self, draw_card: int):
        self.hand.append(draw_card)
        self.matrix[1 + self.hand[0]] = 1
        # self.matrix[7 + self.hand[0]] = 1
    def hand_sort(self):
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
    def bet(self):
        self.bet_decision = True
    def draw_game(self):
        self.currency_after = self.currency_before
    def temp_reset(self):
        self.currency_before = self.currency_after
    def net_income_calc(self):
        val = self.currency_after - self.currency_before
        return val

def get_break_points(deck, current_player:player, _1_player:player, _2_player:player, _3_player:player, _4_player:player, w,x,y,z):
    current_player.draw_or_not_samples = copy.deepcopy(current_player.matrix)
    # current_player.discard_samples = copy.deepcopy(current_player.matrix)
    # 抓/翻模型断点
    if randint(0,1) == 1: #draw
        current_player.draw(deck.drawn())
        current_player.matrix[0] = 1
        current_player.matrix[1 + current_player.hand[0]] = 1
        current_player.matrix[1 + current_player.hand[1]] = 1
        _1_player.matrix[w] = 1
        _2_player.matrix[x] = 1
        _3_player.matrix[y] = 1
        _4_player.matrix[z] = 1
        current_player.hand.sort()
        # 弃牌选择模型断点
        current_player.discard_samples = copy.deepcopy(current_player.matrix)
        if randint(0,1) == 1: #discard big
            # current_player.discard_samples = copy.deepcopy(current_player.matrix)
            current_player.matrix[1] = 1
            current_player.matrix[1 + current_player.hand[0]] = 1
            current_player.matrix[1 + current_player.hand[-1]] = -1
            _1_player.matrix[1 + current_player.hand[-1]] = -1
            _2_player.matrix[1 + current_player.hand[-1]] = -1
            _3_player.matrix[1 + current_player.hand[-1]] = -1
            _4_player.matrix[1 + current_player.hand[-1]] = -1
            current_player.discard(big=1)
        else:
            # current_player.discard_samples = copy.deepcopy(current_player.matrix)
            current_player.matrix[1] = 1
            current_player.matrix[1 + current_player.hand[0]] = -1
            current_player.matrix[1 + current_player.hand[-1]] = 1
            _1_player.matrix[1 + current_player.hand[0]] = -1
            _2_player.matrix[1 + current_player.hand[0]] = -1
            _3_player.matrix[1 + current_player.hand[0]] = -1
            _4_player.matrix[1 + current_player.hand[0]] = -1
            current_player.discard(big=0)
    else:
        deck.replace() #replace

def get_break_points_model_draw(deck, model_draw, current_player:player, _1_player:player, _2_player:player, _3_player:player, _4_player:player, w,x,y,z):
    # return current_player.draw_or_not_samples # , current_player.discard_samples
    current_player.draw_or_not_samples = copy.deepcopy(current_player.matrix)
    # current_player.discard_samples = copy.deepcopy(current_player.matrix)
    # 抓/翻模型断点
    if calc_draw(current_player,model_draw) == 1: #draw
        current_player.draw(deck.drawn())
        current_player.matrix[0] = 1
        current_player.matrix[1 + current_player.hand[0]] = 1
        current_player.matrix[1 + current_player.hand[1]] = 1
        _1_player.matrix[w] = 1
        _2_player.matrix[x] = 1
        _3_player.matrix[y] = 1
        _4_player.matrix[z] = 1
        current_player.hand.sort()
        current_player.discard_samples = copy.deepcopy(current_player.matrix)
        # 弃牌选择模型断点
        if randint(0,1) == 1: #discard big
            # current_player.discard_samples = copy.deepcopy(current_player.matrix)
            current_player.matrix[1] = 1
            current_player.matrix[1 + current_player.hand[0]] = 1
            current_player.matrix[1 + current_player.hand[-1]] = -1
            _1_player.matrix[1 + current_player.hand[-1]] = -1
            _2_player.matrix[1 + current_player.hand[-1]] = -1
            _3_player.matrix[1 + current_player.hand[-1]] = -1
            _4_player.matrix[1 + current_player.hand[-1]] = -1
            current_player.discard(big=1)
        else:
            # current_player.discard_samples = copy.deepcopy(current_player.matrix)
            current_player.matrix[1] = 1
            current_player.matrix[1 + current_player.hand[0]] = -1
            current_player.matrix[1 + current_player.hand[-1]] = 1
            _1_player.matrix[1 + current_player.hand[0]] = -1
            _2_player.matrix[1 + current_player.hand[0]] = -1
            _3_player.matrix[1 + current_player.hand[0]] = -1
            _4_player.matrix[1 + current_player.hand[0]] = -1
            current_player.discard(big=0)
    else:
        deck.replace() #replace

def get_break_points_model_discard(deck, model_discard, current_player:player, _1_player:player, _2_player:player, _3_player:player, _4_player:player, w,x,y,z):
    # return current_player.draw_or_not_samples # , current_player.discard_samples
    # current_player.draw_or_not_samples = copy.deepcopy(current_player.matrix)
    # current_player.discard_samples = copy.deepcopy(current_player.matrix)
    # 抓/翻模型断点
    # if randint(0,1) == 1:# calc_draw(current_player,model_draw) == 1: #draw
    current_player.draw(deck.drawn())
    current_player.matrix[0] = 1
    current_player.matrix[1 + current_player.hand[0]] = 1
    current_player.matrix[1 + current_player.hand[1]] = 1
    _1_player.matrix[w] = 1
    _2_player.matrix[x] = 1
    _3_player.matrix[y] = 1
    _4_player.matrix[z] = 1
    current_player.hand.sort()
    current_player.discard_samples = copy.deepcopy(current_player.matrix)
    # 弃牌选择模型断点
    if calc_discard(current_player,model_discard) == 1: #discard big
        # current_player.discard_samples = copy.deepcopy(current_player.matrix)
        current_player.matrix[1] = 1
        current_player.matrix[1 + current_player.hand[0]] = 1
        current_player.matrix[1 + current_player.hand[-1]] = -1
        _1_player.matrix[1 + current_player.hand[-1]] = -1
        _2_player.matrix[1 + current_player.hand[-1]] = -1
        _3_player.matrix[1 + current_player.hand[-1]] = -1
        _4_player.matrix[1 + current_player.hand[-1]] = -1
        current_player.discard(big=1)
    else:
        # current_player.discard_samples = copy.deepcopy(current_player.matrix)
        current_player.matrix[1] = -1
        current_player.matrix[1 + current_player.hand[0]] = -1
        current_player.matrix[1 + current_player.hand[-1]] = 1
        _1_player.matrix[1 + current_player.hand[0]] = -1
        _2_player.matrix[1 + current_player.hand[0]] = -1
        _3_player.matrix[1 + current_player.hand[0]] = -1
        _4_player.matrix[1 + current_player.hand[0]] = -1
        current_player.discard(big=0)
    # else:
    #     deck.replace() #replace

def calc_draw(current_player,model_draw):
    current_player_matrix_0 = copy.deepcopy(current_player.matrix)
    current_player_matrix_1 = copy.deepcopy(current_player.matrix)
    current_player_matrix_0[0] = 0
    current_player_matrix_1[0] = 1
    pred_0 = 0
    pred_1 = 0
    prediction_draw_0 = model_draw.predict([current_player_matrix_0])
    pred_0 += prediction_draw_0[0]
    prediction_draw_1 = model_draw.predict([current_player_matrix_1])
    pred_1 += prediction_draw_1[0]
    if pred_1>=pred_0: 
        return 1
    else: 
        return 0

def calc_discard(current_player,model_discard):
    current_player_matrix_0 = copy.deepcopy(current_player.matrix)
    current_player_matrix_1 = copy.deepcopy(current_player.matrix)
    current_player_matrix_0[1] = 1 #big
    current_player_matrix_1[1] = -1 #small
    pred_0 = 0
    pred_1 = 0
    prediction_draw_0 = model_discard.predict([current_player_matrix_0])
    pred_0 += prediction_draw_0[0]
    prediction_draw_1 = model_discard.predict([current_player_matrix_1])
    pred_1 += prediction_draw_1[0]
    if pred_0 >= pred_1: 
        return 1
    else: 
        return 0

def calc_bet(current_player,model_bet):
    current_player_matrix_1 = copy.deepcopy(current_player.matrix)
    current_player_matrix_1[21] = 1
    pred_1 = 0
    prediction_draw_1 = model_bet.predict([current_player_matrix_1])
    pred_1 += prediction_draw_1[0]
    if pred_1 > 0: 
        return 1
    else: 
        return 0

def bet_step(deck, player_0: player, player_1, player_2, player_3, player_4, blind, w, x, y, z):
    player_0.bet_or_not_samples = copy.deepcopy(player_0.matrix)
    if randint(0,1) == 1:
        player_0.bet()
        player_0.currency_after -= blind
        deck.pool += blind
        player_0.matrix[26] = deck.pool
        player_0.matrix[21] = blind
        player_1.matrix[w] = blind
        player_2.matrix[x] = blind
        player_3.matrix[y] = blind
        player_4.matrix[z] = blind
    else:
        pass

def public_info(deck, player_0):
    # 汇总场上所有的公开信息给所有人
    # （小早川牌、小早川弃牌堆、所有人弃牌堆）
    player_0.matrix[1 + deck.on_show[0]] = 1
    if deck.drop != []:
        for x in range(len(deck.drop)):
            player_0.matrix[1 + deck.drop[x]] = -1
    else:
        pass

def first_card(deck, player_0, player_1, player_2, player_3, player_4):
    player_0.matrix[1 + deck.on_show[0]] = 1
    player_1.matrix[1 + deck.on_show[0]] = 1
    player_2.matrix[1 + deck.on_show[0]] = 1
    player_3.matrix[1 + deck.on_show[0]] = 1
    player_4.matrix[1 + deck.on_show[0]] = 1
    for i in deck.drop: player_0.matrix[1 + deck.drop[i]] = -1
    for i in deck.drop: player_1.matrix[1 + deck.drop[i]] = -1
    for i in deck.drop: player_2.matrix[1 + deck.drop[i]] = -1
    for i in deck.drop: player_3.matrix[1 + deck.drop[i]] = -1
    for i in deck.drop: player_4.matrix[1 + deck.drop[i]] = -1

def bet_summary(player, final_open):
    if player.bet_decision == True: final_open[player.name] = player.hand[0]

def process_final_open(final_open, deck):
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

def random_game_draw():
    model_random = make_draw_model()
    winner_net_incomes = []
    player_0_dons_sum = []
    player_1_dons_sum = []
    player_2_dons_sum = []
    player_3_dons_sum = []
    player_4_dons_sum = []
    player_0_neti_sum = []
    player_1_neti_sum = []
    player_2_neti_sum = []
    player_3_neti_sum = []
    player_4_neti_sum = []
    epoch = 0
    p0_win = 0
    p1_win = 0
    p2_win = 0
    p3_win = 0
    p4_win = 0
    while epoch<1000:
        epoch += 1
        blind = 1
        player_0 = player(name_='player_0')
        player_1 = player(name_='player_1')
        player_2 = player(name_='player_2')
        player_3 = player(name_='player_3')
        player_4 = player(name_='player_4')
        deck = library(pool = 1)
        deck.refresh()
        deck.place()
        first_card(deck, player_0, player_1, player_2, player_3, player_4)
        player_0.draw(deck.drawn())
        player_1.draw(deck.drawn())
        player_2.draw(deck.drawn())
        player_3.draw(deck.drawn())
        player_4.draw(deck.drawn())
        get_break_points(deck, player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
        get_break_points(deck, player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
        get_break_points(deck, player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
        get_break_points(deck, player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
        get_break_points(deck, player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        public_info(deck, player_0)
        public_info(deck, player_1)
        public_info(deck, player_2)
        public_info(deck, player_3)
        public_info(deck, player_4)
        bet_step(deck, player_0, player_1, player_2, player_3, player_4, blind, 22, 22, 22, 22)
        bet_step(deck, player_1, player_0, player_2, player_3, player_4, blind, 22, 23, 23, 23)
        bet_step(deck, player_2, player_0, player_1, player_3, player_4, blind, 23, 23, 24, 24)
        bet_step(deck, player_3, player_0, player_1, player_2, player_4, blind, 24, 24, 24, 25)
        bet_step(deck, player_4, player_0, player_1, player_2, player_3, blind, 25, 25, 25, 25)
        final_open = {}
        bet_summary(player_0, final_open)
        bet_summary(player_1, final_open)
        bet_summary(player_2, final_open)
        bet_summary(player_3, final_open)
        bet_summary(player_4, final_open)
        result = process_final_open(final_open, deck)
        if result is None:
            player_0.draw_game()
            player_1.draw_game()
            player_2.draw_game()
            player_3.draw_game()
            player_4.draw_game()
            # print ("nobody wins.")
        elif result == 'player_0':
            player_0.currency_after += deck.pool
            p0_win += 1
        elif result == 'player_1':
            player_1.currency_after += deck.pool
            p1_win += 1
        elif result == 'player_2':
            player_2.currency_after += deck.pool
            p2_win += 1
        elif result == 'player_3':
            player_3.currency_after += deck.pool
            p3_win += 1
        elif result == 'player_4':
            player_4.currency_after += deck.pool
            p4_win += 1
        player_0_net_income = player_0.currency_after - player_0.currency_before
        player_0_dons_sum.append(player_0.draw_or_not_samples)
        player_0_neti_sum.append([player_0_net_income])
        player_1_net_income = player_1.currency_after - player_1.currency_before
        player_1_dons_sum.append(player_1.draw_or_not_samples)
        player_1_neti_sum.append([player_1_net_income])
        player_2_net_income = player_2.currency_after - player_2.currency_before
        player_2_dons_sum.append(player_2.draw_or_not_samples)
        player_2_neti_sum.append([player_2_net_income])
        player_3_net_income = player_3.currency_after - player_3.currency_before
        player_3_dons_sum.append(player_3.draw_or_not_samples)
        player_3_neti_sum.append([player_3_net_income])
        player_4_net_income = player_4.currency_after - player_4.currency_before
        player_4_dons_sum.append(player_4.draw_or_not_samples)
        player_4_neti_sum.append([player_4_net_income])
        player_0.temp_reset()
        player_1.temp_reset()
        player_2.temp_reset()
        player_3.temp_reset()
        player_4.temp_reset()
        # print ([player_0_net_income],[player_1_net_income],[player_2_net_income],[player_3_net_income],[player_4_net_income])
        winner_don_samples = []
        winner_don_samples += player_0_dons_sum
        winner_don_samples += player_1_dons_sum
        winner_don_samples += player_2_dons_sum
        winner_don_samples += player_3_dons_sum
        winner_don_samples += player_4_dons_sum
        winner_net_incomes = []
        winner_net_incomes += player_0_neti_sum
        winner_net_incomes += player_1_neti_sum
        winner_net_incomes += player_2_neti_sum
        winner_net_incomes += player_3_neti_sum
        winner_net_incomes += player_4_neti_sum
    print ("training.")
    print (p0_win, p1_win, p2_win, p3_win, p4_win)
    print (len(winner_don_samples))
    model_random.fit(winner_don_samples, winner_net_incomes, epochs=5, verbose=1)
    print ("done.")
    return model_random

def model_self_play_train_draw(model_draw):
    winner_net_incomes = []
    player_0_dons_sum = []
    player_1_dons_sum = []
    player_2_dons_sum = []
    player_3_dons_sum = []
    player_4_dons_sum = []
    player_0_neti_sum = []
    player_1_neti_sum = []
    player_2_neti_sum = []
    player_3_neti_sum = []
    player_4_neti_sum = []
    epoch = 0
    while epoch<1000:
        epoch += 1
        blind = 1
        player_0 = player(name_='player_0')
        player_1 = player(name_='player_1')
        player_2 = player(name_='player_2')
        player_3 = player(name_='player_3')
        player_4 = player(name_='player_4')
        deck = library(pool = 1)
        deck.refresh()
        deck.place()
        first_card(deck, player_0, player_1, player_2, player_3, player_4)
        player_0.draw(deck.drawn())
        player_1.draw(deck.drawn())
        player_2.draw(deck.drawn())
        player_3.draw(deck.drawn())
        player_4.draw(deck.drawn())
        get_break_points_model_draw(deck, model_draw, player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
        get_break_points_model_draw(deck, model_draw, player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
        get_break_points_model_draw(deck, model_draw, player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
        get_break_points_model_draw(deck, model_draw, player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
        get_break_points_model_draw(deck, model_draw, player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        public_info(deck, player_0)
        public_info(deck, player_1)
        public_info(deck, player_2)
        public_info(deck, player_3)
        public_info(deck, player_4)
        bet_step(deck, player_0, player_1, player_2, player_3, player_4, blind, 22, 22, 22, 22)
        bet_step(deck, player_1, player_0, player_2, player_3, player_4, blind, 22, 23, 23, 23)
        bet_step(deck, player_2, player_0, player_1, player_3, player_4, blind, 23, 23, 24, 24)
        bet_step(deck, player_3, player_0, player_1, player_2, player_4, blind, 24, 24, 24, 25)
        bet_step(deck, player_4, player_0, player_1, player_2, player_3, blind, 25, 25, 25, 25)
        final_open = {}
        bet_summary(player_0, final_open)
        bet_summary(player_1, final_open)
        bet_summary(player_2, final_open)
        bet_summary(player_3, final_open)
        bet_summary(player_4, final_open)
        result = process_final_open(final_open, deck)
        if result is None:
            player_0.draw_game()
            player_1.draw_game()
            player_2.draw_game()
            player_3.draw_game()
            player_4.draw_game()
            # print ("nobody wins.")
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
        player_0_dons_sum.append(player_0.draw_or_not_samples)
        player_0_neti_sum.append([player_0_net_income])
        player_1_net_income = player_1.currency_after - player_1.currency_before
        player_1_dons_sum.append(player_1.draw_or_not_samples)
        player_1_neti_sum.append([player_1_net_income])
        player_2_net_income = player_2.currency_after - player_2.currency_before
        player_2_dons_sum.append(player_2.draw_or_not_samples)
        player_2_neti_sum.append([player_2_net_income])
        player_3_net_income = player_3.currency_after - player_3.currency_before
        player_3_dons_sum.append(player_3.draw_or_not_samples)
        player_3_neti_sum.append([player_3_net_income])
        player_4_net_income = player_4.currency_after - player_4.currency_before
        player_4_dons_sum.append(player_4.draw_or_not_samples)
        player_4_neti_sum.append([player_4_net_income])
        player_0.temp_reset()
        player_1.temp_reset()
        player_2.temp_reset()
        player_3.temp_reset()
        player_4.temp_reset()
        winner_don_samples = []
        winner_don_samples += player_0_dons_sum
        winner_don_samples += player_1_dons_sum
        winner_don_samples += player_2_dons_sum
        winner_don_samples += player_3_dons_sum
        winner_don_samples += player_4_dons_sum
        winner_net_incomes = []
        winner_net_incomes += player_0_neti_sum
        winner_net_incomes += player_1_neti_sum
        winner_net_incomes += player_2_neti_sum
        winner_net_incomes += player_3_neti_sum
        winner_net_incomes += player_4_neti_sum
    # print (winner_don_samples)
    # print (winner_net_incomes)
    print ("training.")
    model_draw.fit(winner_don_samples, winner_net_incomes, epochs=5, verbose=1)
    print ("done.")
    return model_draw

def causal_game_with_random_draw(model_draw): #evaluate random
    test_epochs = 1000
    model_wins = 0
    epoch = 0
    while epoch<test_epochs:
        epoch += 1
        blind = 1
        player_0 = player(name_='player_0')
        player_1 = player(name_='player_1')
        player_2 = player(name_='player_2')
        player_3 = player(name_='player_3')
        player_4 = player(name_='player_4')
        deck = library(pool = 1)
        deck.refresh()
        deck.place()
        first_card(deck, player_0, player_1, player_2, player_3, player_4)
        player_0.draw(deck.drawn())
        player_1.draw(deck.drawn())
        player_2.draw(deck.drawn())
        player_3.draw(deck.drawn())
        player_4.draw(deck.drawn())
        #get_break_points_model_selfplay
        if epoch<= test_epochs/5:
            get_break_points_model_draw(deck, model_draw, player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
            get_break_points(deck, player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
            get_break_points(deck, player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
            get_break_points(deck, player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
            get_break_points(deck, player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        elif epoch>test_epochs/5 and epoch<=test_epochs*2/5:
            get_break_points(deck, player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
            get_break_points_model_draw(deck, model_draw, player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
            get_break_points(deck, player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
            get_break_points(deck, player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
            get_break_points(deck, player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        elif epoch>test_epochs*2/5 and epoch<=test_epochs*3/5:
            get_break_points(deck, player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
            get_break_points(deck, player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
            get_break_points_model_draw(deck, model_draw, player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
            get_break_points(deck, player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
            get_break_points(deck, player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        elif epoch>test_epochs*3/5 and epoch<=test_epochs*4/5:
            get_break_points(deck, player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
            get_break_points(deck, player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
            get_break_points(deck, player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
            get_break_points_model_draw(deck, model_draw, player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
            get_break_points(deck, player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        else:
            get_break_points(deck, player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
            get_break_points(deck, player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
            get_break_points(deck, player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
            get_break_points(deck, player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
            get_break_points_model_draw(deck, model_draw, player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        public_info(deck, player_0)
        public_info(deck, player_1)
        public_info(deck, player_2)
        public_info(deck, player_3)
        public_info(deck, player_4)
        bet_step(deck, player_0, player_1, player_2, player_3, player_4, blind, 22, 22, 22, 22)
        bet_step(deck, player_1, player_0, player_2, player_3, player_4, blind, 22, 23, 23, 23)
        bet_step(deck, player_2, player_0, player_1, player_3, player_4, blind, 23, 23, 24, 24)
        bet_step(deck, player_3, player_0, player_1, player_2, player_4, blind, 24, 24, 24, 25)
        bet_step(deck, player_4, player_0, player_1, player_2, player_3, blind, 25, 25, 25, 25)
        final_open = {}
        bet_summary(player_0, final_open)
        bet_summary(player_1, final_open)
        bet_summary(player_2, final_open)
        bet_summary(player_3, final_open)
        bet_summary(player_4, final_open)
        result = process_final_open(final_open, deck)
        if result is None:
            pass
        elif result == 'player_0' and epoch<= test_epochs/5:
            model_wins += 1
        elif result == 'player_1' and epoch>test_epochs/5 and epoch<=test_epochs*2/5:
            model_wins += 1
        elif result == 'player_2' and epoch>test_epochs*2/5 and epoch<=test_epochs*3/5:
            model_wins += 1
        elif result == 'player_3' and epoch>test_epochs*3/5 and epoch<=test_epochs*4/5:
            model_wins += 1
        elif result == 'player_4' and epoch>test_epochs*3/5 and epoch<=test_epochs:
            model_wins += 1
    print ("model_wins", model_wins)
    if model_wins >= 205:
        print ("model_wins:", True)
        return True
    else:
        model_wins = 0
        print ("model_wins:", False)
        return False

def causal_game_with_previous_draw(model_previous, model_current):
    test_epochs = 1000
    model_current_wins = 0
    epoch = 0
    while epoch<test_epochs:
        epoch += 1
        blind = 1
        player_0 = player(name_='player_0')
        player_1 = player(name_='player_1')
        player_2 = player(name_='player_2')
        player_3 = player(name_='player_3')
        player_4 = player(name_='player_4')
        deck = library(pool = 1)
        deck.refresh()
        deck.place()
        first_card(deck, player_0, player_1, player_2, player_3, player_4)
        player_0.draw(deck.drawn())
        player_1.draw(deck.drawn())
        player_2.draw(deck.drawn())
        player_3.draw(deck.drawn())
        player_4.draw(deck.drawn())
        # get_break_points_model_selfplay
        if epoch<= test_epochs/5:
            get_break_points_model_draw(deck, model_current, player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
            get_break_points_model_draw(deck, model_previous,player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
            get_break_points_model_draw(deck, model_previous,player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
            get_break_points_model_draw(deck, model_previous,player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
            get_break_points_model_draw(deck, model_previous,player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        elif epoch>test_epochs/5 and epoch<=test_epochs*2/5:
            get_break_points_model_draw(deck, model_previous,player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
            get_break_points_model_draw(deck, model_current, player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
            get_break_points_model_draw(deck, model_previous,player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
            get_break_points_model_draw(deck, model_previous,player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
            get_break_points_model_draw(deck, model_previous,player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        elif epoch>test_epochs*2/5 and epoch<=test_epochs*3/5:
            get_break_points_model_draw(deck, model_previous,player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
            get_break_points_model_draw(deck, model_previous,player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
            get_break_points_model_draw(deck, model_current, player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
            get_break_points_model_draw(deck, model_previous,player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
            get_break_points_model_draw(deck, model_previous,player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        elif epoch>test_epochs*3/5 and epoch<=test_epochs*4/5:
            get_break_points_model_draw(deck, model_previous,player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
            get_break_points_model_draw(deck, model_previous,player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
            get_break_points_model_draw(deck, model_previous,player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
            get_break_points_model_draw(deck, model_current, player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
            get_break_points_model_draw(deck, model_previous,player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        else:
            get_break_points_model_draw(deck, model_previous,player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
            get_break_points_model_draw(deck, model_previous,player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
            get_break_points_model_draw(deck, model_previous,player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
            get_break_points_model_draw(deck, model_previous,player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
            get_break_points_model_draw(deck, model_current, player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        public_info(deck, player_0)
        public_info(deck, player_1)
        public_info(deck, player_2)
        public_info(deck, player_3)
        public_info(deck, player_4)
        bet_step(deck, player_0, player_1, player_2, player_3, player_4, blind, 22, 22, 22, 22)
        bet_step(deck, player_1, player_0, player_2, player_3, player_4, blind, 22, 23, 23, 23)
        bet_step(deck, player_2, player_0, player_1, player_3, player_4, blind, 23, 23, 24, 24)
        bet_step(deck, player_3, player_0, player_1, player_2, player_4, blind, 24, 24, 24, 25)
        bet_step(deck, player_4, player_0, player_1, player_2, player_3, blind, 25, 25, 25, 25)
        final_open = {}
        bet_summary(player_0, final_open)
        bet_summary(player_1, final_open)
        bet_summary(player_2, final_open)
        bet_summary(player_3, final_open)
        bet_summary(player_4, final_open)
        result = process_final_open(final_open, deck)
        if result is None:
            pass
        elif result == 'player_0' and epoch<= test_epochs/5:
            model_current_wins += 1
        elif result == 'player_1' and epoch>test_epochs/5 and epoch<=test_epochs*2/5:
            model_current_wins += 1
        elif result == 'player_2' and epoch>test_epochs*2/5 and epoch<=test_epochs*3/5:
            model_current_wins += 1
        elif result == 'player_3' and epoch>test_epochs*3/5 and epoch<=test_epochs*4/5:
            model_current_wins += 1
        elif result == 'player_4' and epoch>test_epochs*3/5 and epoch<=test_epochs:
            model_current_wins += 1
    print ("model_wins", model_current_wins)
    if model_current_wins >= 200:
        print ("model_wins:", True)
        return True
    else:
        model_current_wins = 0
        print ("model_wins:", False)
        return False

def random_game_discard():
    model_random = make_bet_model()
    draw_game = 0
    winner_net_incomes = []
    player_0_dons_sum = []
    player_1_dons_sum = []
    player_2_dons_sum = []
    player_3_dons_sum = []
    player_4_dons_sum = []
    player_0_neti_sum = []
    player_1_neti_sum = []
    player_2_neti_sum = []
    player_3_neti_sum = []
    player_4_neti_sum = []
    p0_win = 0
    p1_win = 0
    p2_win = 0
    p3_win = 0
    p4_win = 0
    epoch = 0
    while epoch<2000:
        epoch += 1
        blind = 1
        player_0 = player(name_='player_0')
        player_1 = player(name_='player_1')
        player_2 = player(name_='player_2')
        player_3 = player(name_='player_3')
        player_4 = player(name_='player_4')
        deck = library(pool = 1)
        deck.refresh()
        deck.place()
        first_card(deck, player_0, player_1, player_2, player_3, player_4)
        player_0.draw(deck.drawn())
        player_1.draw(deck.drawn())
        player_2.draw(deck.drawn())
        player_3.draw(deck.drawn())
        player_4.draw(deck.drawn())
        get_break_points(deck, player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
        get_break_points(deck, player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
        get_break_points(deck, player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
        get_break_points(deck, player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
        get_break_points(deck, player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        public_info(deck, player_0)
        public_info(deck, player_1)
        public_info(deck, player_2)
        public_info(deck, player_3)
        public_info(deck, player_4)
        # print (player_0.currency_after, player_1.currency_after, player_2.currency_after, player_3.currency_after, player_4.currency_after)
        bet_step(deck, player_0, player_1, player_2, player_3, player_4, blind, 22, 22, 22, 22)
        bet_step(deck, player_1, player_0, player_2, player_3, player_4, blind, 22, 23, 23, 23)
        bet_step(deck, player_2, player_0, player_1, player_3, player_4, blind, 23, 23, 24, 24)
        bet_step(deck, player_3, player_0, player_1, player_2, player_4, blind, 24, 24, 24, 25)
        bet_step(deck, player_4, player_0, player_1, player_2, player_3, blind, 25, 25, 25, 25)
        final_open = {}
        bet_summary(player_0, final_open)
        bet_summary(player_1, final_open)
        bet_summary(player_2, final_open)
        bet_summary(player_3, final_open)
        bet_summary(player_4, final_open)
        result = process_final_open(final_open, deck)
        # print (player_0.currency_after, player_1.currency_after, player_2.currency_after, player_3.currency_after, player_4.currency_after)
        if result is None:
            player_0.draw_game()
            player_1.draw_game()
            player_2.draw_game()
            player_3.draw_game()
            player_4.draw_game()
            draw_game += 1
            # print ("nobody wins.")
        elif result == 'player_0':
            player_0.currency_after += deck.pool
            p0_win += 1
        elif result == 'player_1':
            player_1.currency_after += deck.pool
            p1_win += 1
        elif result == 'player_2':
            player_2.currency_after += deck.pool
            p2_win += 1
        elif result == 'player_3':
            player_3.currency_after += deck.pool
            p3_win += 1
        elif result == 'player_4':
            player_4.currency_after += deck.pool
            p4_win += 1
        if player_0.matrix[0] == 1:
            player_0_net_income = player_0.currency_after - player_0.currency_before
            player_0_dons_sum.append(player_0.discard_samples)
            player_0_neti_sum.append([player_0_net_income])
        if player_1.matrix[0] == 1:
            player_1_net_income = player_1.currency_after - player_1.currency_before
            player_1_dons_sum.append(player_1.discard_samples)
            player_1_neti_sum.append([player_1_net_income])
        if player_2.matrix[0] == 1:
            player_2_net_income = player_2.currency_after - player_2.currency_before
            player_2_dons_sum.append(player_2.discard_samples)
            player_2_neti_sum.append([player_2_net_income])
        if player_3.matrix[0] == 1:
            player_3_net_income = player_3.currency_after - player_3.currency_before
            player_3_dons_sum.append(player_3.discard_samples)
            player_3_neti_sum.append([player_3_net_income])
        if player_4.matrix[0] == 1:
            player_4_net_income = player_4.currency_after - player_4.currency_before
            player_4_dons_sum.append(player_4.discard_samples)
            player_4_neti_sum.append([player_4_net_income])
        player_0.temp_reset()
        player_1.temp_reset()
        player_2.temp_reset()
        player_3.temp_reset()
        player_4.temp_reset()
        winner_don_samples = []
        winner_don_samples += player_0_dons_sum
        winner_don_samples += player_1_dons_sum
        winner_don_samples += player_2_dons_sum
        winner_don_samples += player_3_dons_sum
        winner_don_samples += player_4_dons_sum
        winner_net_incomes = []
        winner_net_incomes += player_0_neti_sum
        winner_net_incomes += player_1_neti_sum
        winner_net_incomes += player_2_neti_sum
        winner_net_incomes += player_3_neti_sum
        winner_net_incomes += player_4_neti_sum
    print (p0_win, p1_win, p2_win, p3_win, p4_win)
    print (len(winner_don_samples), len(winner_net_incomes))
    print ("training.")
    print ("draw games: ", draw_game)
    model_random.fit(winner_don_samples, winner_net_incomes, epochs=5, verbose=1)
    print ("done.")
    return model_random

def model_self_play_train_discard(model_discard):
    winner_net_incomes = []
    player_0_dons_sum = []
    player_1_dons_sum = []
    player_2_dons_sum = []
    player_3_dons_sum = []
    player_4_dons_sum = []
    player_0_neti_sum = []
    player_1_neti_sum = []
    player_2_neti_sum = []
    player_3_neti_sum = []
    player_4_neti_sum = []
    epoch = 0
    while epoch<2000:
        epoch += 1
        blind = 1
        player_0 = player(name_='player_0')
        player_1 = player(name_='player_1')
        player_2 = player(name_='player_2')
        player_3 = player(name_='player_3')
        player_4 = player(name_='player_4')
        deck = library(pool = 1)
        deck.refresh()
        deck.place()
        first_card(deck, player_0, player_1, player_2, player_3, player_4)
        player_0.draw(deck.drawn())
        player_1.draw(deck.drawn())
        player_2.draw(deck.drawn())
        player_3.draw(deck.drawn())
        player_4.draw(deck.drawn())
        get_break_points_model_discard(deck, model_discard, player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
        get_break_points_model_discard(deck, model_discard, player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
        get_break_points_model_discard(deck, model_discard, player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
        get_break_points_model_discard(deck, model_discard, player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
        get_break_points_model_discard(deck, model_discard, player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        public_info(deck, player_0)
        public_info(deck, player_1)
        public_info(deck, player_2)
        public_info(deck, player_3)
        public_info(deck, player_4)
        bet_step(deck, player_0, player_1, player_2, player_3, player_4, blind, 22, 22, 22, 22)
        bet_step(deck, player_1, player_0, player_2, player_3, player_4, blind, 22, 23, 23, 23)
        bet_step(deck, player_2, player_0, player_1, player_3, player_4, blind, 23, 23, 24, 24)
        bet_step(deck, player_3, player_0, player_1, player_2, player_4, blind, 24, 24, 24, 25)
        bet_step(deck, player_4, player_0, player_1, player_2, player_3, blind, 25, 25, 25, 25)
        final_open = {}
        bet_summary(player_0, final_open)
        bet_summary(player_1, final_open)
        bet_summary(player_2, final_open)
        bet_summary(player_3, final_open)
        bet_summary(player_4, final_open)
        result = process_final_open(final_open, deck)
        if result is None:
            player_0.draw_game()
            player_1.draw_game()
            player_2.draw_game()
            player_3.draw_game()
            player_4.draw_game()
            # print ("nobody wins.")
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
        # print (player_0.discard_samples)
        # print ([player_0.net_income])
        if player_0.matrix[0] == 1:
            player_0_net_income = player_0.currency_after - player_0.currency_before
            player_0_dons_sum.append(player_0.discard_samples)
            player_0_neti_sum.append([player_0_net_income])
        if player_1.matrix[0] == 1:
            player_1_net_income = player_1.currency_after - player_1.currency_before
            player_1_dons_sum.append(player_1.discard_samples)
            player_1_neti_sum.append([player_1_net_income])
        if player_2.matrix[0] == 1:
            player_2_net_income = player_2.currency_after - player_2.currency_before
            player_2_dons_sum.append(player_2.discard_samples)
            player_2_neti_sum.append([player_2_net_income])
        if player_3.matrix[0] == 1:
            player_3_net_income = player_3.currency_after - player_3.currency_before
            player_3_dons_sum.append(player_3.discard_samples)
            player_3_neti_sum.append([player_3_net_income])
        if player_4.matrix[0] == 1:
            player_4_net_income = player_4.currency_after - player_4.currency_before
            player_4_dons_sum.append(player_4.discard_samples)
            player_4_neti_sum.append([player_4_net_income])
        player_0.temp_reset()
        player_1.temp_reset()
        player_2.temp_reset()
        player_3.temp_reset()
        player_4.temp_reset()
        winner_don_samples = []
        winner_don_samples += player_0_dons_sum
        winner_don_samples += player_1_dons_sum
        winner_don_samples += player_2_dons_sum
        winner_don_samples += player_3_dons_sum
        winner_don_samples += player_4_dons_sum
        winner_net_incomes = []
        winner_net_incomes += player_0_neti_sum
        winner_net_incomes += player_1_neti_sum
        winner_net_incomes += player_2_neti_sum
        winner_net_incomes += player_3_neti_sum
        winner_net_incomes += player_4_neti_sum
    print ("training.")
    model_discard.fit(winner_don_samples, winner_net_incomes, epochs=5, verbose=1)
    print ("done.")
    return model_discard

def causal_game_with_random_discard(model_discard): #evaluate random
    test_epochs = 2000
    model_wins = 0
    epoch = 0
    discard_times = 0
    while epoch<test_epochs:
        epoch += 1
        blind = 1
        player_0 = player(name_='player_0')
        player_1 = player(name_='player_1')
        player_2 = player(name_='player_2')
        player_3 = player(name_='player_3')
        player_4 = player(name_='player_4')
        deck = library(pool = 1)
        deck.refresh()
        deck.place()
        first_card(deck, player_0, player_1, player_2, player_3, player_4)
        player_0.draw(deck.drawn())
        player_1.draw(deck.drawn())
        player_2.draw(deck.drawn())
        player_3.draw(deck.drawn())
        player_4.draw(deck.drawn())
        #get_break_points_model_selfplay
        if epoch<= test_epochs/5:
            get_break_points_model_discard(deck, model_discard, player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
            get_break_points(deck, player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
            get_break_points(deck, player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
            get_break_points(deck, player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
            get_break_points(deck, player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        elif epoch>test_epochs/5 and epoch<=test_epochs*2/5:
            get_break_points(deck, player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
            get_break_points_model_discard(deck, model_discard, player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
            get_break_points(deck, player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
            get_break_points(deck, player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
            get_break_points(deck, player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        elif epoch>test_epochs*2/5 and epoch<=test_epochs*3/5:
            get_break_points(deck, player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
            get_break_points(deck, player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
            get_break_points_model_discard(deck, model_discard, player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
            get_break_points(deck, player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
            get_break_points(deck, player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        elif epoch>test_epochs*3/5 and epoch<=test_epochs*4/5:
            get_break_points(deck, player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
            get_break_points(deck, player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
            get_break_points(deck, player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
            get_break_points_model_discard(deck, model_discard, player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
            get_break_points(deck, player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        else:
            get_break_points(deck, player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
            get_break_points(deck, player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
            get_break_points(deck, player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
            get_break_points(deck, player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
            get_break_points_model_discard(deck, model_discard, player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        public_info(deck, player_0)
        public_info(deck, player_1)
        public_info(deck, player_2)
        public_info(deck, player_3)
        public_info(deck, player_4)
        bet_step(deck, player_0, player_1, player_2, player_3, player_4, blind, 22, 22, 22, 22)
        bet_step(deck, player_1, player_0, player_2, player_3, player_4, blind, 22, 23, 23, 23)
        bet_step(deck, player_2, player_0, player_1, player_3, player_4, blind, 23, 23, 24, 24)
        bet_step(deck, player_3, player_0, player_1, player_2, player_4, blind, 24, 24, 24, 25)
        bet_step(deck, player_4, player_0, player_1, player_2, player_3, blind, 25, 25, 25, 25)
        final_open = {}
        bet_summary(player_0, final_open)
        bet_summary(player_1, final_open)
        bet_summary(player_2, final_open)
        bet_summary(player_3, final_open)
        bet_summary(player_4, final_open)
        result = process_final_open(final_open, deck)
        if epoch<= test_epochs/5: # and player_0.matrix[0] == 1
            discard_times += 1
            if result == 'player_0':
                model_wins += 1
        elif epoch>test_epochs/5 and epoch<=test_epochs*2/5: #and player_1.matrix[1] == 1
            discard_times += 1
            if result == 'player_1':
                model_wins += 1
        elif epoch>test_epochs*2/5 and epoch<=test_epochs*3/5: #and player_2.matrix[2] == 1
            discard_times += 1
            if result == 'player_2': 
                model_wins += 1
        elif epoch>test_epochs*3/5 and epoch<=test_epochs*4/5: # and player_3.matrix[3] == 1
            discard_times += 1
            if result == 'player_3': 
                model_wins += 1
        elif epoch>test_epochs*3/5 and epoch<=test_epochs: #and player_4.matrix[4] == 1 
            discard_times += 1
            if result == 'player_4': 
                model_wins += 1
        # print (discard_times, model_wins)
    print ("model_wins", model_wins, "total_discards", discard_times)
    if model_wins >= 0.180 * discard_times:
        print ("model_wins:", True)
        return True
    else:
        model_wins = 0
        discard_times = 0
        print ("model_wins:", False)
        return False

def causal_game_with_previous_discard(model_previous, model_current):
    test_epochs = 2000
    model_current_wins = 0
    epoch = 0
    discard_times = 0
    while epoch<test_epochs:
        epoch += 1
        blind = 1
        player_0 = player(name_='player_0')
        player_1 = player(name_='player_1')
        player_2 = player(name_='player_2')
        player_3 = player(name_='player_3')
        player_4 = player(name_='player_4')
        deck = library(pool = 1)
        deck.refresh()
        deck.place()
        first_card(deck, player_0, player_1, player_2, player_3, player_4)
        player_0.draw(deck.drawn())
        player_1.draw(deck.drawn())
        player_2.draw(deck.drawn())
        player_3.draw(deck.drawn())
        player_4.draw(deck.drawn())
        # get_break_points_model_selfplay
        if epoch<= test_epochs/5:
            get_break_points_model_discard(deck, model_current, player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
            get_break_points_model_discard(deck, model_previous,player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
            get_break_points_model_discard(deck, model_previous,player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
            get_break_points_model_discard(deck, model_previous,player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
            get_break_points_model_discard(deck, model_previous,player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        elif epoch>test_epochs/5 and epoch<=test_epochs*2/5:
            get_break_points_model_discard(deck, model_previous,player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
            get_break_points_model_discard(deck, model_current, player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
            get_break_points_model_discard(deck, model_previous,player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
            get_break_points_model_discard(deck, model_previous,player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
            get_break_points_model_discard(deck, model_previous,player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        elif epoch>test_epochs*2/5 and epoch<=test_epochs*3/5:
            get_break_points_model_discard(deck, model_previous,player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
            get_break_points_model_discard(deck, model_previous,player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
            get_break_points_model_discard(deck, model_current, player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
            get_break_points_model_discard(deck, model_previous,player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
            get_break_points_model_discard(deck, model_previous,player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        elif epoch>test_epochs*3/5 and epoch<=test_epochs*4/5:
            get_break_points_model_discard(deck, model_previous,player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
            get_break_points_model_discard(deck, model_previous,player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
            get_break_points_model_discard(deck, model_previous,player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
            get_break_points_model_discard(deck, model_current, player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
            get_break_points_model_discard(deck, model_previous,player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        else:
            get_break_points_model_discard(deck, model_previous,player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
            get_break_points_model_discard(deck, model_previous,player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
            get_break_points_model_discard(deck, model_previous,player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
            get_break_points_model_discard(deck, model_previous,player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
            get_break_points_model_discard(deck, model_current, player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        public_info(deck, player_0)
        public_info(deck, player_1)
        public_info(deck, player_2)
        public_info(deck, player_3)
        public_info(deck, player_4)
        bet_step(deck, player_0, player_1, player_2, player_3, player_4, blind, 22, 22, 22, 22)
        bet_step(deck, player_1, player_0, player_2, player_3, player_4, blind, 22, 23, 23, 23)
        bet_step(deck, player_2, player_0, player_1, player_3, player_4, blind, 23, 23, 24, 24)
        bet_step(deck, player_3, player_0, player_1, player_2, player_4, blind, 24, 24, 24, 25)
        bet_step(deck, player_4, player_0, player_1, player_2, player_3, blind, 25, 25, 25, 25)
        final_open = {}
        bet_summary(player_0, final_open)
        bet_summary(player_1, final_open)
        bet_summary(player_2, final_open)
        bet_summary(player_3, final_open)
        bet_summary(player_4, final_open)
        result = process_final_open(final_open, deck)
        if result is None:
            pass
        elif epoch<= test_epochs/5 and player_0.matrix[0] == 1:
            discard_times += 1
            if result == 'player_0':
                model_current_wins += 1
                print (discard_times, model_current_wins)
        elif epoch>test_epochs/5 and epoch<=test_epochs*2/5 and player_1.matrix[1] == 1:
            discard_times += 1
            if result == 'player_1':
                model_current_wins += 1
                print (discard_times, model_current_wins)
        elif epoch>test_epochs*2/5 and epoch<=test_epochs*3/5 and player_2.matrix[2] == 1:
            discard_times += 1
            if result == 'player_2': 
                model_current_wins += 1
                print (discard_times, model_current_wins)
        elif epoch>test_epochs*3/5 and epoch<=test_epochs*4/5 and player_3.matrix[3] == 1:
            discard_times += 1
            if result == 'player_3': 
                model_current_wins += 1
                print (discard_times, model_current_wins)
        elif epoch>test_epochs*3/5 and epoch<=test_epochs and player_4.matrix[4] == 1:
            discard_times += 1
            if result == 'player_4': 
                model_current_wins += 1
                print (discard_times, model_current_wins)
    print ("model_wins", model_current_wins, "discard_times:", discard_times)
    if model_current_wins >= discard_times * 0.175:
        print ("model_wins:", True)
        return True
    else:
        model_current_wins = 0
        discard_times = 0
        print ("model_wins:", False)
        return False

def bet_step_model(deck, model_bet, player_0: player, player_1, player_2, player_3, player_4, blind, w, x, y, z):
    if calc_bet(player_0, model_bet) == 1:
        player_0.bet_or_not_samples = copy.deepcopy(player_0.matrix)
        player_0.bet()
        player_0.currency_after -= blind
        deck.pool += blind
        player_0.matrix[26] = deck.pool
        player_0.matrix[21] = blind
        player_1.matrix[w] = blind
        player_2.matrix[x] = blind
        player_3.matrix[y] = blind
        player_4.matrix[z] = blind
    else:
        player_0.bet_or_not_samples = copy.deepcopy(player_0.matrix)

def random_game_bet():
    model_random = make_bet_model()
    winner_net_incomes = []
    player_0_dons_sum = []
    player_1_dons_sum = []
    player_2_dons_sum = []
    player_3_dons_sum = []
    player_4_dons_sum = []
    player_0_neti_sum = []
    player_1_neti_sum = []
    player_2_neti_sum = []
    player_3_neti_sum = []
    player_4_neti_sum = []
    epoch = 0
    p0_win = 0
    p1_win = 0
    p2_win = 0
    p3_win = 0
    p4_win = 0
    draw_games = 0
    while epoch<5000:
        epoch += 1
        blind = 1
        player_0 = player(name_='player_0')
        player_1 = player(name_='player_1')
        player_2 = player(name_='player_2')
        player_3 = player(name_='player_3')
        player_4 = player(name_='player_4')
        deck = library(pool = 1)
        deck.refresh()
        deck.place()
        first_card(deck, player_0, player_1, player_2, player_3, player_4)
        player_0.draw(deck.drawn())
        player_1.draw(deck.drawn())
        player_2.draw(deck.drawn())
        player_3.draw(deck.drawn())
        player_4.draw(deck.drawn())
        get_break_points(deck, player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
        get_break_points(deck, player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
        get_break_points(deck, player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
        get_break_points(deck, player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
        get_break_points(deck, player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        public_info(deck, player_0)
        public_info(deck, player_1)
        public_info(deck, player_2)
        public_info(deck, player_3)
        public_info(deck, player_4)
        bet_step(deck, player_0, player_1, player_2, player_3, player_4, blind, 22, 22, 22, 22)
        bet_step(deck, player_1, player_0, player_2, player_3, player_4, blind, 22, 23, 23, 23)
        bet_step(deck, player_2, player_0, player_1, player_3, player_4, blind, 23, 23, 24, 24)
        bet_step(deck, player_3, player_0, player_1, player_2, player_4, blind, 24, 24, 24, 25)
        bet_step(deck, player_4, player_0, player_1, player_2, player_3, blind, 25, 25, 25, 25)
        final_open = {}
        bet_summary(player_0, final_open)
        bet_summary(player_1, final_open)
        bet_summary(player_2, final_open)
        bet_summary(player_3, final_open)
        bet_summary(player_4, final_open)
        result = process_final_open(final_open, deck)
        if result is None:
            player_0.draw_game()
            player_1.draw_game()
            player_2.draw_game()
            player_3.draw_game()
            player_4.draw_game()
            draw_games += 1
            # print ("nobody wins.")
        elif result == 'player_0':
            player_0.currency_after += deck.pool
            p0_win += 1
        elif result == 'player_1':
            player_1.currency_after += deck.pool
            p1_win += 1
        elif result == 'player_2':
            player_2.currency_after += deck.pool
            p2_win += 1
        elif result == 'player_3':
            player_3.currency_after += deck.pool
            p3_win += 1
        elif result == 'player_4':
            player_4.currency_after += deck.pool
            p4_win += 1
        winner_don_samples = []
        winner_net_incomes = []
        if player_0.bet_decision == True:
            player_0_net_income = player_0.currency_after - player_0.currency_before
            player_0_dons_sum.append(player_0.draw_or_not_samples)
            player_0_neti_sum.append([player_0_net_income])
            winner_don_samples += player_0_dons_sum
            winner_net_incomes += player_0_neti_sum
        if player_1.bet_decision == True:
            player_1_net_income = player_1.currency_after - player_1.currency_before
            player_1_dons_sum.append(player_1.draw_or_not_samples)
            player_1_neti_sum.append([player_1_net_income])
            winner_don_samples += player_1_dons_sum
            winner_net_incomes += player_1_neti_sum
        if player_2.bet_decision == True:
            player_2_net_income = player_2.currency_after - player_2.currency_before
            player_2_dons_sum.append(player_2.draw_or_not_samples)
            player_2_neti_sum.append([player_2_net_income])
            winner_don_samples += player_2_dons_sum
            winner_net_incomes += player_2_neti_sum
        if player_3.bet_decision == True:
            player_3_net_income = player_3.currency_after - player_3.currency_before
            player_3_dons_sum.append(player_3.draw_or_not_samples)
            player_3_neti_sum.append([player_3_net_income])
            winner_don_samples += player_3_dons_sum
            winner_net_incomes += player_3_neti_sum
        if player_4.bet_decision == True:
            player_4_net_income = player_4.currency_after - player_4.currency_before
            player_4_dons_sum.append(player_4.draw_or_not_samples)
            player_4_neti_sum.append([player_4_net_income])
            winner_don_samples += player_4_dons_sum
            winner_net_incomes += player_4_neti_sum
        player_0.temp_reset()
        player_1.temp_reset()
        player_2.temp_reset()
        player_3.temp_reset()
        player_4.temp_reset()
    print ("training.")
    print (p0_win, p1_win, p2_win, p3_win, p4_win)
    print (len(winner_don_samples), len(winner_net_incomes))
    print (p0_win, p1_win, p2_win, p3_win, p4_win)
    print ("draw games:", draw_games)
    model_random.fit(winner_don_samples, winner_net_incomes, epochs=5, verbose=1)
    print ("done.")
    return model_random

def model_self_play_train_bet(model_bet):
    winner_net_incomes = []
    player_0_dons_sum = []
    player_1_dons_sum = []
    player_2_dons_sum = []
    player_3_dons_sum = []
    player_4_dons_sum = []
    player_0_neti_sum = []
    player_1_neti_sum = []
    player_2_neti_sum = []
    player_3_neti_sum = []
    player_4_neti_sum = []
    epoch = 0
    while epoch<1000:
        epoch += 1
        blind = 1
        player_0 = player(name_='player_0')
        player_1 = player(name_='player_1')
        player_2 = player(name_='player_2')
        player_3 = player(name_='player_3')
        player_4 = player(name_='player_4')
        deck = library(pool = 1)
        deck.refresh()
        deck.place()
        first_card(deck, player_0, player_1, player_2, player_3, player_4)
        player_0.draw(deck.drawn())
        player_1.draw(deck.drawn())
        player_2.draw(deck.drawn())
        player_3.draw(deck.drawn())
        player_4.draw(deck.drawn())
        get_break_points(deck, player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
        get_break_points(deck, player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
        get_break_points(deck, player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
        get_break_points(deck, player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
        get_break_points(deck, player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        public_info(deck, player_0)
        public_info(deck, player_1)
        public_info(deck, player_2)
        public_info(deck, player_3)
        public_info(deck, player_4)
        bet_step_model(deck, model_bet, player_0, player_1, player_2, player_3, player_4, blind, 22, 22, 22, 22)
        bet_step_model(deck, model_bet, player_1, player_0, player_2, player_3, player_4, blind, 22, 23, 23, 23)
        bet_step_model(deck, model_bet, player_2, player_0, player_1, player_3, player_4, blind, 23, 23, 24, 24)
        bet_step_model(deck, model_bet, player_3, player_0, player_1, player_2, player_4, blind, 24, 24, 24, 25)
        bet_step_model(deck, model_bet, player_4, player_0, player_1, player_2, player_3, blind, 25, 25, 25, 25)
        final_open = {}
        bet_summary(player_0, final_open)
        bet_summary(player_1, final_open)
        bet_summary(player_2, final_open)
        bet_summary(player_3, final_open)
        bet_summary(player_4, final_open)
        result = process_final_open(final_open, deck)
        if result is None:
            player_0.draw_game()
            player_1.draw_game()
            player_2.draw_game()
            player_3.draw_game()
            player_4.draw_game()
            # print ("nobody wins.")
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
        winner_don_samples = []
        winner_net_incomes = []
        if player_0.bet_decision == True:
            player_0_net_income = player_0.currency_after - player_0.currency_before
            player_0_dons_sum.append(player_0.draw_or_not_samples)
            player_0_neti_sum.append([player_0_net_income])
            winner_don_samples += player_0_dons_sum
            winner_net_incomes += player_0_neti_sum
        if player_1.bet_decision == True:
            player_1_net_income = player_1.currency_after - player_1.currency_before
            player_1_dons_sum.append(player_1.draw_or_not_samples)
            player_1_neti_sum.append([player_1_net_income])
            winner_don_samples += player_1_dons_sum
            winner_net_incomes += player_1_neti_sum
        if player_2.bet_decision == True:
            player_2_net_income = player_2.currency_after - player_2.currency_before
            player_2_dons_sum.append(player_2.draw_or_not_samples)
            player_2_neti_sum.append([player_2_net_income])
            winner_don_samples += player_2_dons_sum
            winner_net_incomes += player_2_neti_sum
        if player_3.bet_decision == True:
            player_3_net_income = player_3.currency_after - player_3.currency_before
            player_3_dons_sum.append(player_3.draw_or_not_samples)
            player_3_neti_sum.append([player_3_net_income])
            winner_don_samples += player_3_dons_sum
            winner_net_incomes += player_3_neti_sum
        if player_4.bet_decision == True:
            player_4_net_income = player_4.currency_after - player_4.currency_before
            player_4_dons_sum.append(player_4.draw_or_not_samples)
            player_4_neti_sum.append([player_4_net_income])
            winner_don_samples += player_4_dons_sum
            winner_net_incomes += player_4_neti_sum
        player_0.temp_reset()
        player_1.temp_reset()
        player_2.temp_reset()
        player_3.temp_reset()
        player_4.temp_reset()
    print ("training.")
    model_bet.fit(winner_don_samples, winner_net_incomes, epochs=5, verbose=1)
    print ("done.")
    return model_bet

def causal_game_with_random_bet(model_bet): #evaluate random
    test_epochs = 1000
    model_wins = 0
    epoch = 0
    p0_win = 0
    p1_win = 0
    p2_win = 0
    p3_win = 0
    p4_win = 0
    while epoch<test_epochs:
        epoch += 1
        blind = 1
        player_0 = player(name_='player_0')
        player_1 = player(name_='player_1')
        player_2 = player(name_='player_2')
        player_3 = player(name_='player_3')
        player_4 = player(name_='player_4')
        deck = library(pool = 1)
        deck.refresh()
        deck.place()
        first_card(deck, player_0, player_1, player_2, player_3, player_4)
        player_0.draw(deck.drawn())
        player_1.draw(deck.drawn())
        player_2.draw(deck.drawn())
        player_3.draw(deck.drawn())
        player_4.draw(deck.drawn())
        #get_break_points_model_selfplay
        get_break_points(deck, player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
        get_break_points(deck, player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
        get_break_points(deck, player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
        get_break_points(deck, player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
        get_break_points(deck, player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        public_info(deck, player_0)
        public_info(deck, player_1)
        public_info(deck, player_2)
        public_info(deck, player_3)
        public_info(deck, player_4)
        if epoch<= test_epochs/5:
            bet_step_model(deck, model_bet, player_0, player_1, player_2, player_3, player_4, blind, 22, 22, 22, 22)
            bet_step(deck, player_1, player_0, player_2, player_3, player_4, blind, 22, 23, 23, 23)
            bet_step(deck, player_2, player_0, player_1, player_3, player_4, blind, 23, 23, 24, 24)
            bet_step(deck, player_3, player_0, player_1, player_2, player_4, blind, 24, 24, 24, 25)
            bet_step(deck, player_4, player_0, player_1, player_2, player_3, blind, 25, 25, 25, 25)
        elif epoch>test_epochs/5 and epoch<=test_epochs*2/5:
            bet_step(deck, player_0, player_1, player_2, player_3, player_4, blind, 22, 22, 22, 22)
            bet_step_model(deck, model_bet, player_1, player_0, player_2, player_3, player_4, blind, 22, 23, 23, 23)
            bet_step(deck, player_2, player_0, player_1, player_3, player_4, blind, 23, 23, 24, 24)
            bet_step(deck, player_3, player_0, player_1, player_2, player_4, blind, 24, 24, 24, 25)
            bet_step(deck, player_4, player_0, player_1, player_2, player_3, blind, 25, 25, 25, 25)
        elif epoch>test_epochs*2/5 and epoch<=test_epochs*3/5:
            bet_step(deck, player_0, player_1, player_2, player_3, player_4, blind, 22, 22, 22, 22)
            bet_step(deck, player_1, player_0, player_2, player_3, player_4, blind, 22, 23, 23, 23)
            bet_step_model(deck, model_bet, player_2, player_0, player_1, player_3, player_4, blind, 23, 23, 24, 24)
            bet_step(deck, player_3, player_0, player_1, player_2, player_4, blind, 24, 24, 24, 25)
            bet_step(deck, player_4, player_0, player_1, player_2, player_3, blind, 25, 25, 25, 25)
        elif epoch>test_epochs*3/5 and epoch<=test_epochs*4/5:
            bet_step(deck, player_0, player_1, player_2, player_3, player_4, blind, 22, 22, 22, 22)
            bet_step(deck, player_1, player_0, player_2, player_3, player_4, blind, 22, 23, 23, 23)
            bet_step(deck, player_2, player_0, player_1, player_3, player_4, blind, 23, 23, 24, 24)
            bet_step_model(deck, model_bet,  player_3, player_0, player_1, player_2, player_4, blind, 24, 24, 24, 25)
            bet_step(deck, player_4, player_0, player_1, player_2, player_3, blind, 25, 25, 25, 25)
        else:
            bet_step(deck, player_0, player_1, player_2, player_3, player_4, blind, 22, 22, 22, 22)
            bet_step(deck, player_1, player_0, player_2, player_3, player_4, blind, 22, 23, 23, 23)
            bet_step(deck, player_2, player_0, player_1, player_3, player_4, blind, 23, 23, 24, 24)
            bet_step(deck, player_3, player_0, player_1, player_2, player_4, blind, 24, 24, 24, 25)
            bet_step_model(deck, model_bet,  player_4, player_0, player_1, player_2, player_3, blind, 25, 25, 25, 25)
        final_open = {}
        bet_summary(player_0, final_open)
        bet_summary(player_1, final_open)
        bet_summary(player_2, final_open)
        bet_summary(player_3, final_open)
        bet_summary(player_4, final_open)
        result = process_final_open(final_open, deck)
        if result is None:
            pass
        elif result == 'player_0' and epoch<= test_epochs/5:
            model_wins += 1
            p0_win += 1
        elif result == 'player_1' and epoch>test_epochs/5 and epoch<=test_epochs*2/5:
            model_wins += 1
            p1_win += 1
        elif result == 'player_2' and epoch>test_epochs*2/5 and epoch<=test_epochs*3/5:
            model_wins += 1
            p2_win += 1
        elif result == 'player_3' and epoch>test_epochs*3/5 and epoch<=test_epochs*4/5:
            model_wins += 1
            p3_win += 1
        elif result == 'player_4' and epoch>test_epochs*3/5 and epoch<=test_epochs:
            model_wins += 1
            p4_win += 1
    print ("model_wins", model_wins)
    print (p0_win, p1_win, p2_win, p3_win, p4_win)
    if model_wins >= 275:
        print ("model_wins:", True)
        return True
    else:
        model_wins = 0
        print ("model_wins:", False)
        return False

def causal_game_with_previous_bet(model_previous, model_current):
    test_epochs = 1000
    model_current_wins = 0
    epoch = 0
    p0_win = 0
    p1_win = 0
    p2_win = 0
    p3_win = 0
    p4_win = 0
    draws = 0
    while epoch<test_epochs:
        epoch += 1
        blind = 1
        player_0 = player(name_='player_0')
        player_1 = player(name_='player_1')
        player_2 = player(name_='player_2')
        player_3 = player(name_='player_3')
        player_4 = player(name_='player_4')
        deck = library(pool = 1)
        deck.refresh()
        deck.place()
        first_card(deck, player_0, player_1, player_2, player_3, player_4)
        player_0.draw(deck.drawn())
        player_1.draw(deck.drawn())
        player_2.draw(deck.drawn())
        player_3.draw(deck.drawn())
        player_4.draw(deck.drawn())
        # get_break_points_model_selfplay
        get_break_points(deck, player_0, player_1, player_2, player_3, player_4, 17, 17, 17, 17)
        get_break_points(deck, player_1, player_0, player_2, player_3, player_4, 17, 18, 18, 18)
        get_break_points(deck, player_2, player_0, player_1, player_3, player_4, 18, 18, 19, 19)
        get_break_points(deck, player_3, player_0, player_1, player_2, player_4, 19, 19, 19, 20)
        get_break_points(deck, player_4, player_0, player_1, player_2, player_3, 20, 20, 20, 20)
        public_info(deck, player_0)
        public_info(deck, player_1)
        public_info(deck, player_2)
        public_info(deck, player_3)
        public_info(deck, player_4)
        if epoch<= test_epochs/5:
            bet_step_model(deck, model_current, player_0, player_1, player_2, player_3, player_4, blind, 22, 22, 22, 22)
            bet_step_model(deck, model_previous,player_1, player_0, player_2, player_3, player_4, blind, 22, 23, 23, 23)
            bet_step_model(deck, model_previous,player_2, player_0, player_1, player_3, player_4, blind, 23, 23, 24, 24)
            bet_step_model(deck, model_previous,player_3, player_0, player_1, player_2, player_4, blind, 24, 24, 24, 25)
            bet_step_model(deck, model_previous,player_4, player_0, player_1, player_2, player_3, blind, 25, 25, 25, 25)
        elif epoch>test_epochs/5 and epoch<=test_epochs*2/5:
            bet_step_model(deck, model_previous,player_0, player_1, player_2, player_3, player_4, blind, 22, 22, 22, 22)
            bet_step_model(deck, model_current, player_1, player_0, player_2, player_3, player_4, blind, 22, 23, 23, 23)
            bet_step_model(deck, model_previous,player_2, player_0, player_1, player_3, player_4, blind, 23, 23, 24, 24)
            bet_step_model(deck, model_previous,player_3, player_0, player_1, player_2, player_4, blind, 24, 24, 24, 25)
            bet_step_model(deck, model_previous,player_4, player_0, player_1, player_2, player_3, blind, 25, 25, 25, 25)
        elif epoch>test_epochs*2/5 and epoch<=test_epochs*3/5:
            bet_step_model(deck, model_previous,player_0, player_1, player_2, player_3, player_4, blind, 22, 22, 22, 22)
            bet_step_model(deck, model_previous,player_1, player_0, player_2, player_3, player_4, blind, 22, 23, 23, 23)
            bet_step_model(deck, model_current, player_2, player_0, player_1, player_3, player_4, blind, 23, 23, 24, 24)
            bet_step_model(deck, model_previous,player_3, player_0, player_1, player_2, player_4, blind, 24, 24, 24, 25)
            bet_step_model(deck, model_previous,player_4, player_0, player_1, player_2, player_3, blind, 25, 25, 25, 25)
        elif epoch>test_epochs*3/5 and epoch<=test_epochs*4/5:
            bet_step_model(deck, model_previous,player_0, player_1, player_2, player_3, player_4, blind, 22, 22, 22, 22)
            bet_step_model(deck, model_previous,player_1, player_0, player_2, player_3, player_4, blind, 22, 23, 23, 23)
            bet_step_model(deck, model_previous,player_2, player_0, player_1, player_3, player_4, blind, 23, 23, 24, 24)
            bet_step_model(deck, model_current, player_3, player_0, player_1, player_2, player_4, blind, 24, 24, 24, 25)
            bet_step_model(deck, model_previous,player_4, player_0, player_1, player_2, player_3, blind, 25, 25, 25, 25)
        else:
            bet_step_model(deck, model_previous,player_0, player_1, player_2, player_3, player_4, blind, 22, 22, 22, 22)
            bet_step_model(deck, model_previous,player_1, player_0, player_2, player_3, player_4, blind, 22, 23, 23, 23)
            bet_step_model(deck, model_previous,player_2, player_0, player_1, player_3, player_4, blind, 23, 23, 24, 24)
            bet_step_model(deck, model_previous,player_3, player_0, player_1, player_2, player_4, blind, 24, 24, 24, 25)
            bet_step_model(deck, model_current, player_4, player_0, player_1, player_2, player_3, blind, 25, 25, 25, 25)
        final_open = {}
        bet_summary(player_0, final_open)
        bet_summary(player_1, final_open)
        bet_summary(player_2, final_open)
        bet_summary(player_3, final_open)
        bet_summary(player_4, final_open)
        result = process_final_open(final_open, deck)
        if result is None:
            draws += 1
        elif result == 'player_0' and epoch<= test_epochs/5:
            model_current_wins += 1
            p0_win += 1
        elif result == 'player_1' and epoch>test_epochs/5 and epoch<=test_epochs*2/5:
            model_current_wins += 1
            p1_win += 1
        elif result == 'player_2' and epoch>test_epochs*2/5 and epoch<=test_epochs*3/5:
            model_current_wins += 1
            p2_win += 1
        elif result == 'player_3' and epoch>test_epochs*3/5 and epoch<=test_epochs*4/5:
            model_current_wins += 1
            p3_win += 1
        elif result == 'player_4' and epoch>test_epochs*3/5 and epoch<=test_epochs:
            model_current_wins += 1
            p4_win += 1
    print ("model_wins", model_current_wins)
    print ("draw games:", draws)
    print (p0_win, p1_win, p2_win, p3_win, p4_win)
    if model_current_wins >= 440:
        print ("model_wins:", True)
        return True
    else:
        model_current_wins = 0
        print ("model_wins:", False)
        return False

def self_play_trains_draw():
    self_play_steps = 0
    current_model = None
    converge_tag = 0
    while True:
        model_random = random_game_draw()
        if causal_game_with_random_draw(model_random) == True:
            print("随机模型合格，返回给current_model")
            current_model = model_random
            self_play_steps += 1
            break
        else:
            print("随机模型不合格")
            continue
    # current_model 确立
    while True:
        print("自对弈训练开始")
        new_model = model_self_play_train_draw(current_model)
        if converge_tag >= 5: 
            break
        if causal_game_with_previous_draw(new_model, current_model) == True:
            print("新模型合格，返回给current_model")
            current_model = model_random
            self_play_steps += 1
            print ("self_play_steps:", self_play_steps)
            converge_tag = 0
            continue
        else:
            print("新模型不合格")
            converge_tag += 1
            continue
    print ("新模型已经收敛。")
    current_model.save(r'model_data/model_draw.h5')
    
def self_play_trains_discard():
    self_play_steps = 0
    current_model = None
    converge_tag = 0
    while True:
        model_random = random_game_discard()
        if causal_game_with_random_discard(model_random) == True:
            print("随机模型合格，返回给current_model")
            current_model = model_random
            self_play_steps += 1
            break
        else:
            print("随机模型不合格")
            continue
    # current_model 确立
    while True:
        print("自对弈训练开始")
        new_model = model_self_play_train_discard(current_model)
        if converge_tag >= 5: 
            break
        if causal_game_with_previous_discard(new_model, current_model) == True:
            print("新模型合格，返回给current_model")
            current_model = model_random
            self_play_steps += 1
            print ("self_play_steps:", self_play_steps)
            converge_tag = 0
            continue
        else:
            print("新模型不合格")
            converge_tag += 1
            continue
    print ("新模型已经收敛。")
    current_model.save(r'model_data/model.h5')
    
def self_play_trains_bet():
    self_play_steps = 0
    current_model = None
    converge_tag = 0
    while True:
        model_random = random_game_bet()
        if causal_game_with_random_bet(model_random) == True:
            print("随机模型合格，返回给current_model")
            current_model = model_random
            self_play_steps += 1
            break
        else:
            print("随机模型不合格")
            continue
    # current_model 确立
    while True:
        print("自对弈训练开始")
        new_model = model_self_play_train_bet(current_model)
        if converge_tag >= 5: 
            break
        if causal_game_with_previous_bet(new_model, current_model) == True:
            print("新模型合格，返回给current_model")
            current_model = model_random
            self_play_steps += 1
            print ("self_play_steps:", self_play_steps)
            converge_tag = 0
            continue
        else:
            print("新模型不合格")
            converge_tag += 1
            continue
    print ("新模型已经收敛。")
    current_model.save(r'model_data/model_bet.h5')
    
if __name__=='__main__':
    self_play_trains_bet()
    # random_game('draw')