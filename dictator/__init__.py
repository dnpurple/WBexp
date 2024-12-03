
from otree.api import *
c = cu

doc = ''
class C(BaseConstants):
    NAME_IN_URL = 'dictator'
    PLAYERS_PER_GROUP = 2
    ENDOWMENTS = 5
    NUM_ROUNDS = 1
    ROLES = ('Dictator', 'Receiver')
class Subsession(BaseSubsession):
    pass
def creating_session(subsession: Subsession):
    session = subsession.session
    from random import shuffle
    
    ps = subsession.get_players()
    shuffle(ps)
    
    pairs = [ps[n: n + C.PLAYERS_PER_GROUP] for n in range(0, len(ps), C.PLAYERS_PER_GROUP)]
    for pair in pairs:
        pair[0].task_role = C.ROLES[0]
        pair[1].task_role = C.ROLES[1]
    
    subsession.set_group_matrix(pairs)
    
    
    
class Group(BaseGroup):
    decision = models.IntegerField(label='What do you want to send to the other player?', max=C.ENDOWMENTS, min=0)
def set_payoff(group: Group):
    dictator = group.get_player_by_id(1)
    receiver = group.get_player_by_id(2)
    
    dictator.payoff = C.ENDOWMENTS - group.decision 
    receiver.payoff = group.decision 
class Player(BasePlayer):
    task_role = models.StringField(choices=C.ROLES)
class Instructions(Page):
    form_model = 'player'
class Decision(Page):
    form_model = 'group'
    form_fields = ['decision']
    @staticmethod
    def is_displayed(player: Player):
        group = player.group
        return player.id_in_group == 1
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        set_payoff(group)
class WaitingDecision(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        group = player.group
        return player.id_in_group == 2
class Results(Page):
    form_model = 'player'
page_sequence = [Instructions, Decision, WaitingDecision, Results]