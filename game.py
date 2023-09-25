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
    def net_income(self):
        return self.currency_after - self.currency_before
    def order(self, number: int):
        self.matrix[number] = 1
    def draw_game(self):
        self.currency_after = self.currency_before
    def temp_reset(self):
        self.currency_before = self.currency_after


def get_break_points(current_player, _1_player, _2_player, _3_player, _4_player, w,x,y,z):
    current_player_draw_or_not_samples = copy.deepcopy(current_player.matrix)
    current_player_discard_samples = copy.deepcopy(current_player.matrix)
    # 抓/翻模型断点
    if randint(0,1) == 1: #draw
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
    player_0.bet()
    player_0.currency_after -= blind
    deck.pool += blind
    player_0.matrix[147] = blind
    player_1.matrix[w] = blind
    player_2.matrix[x] = blind
    player_3.matrix[y] = blind
    player_4.matrix[z] = blind

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

if __name__ == '__main__':
    rounds = 0
    draw_or_not_samples = []
    discard_samples = []
    bet_or_not_samples = []
    net_incomes = []
    while rounds< 1:
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
        player_0.order(0)
        player_1.order(1)
        player_2.order(2)
        player_3.order(3)
        player_4.order(4)
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
        player_0_draw_or_not_samples, player_0_discard_samples = get_break_points(player_0, player_1, player_2, player_3, player_4, 38, 38, 38, 38)
        player_1_draw_or_not_samples, player_1_discard_samples = get_break_points(player_1, player_0, player_2, player_3, player_4, 38, 39, 39, 39)
        player_2_draw_or_not_samples, player_2_discard_samples = get_break_points(player_2, player_0, player_1, player_3, player_4, 39, 39, 40, 40)
        player_3_draw_or_not_samples, player_3_discard_samples = get_break_points(player_3, player_0, player_1, player_2, player_4, 40, 40, 40, 41)
        player_4_draw_or_not_samples, player_4_discard_samples = get_break_points(player_4, player_0, player_1, player_2, player_3, 41, 41, 41, 41)
        print ("牌库剩余：", deck.hand)
        print ("总弃牌堆：", deck.drop)
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
        player_0_library_assumption = copy.copy(player_0.matrix)
        player_1_library_assumption = copy.copy(player_1.matrix)
        player_2_library_assumption = copy.copy(player_2.matrix)
        player_3_library_assumption = copy.copy(player_3.matrix)
        player_4_library_assumption = copy.copy(player_4.matrix)
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
        elif result == 'player_1':
            player_1.currency_after += deck.pool
        elif result == 'player_2':
            player_2.currency_after += deck.pool
        elif result == 'player_3':
            player_3.currency_after += deck.pool
        elif result == 'player_4':
            player_4.currency_after += deck.pool
        player_0.temp_reset()
        player_1.temp_reset()
        player_2.temp_reset()
        player_3.temp_reset()
        player_4.temp_reset()
        draw_or_not_samples.append(player_0_draw_or_not_samples)
        discard_samples.append(player_0_discard_samples)
        bet_or_not_samples.append(player_0_bet_or_not_samples)
        net_incomes.append(player_0.net_income)
        draw_or_not_samples.append(player_1_draw_or_not_samples)
        discard_samples.append(player_1_discard_samples)
        bet_or_not_samples.append(player_1_bet_or_not_samples)
        net_incomes.append(player_1.net_income)
        draw_or_not_samples.append(player_2_draw_or_not_samples)
        discard_samples.append(player_2_discard_samples)
        bet_or_not_samples.append(player_2_bet_or_not_samples)
        net_incomes.append(player_2.net_income)
        draw_or_not_samples.append(player_3_draw_or_not_samples)
        discard_samples.append(player_3_discard_samples)
        bet_or_not_samples.append(player_3_bet_or_not_samples)
        net_incomes.append(player_3.net_income)
        draw_or_not_samples.append(player_4_draw_or_not_samples)
        discard_samples.append(player_4_discard_samples)
        bet_or_not_samples.append(player_4_bet_or_not_samples)
        net_incomes.append(player_4.net_income)
    print("到这为止正常。")
    print("start train.")
    model_draw, model_discard, model_bet = make_models()
    model_draw.fit(draw_or_not_samples, net_incomes, epochs=200, verbose=0)
    model_discard.fit(discard_samples, net_incomes, epochs=200, verbose=0)
    model_bet.fit(bet_or_not_samples, net_incomes, epochs=200, verbose=0)
    print("end train.")