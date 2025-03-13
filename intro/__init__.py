
from otree.api import *
c = cu

doc = 'PartA'
class C(BaseConstants):
    NAME_IN_URL = 'wb_part_a'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    # MODULE - 6 - Exercise 1 (RET)
    NUM_ADDENDA = 3
    ADDENDUM_MAX_VALUE = 99

    # MODULE 7 - Exercise 4
    BONUS_PER_SOLVED_ADDITION = 100


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    # MODULE - 9 - Exercise 4 (Challenge)
    has_finished = models.BooleanField(initial=False)


class Player(BasePlayer):
    # MODULE - 6 - Exercise 3 (RET)
    num_attempts = models.IntegerField(initial=0)

    # MODULE - 6 - Exercise 4 (RET)
    num_solved = models.IntegerField(initial=0)


# FUNCTIONS
def get_addition(player: Player) -> list:
    from random import randint

    # MODULE - 6 - Exercise 1 (RET)
    # addenda = [randint(1, C.ADDENDUM_MAX_VALUE) for _ in range(C.NUM_ADDENDA)]
    # return addenda

    # MODULE - 6 - Exercise 7 (RET - Challenge)
    session = player.session
    config = session.config
    addenda = [
        randint(config.get('addendum_min_value', 1), config.get('addendum_max_value', C.ADDENDUM_MAX_VALUE))
        for _ in range(C.NUM_ADDENDA)
    ]
    return addenda


# MODULE - 6 - Exercise 4 (RET)
from typing import List
def is_correct(addition: List[int], answer: int) -> bool:
    return sum(addition) == answer


def live_ret_addition(player: Player, data: dict) -> dict:
    participant = player.participant

    # MODULE - 9 - Exercise 4
    group = player.group
    if group.has_finished:
        return

    if data['action'] == 'load':
        addition = participant.vars.setdefault('addition', get_addition(player))

        # MODULE - 6 - Exercise 6 (RET)
        data = dict(
            addition=participant.vars['addition'],
            num_attempts=player.num_attempts,
            num_solved=player.num_solved
        )
        return {player.id_in_group: data}

    else:

        print(data['answer'])

        # MODULE - 6 - Exercise 3 (RET)
        player.num_attempts += 1

        # MODULE - 6 - Exercise 4 (RET)
        if is_correct(participant.vars['addition'], int(data['answer'])):
            player.num_solved += 1

            # MODULE - 9 - Exercise 4
            if player.num_solved == 4:
                group.has_finished = True

        participant.vars['addition'] = get_addition(player)

        # MODULE - 6 - Exercise 6 (RET)
        data = dict(
            addition=participant.vars['addition'],
            num_attempts=player.num_attempts,
            num_solved=player.num_solved,

            # MODULE - 9 - Exercise 4
            has_finished=group.has_finished
        )

        # MODULE - 9 - Exercise 4
        if group.has_finished:
            return {0: data}
        else:
            return {player.id_in_group: data}


class RETBaseline(Page):
    @staticmethod
    def live_method(player: Player, data):
        return live_ret_addition(player, data)

    # MODULE - 6 - Exercise 2 (RET)
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            addenda=[n for n in range(1, C.NUM_ADDENDA + 1)]
        )

    # MODULE 9 - Exercise 4
    @staticmethod
    def is_displayed(player: Player):
        group = player.group
        return not group.has_finished

    # MODULE 7 - Exercise 4
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        participant.payoff_baseline = C.BONUS_PER_SOLVED_ADDITION * player.num_solved

    def get_timeout_seconds(player: Player):
        session = player.session
        return 60  # player.session.config['quiz_timeout_seconds']


class PartAInstructions(Page):
    form_model = 'player'

    timer_text = 'Time left:'

    @staticmethod
    def vars_for_template(player: Player):

        # Return a dictionary with `timeout_seconds` at the top level
        return {
            'timeout_seconds': PartAInstructions.get_timeout_seconds(player)  # Ensure it’s at the top level
        }

    @staticmethod
    def get_timeout_seconds(player: Player):
        if player.round_number == 1:
            return 65  # Shorter timeout for other rounds

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class ResultsWaitPage(WaitPage):
    #after_all_players_arrive = set_payoffs_and_calculate_beliefs
    pass



class BaselineResults(Page):
    form_model = 'player'

    timer_text = 'Time left:'

    @staticmethod
    def vars_for_template(player: Player):

        # Return a dictionary with `timeout_seconds` at the top level
        return {
            'timeout_seconds': BaselineResults.get_timeout_seconds(player)  # Ensure it’s at the top level
        }

    @staticmethod
    def get_timeout_seconds(player: Player):
        if player.round_number == 1:
            return 20  # Set a longer timeout for the first round if desired


    @staticmethod
    def is_displayed(player: Player):
        return True
        # Show this page in all rounds
class StartWaitPage(WaitPage):
    title_text = "Waiting to Start"
    body_text = "Please wait until all participants are ready and the experimenter starts the session."

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1  # Only show in the first round

    wait_for_all_groups = True  # Waits for all participants in the session

    # Optional: Add a timer if you want a max wait time (e.g., 10 minutes)
   # @staticmethod
    #def get_timeout_seconds(player: Player):
     #   return 600  # 10 minutes, adjust as needed

#class Welcome(Page):
 #   form_model = 'player'
#class PaymentInfo(Page):
 #   form_model = 'player'
#class GeneralInfo(Page):
 #   form_model = 'player'
page_sequence = [StartWaitPage, PartAInstructions, RETBaseline, BaselineResults, ResultsWaitPage]