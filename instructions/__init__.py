from otree.api import *

class C(BaseConstants):
    NAME_IN_URL = 'instructions'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    pass

class Instructions(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return {
            'treatment_probability': int(player.session.config['treatment_probability'] * 100),  # Convert to percentage
            'interference_level': player.session.config['interference_level']  # Pass interference level to template
        }




page_sequence = [Instructions]
