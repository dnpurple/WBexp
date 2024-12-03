
from otree.api import *
c = cu

doc = ''
class C(BaseConstants):
    NAME_IN_URL = 'end'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
class Subsession(BaseSubsession):
    pass
class Group(BaseGroup):
    pass
class Player(BasePlayer):
    my_field = models.IntegerField()
class Results(Page):
    form_model = 'player'
    @staticmethod
    def vars_for_template(player: Player):
        participant = player.participant
        participant = player.participant
        participant.payoff = cu(participant.vars.get('payoff_forcast', 0) + participant.payoff_collective_risk)
        
        participant.total_earnings = participant.payoff_plus_participation_fee()
        
        return dict()
page_sequence = [Results]