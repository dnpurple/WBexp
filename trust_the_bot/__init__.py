
from otree.api import *
c = cu

doc = ''
class C(BaseConstants):
    NAME_IN_URL = 'trust_the_bot'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    ENDOWMENT = 100
    MULTIPLIER = 2
    WAITING_MIN_MAX = (10, 100)
class Subsession(BaseSubsession):
    pass
class Group(BaseGroup):
    pass
class Player(BasePlayer):
    send = models.IntegerField(label='How much do you want to sens to the bot?', max=C.ENDOWMENT, min=0)
    returned = models.IntegerField()
def bot_heuristic(player: Player):
    if player.send <= C.ENDOWMENT/2:
        player.returned = 0
    
    else:
        player.returned = round(player.send*C.MULTIPLIER/2, 2)
def set_payoff(player: Player):
    bot_heuristic(player)
    player.payoff = C.ENDOWMENT - player.send + player.returned
class Decision(Page):
    form_model = 'player'
    form_fields = ['send']
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        set_payoff(player)
class WaitingResults(Page):
    form_model = 'player'
    @staticmethod
    def get_timeout_seconds(player: Player):
        from random import randint
        return randint(*C.WAITING_MIN_MAX)
page_sequence = [Decision, WaitingResults]