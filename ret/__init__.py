from .helpers import get_player_by_participant_id


import random
from random import choice
from otree.api import *
c = cu


doc = 'real effort task'

class C(BaseConstants):
    NAME_IN_URL = 'wb_part_b'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 5
    NAME_IN_URL = 'ret'
    NUM_ADDENDA = 3
    ADDENDUM_MAX_VALUE = 99
    MULTIPLIER = 5
    ENDOWMENT = 500
   # BASELINE_ROUND = 1
    #GROUP_ROUNDS = [i for i in range(1, NUM_ROUNDS + 1)]  # Rounds from 2 to 15
    QUIZ_FIELDS = ('q1', 'q2', 'q3', 'q4')
    QUIZ_CORRECT = ('1', '2', '3', '1')
    REPORT_PENALTY_PROBABILITIES = (0.97,)
    #TREATMENT_PROBABILITIES = (0.8,)
    OFFER_CHOICES = (0,)
    MAX_PERCENTAGE = 50
    MAX_PERCENTAGE_PLUS_ONE = MAX_PERCENTAGE + 1
    PERCENTAGE_CHOICES = list(range(0, MAX_PERCENTAGE + 1, 10))  # Percent choices from 0% to 50% in increments of 10

    BONUS_PER_SOLVED_ADDITION = 100
    WORKER_REPORT_REWARD = 50  # For example, worker gets 50 points if report succeeds
    WORKER_REPORT_PENALTY = 20  # Worker loses 20 points if report fails
    MANAGER_REPORT_PENALTY = 100  # Manager loses 100 points if report succeeds
    INTERFERE_COST = 5
    TRANSFER_AMOUNT = 60
    ALPHA_LOW = 0.7  # Low interference (less corruption)
    ALPHA_HIGH = 0.3  # High interference (more corruption)
    SWITCH_ROUND = 3  # The round at which the treatment changes
class Subsession(BaseSubsession):
    def creating_session(self):
        print(f"DEBUG: Starting creating_session for Round {self.round_number}")
        for player in self.get_players():
            player.set_treatment_probability()
            print(
                f"DEBUG: Round {self.round_number}, Player {player.id_in_group}, Treatment Probability: {player.treatment_probability}")
        if self.round_number == 1:
            self.initialize_group_structure()
        print(f"DEBUG: Finished creating_session for Round {self.round_number}")

    def initialize_group_structure(self):
        if self.round_number == 1:
            players = self.get_players()

            random.shuffle(players)
            group_matrix = [players[i:i + C.PLAYERS_PER_GROUP] for i in range(0, len(players), C.PLAYERS_PER_GROUP)]
            self.set_group_matrix(group_matrix)

            print(f"DEBUG: Group matrix: {self.get_group_matrix()}")



            for player in self.get_players():
                print(
                    f"DEBUG: Player {player.id_in_group}, Participant ID: {player.participant.id}, Role: {player.get_role()}")

    def pair_managers_with_workers(self):
        players = self.get_players()
        managers = [p for p in players if p.get_role() == "Manager"]
        workers = [p for p in players if p.get_role() == "Worker"]

        # Ensure 3 managers and 3 workers (with 9 players, this should hold)
        if len(managers) != len(workers) or len(managers) < 1:
            raise ValueError(f"Mismatch: {len(managers)} managers, {len(workers)} workers.")

            # In full experiment, expect 3 managers and 3 workers; warn if not
        expected_num = 3  # For 9 players
        if len(managers) != expected_num:
            print(f"WARNING: Expected {expected_num} managers, got {len(managers)}. Running with available players.")

        # Shuffle workers for random pairing
        random.shuffle(workers)
        pairs = list(zip(managers, workers))

        # Store pairings for debugging
        self.session.vars['pairings'] = [
            {'manager_id': manager.participant.id, 'worker_id': worker.participant.id}
            for manager, worker in pairs
        ]

        # Assign pairings and set victim_worker_id
        for manager, worker in pairs:
            manager.participant.vars['paired_worker_id'] = worker.participant.id
            worker.participant.vars['paired_manager_id'] = manager.participant.id
            # Store the victim’s participant ID in the manager’s group
            print(f"DEBUG: Round {self.round_number}, Manager {manager.participant.id} "
                  f"(Group {manager.group.id_in_subsession}) paired with Worker {worker.participant.id} "
                  f"(Group {worker.group.id_in_subsession})")

        # Confirm assignments
        for player in players:
            print(f"DEBUG: Player {player.participant.id} vars: {player.participant.vars}")

        # Set default group fields and participant vars
        for group in self.get_groups():
            group.wants_to_take = True
            group.wants_to_pay_transfer = False
            for player in group.get_players():
                participant = player.participant
                participant.selected_round = None
                participant.selected_round_earnings = 0


    def set_random_round_payment(self):
        import random

        # Select a random round to be the payoff round
        random_round = random.randint(1, C.NUM_ROUNDS)

        # Loop through all players and set the earnings based on the randomly selected round
        for player in self.get_players():
            participant = player.participant
            player_in_selected_round = player.in_round(random_round)

            # Set the selected round and its earnings
            participant.vars['selected_round'] = random_round
            participant.vars['selected_round_earnings'] = int(player_in_selected_round.total_earnings)

            # Assign the earnings to participant payoff for final display
            participant.payoff = participant.vars['selected_round_earnings']


class Group(BaseGroup):
    offer_accepted = models.BooleanField()
    amount_offered = models.IntegerField(choices=C.OFFER_CHOICES)
    authority_transfer_asked = models.BooleanField(choices=[[True, 'Yes'], [False, 'No']], label='Do you want accept a transfer?', widget=widgets.RadioSelectHorizontal)

    victim_worker_id = models.IntegerField()  # Add a field to store the victim's ID
    authority_accepted_transfer = models.BooleanField(choices=[[True, 'Yes'], [False, 'No']], label ='',widget=widgets.RadioSelectHorizontal, initial=False)  # <-- Add this field


    min_report_percentage_other_worker = models.IntegerField(
        label="Minimum percentage taken for you to report if the manager took from another worker",
        initial=25
    )
    min_report_percentage_self = models.IntegerField(
        label="Minimum percentage taken for you to report if the manager took from you",
        initial=25
    )

    authority_minimum_transfer = models.IntegerField(
        label="Minimum transfer you will accept (0 accepts any transfer, none rejects all.)",  initial=C.INTERFERE_COST
    )
    report_decision = models.BooleanField(initial=False)
    wants_to_take = models.BooleanField(choices=[[True, 'Yes'], [False, 'No']], label = 'Do you want to take from the worker’s earnings?')
    wants_to_pay_transfer = models.BooleanField(choices=[[True, 'Yes'], [False, 'No']],label ='',widget=widgets.RadioSelectHorizontal, initial=False)

    percentage_taken = models.IntegerField(blank=True)  # Allow blank if not taking
    #transfer_amount = models.IntegerField(blank=True)  # Allow blank if not transferring
    transfer_amount = models.IntegerField(
        min=0,
        blank=True,  # Set to True if transfer amount is optional
        doc="Amount offered by the manager for the authority's acceptance."
    )


class Player(BasePlayer):
    treatment_probability = models.FloatField()
    timeout_flag = models.BooleanField(initial=False)
    group_result = models.IntegerField(initial=0)
    num_attempts = models.IntegerField(initial=0)
    num_solved = models.IntegerField(initial=0)
    my_field2 = models.IntegerField()
    q1 = models.IntegerField(choices=[[1, 'Yes'], [2, 'No']], label='1.  Do you play in groups?', widget=widgets.RadioSelect)
    q1_num_errors = models.IntegerField(initial=0)
    q2 = models.IntegerField(choices=[[1, 'yes'], [2, 'no']], label='Will your group members change?', widget=widgets.RadioSelect)
    q2_num_errors = models.IntegerField(initial=0)
    q3 = models.IntegerField(choices=[[1, '1'], [2, '2'], [3, '3'], [4, '4']], label='How many numbers will you add to earn ECUs  ', widget=widgets.RadioSelect)
    q3_num_errors = models.IntegerField(initial=0)
    q4 = models.IntegerField(choices=[[1, 'Authority'], [2, 'Worker'], [3, 'Manager']], label='Who earns ECUs even is they do not any numbers correctly?', widget=widgets.RadioSelect)
    q4_num_errors = models.IntegerField(initial=0)
    effort_points = models.IntegerField()

    total_earnings = models.IntegerField(initial=0)  # To track all earnings
    report_successful = models.BooleanField(initial=False, doc="Whether the worker's report succeeded")
    worker_reported = models.BooleanField(initial=False, doc="Whether the worker chose to report their manager")
    intended_to_report = models.BooleanField(initial=False, doc="Whether the worker intended to report their manager")
    report_would_have_succeeded = models.BooleanField(initial=False,
                                                      doc="Whether the intended report would have succeeded")

    points_earned = models.IntegerField(initial=0)  # Earnings from the RET task
    transfer_earnings = models.IntegerField(initial=0)  # Earnings/deductions from transfers and reports
    #belief_earnings = models.IntegerField(initial=0)  # Earnings from belief elicitation

    report_earnings = models.IntegerField(initial=0)  # Earnings from report/reward mechanics
    manager_earnings = models.IntegerField(initial=0)  # Manager's custom earnings
    authority_earnings = models.IntegerField(initial=0)  # Authority's custom earnings
    #belief_payoff = models.IntegerField(initial=0)


    amount_lost = models.IntegerField(initial=0)
    manager_take_earnings = models.IntegerField(initial=0)

    player_role = models.StringField(initial="Unknown")  # Add role explicitly
    unique_id = models.StringField()  # A unique identifier for each player

    def set_treatment_probability(self):
        treatment_order = self.session.config.get("treatment_order", "low_to_high")
        if treatment_order == "low_to_high":
            self.treatment_probability = C.ALPHA_LOW if self.round_number <= C.SWITCH_ROUND else C.ALPHA_HIGH
        else:  # high_to_low
            self.treatment_probability = C.ALPHA_HIGH if self.round_number <= C.SWITCH_ROUND else C.ALPHA_LOW
        print(
            f"DEBUG: Player {self.id_in_group}, Round {self.round_number}, Set Treatment Probability: {self.treatment_probability}")
        return self.treatment_probability

    def get_role(self):
        if self.id_in_group == 1:
            return "Worker"
        elif self.id_in_group == 2:
            return "Manager"
        elif self.id_in_group == 3:
            return "Authority"
        else:
            return "Unknown Role"


def live_ret_addition(player: Player, data):
    group = player.group
    participant = player.participant


    participant = player.participant
    if data['action'] == 'load':
        if 'addition' not in participant.vars:
            participant.vars['addition'] = get_addition(player)
        data = dict(
                addition=participant.vars['addition'],
                num_attempts=player.num_attempts,
                num_solved=player.num_solved
            )


        return {player.id_in_group: data}

    else:
         print(data['answer'])


         player.num_attempts += 1

         if sum(participant.vars['addition']) == int(data['answer']):
              player.num_solved += 1

         participant.vars['addition'] = get_addition(player)


         data = dict(
                addition=participant.vars['addition'],
                num_attempts=player.num_attempts,
                num_solved=player.num_solved
            )
         return {player.id_in_group: data}

         player.payoff = C.MULTIPLIER * player.num_solved
def get_addition(player: Player):
    session = player.session
    from random import randint

    #addenda = [randint(1, C.ADDENDUM_MAX_VALUE) for _ in range(C.NUM_ADDENDA)]
    #return addenda

    session = player.session
    config = session.config
    addenda = [
        randint(config.get('addendum_min_value', 1), config.get('addendum_max_value', C.ADDENDUM_MAX_VALUE))
        for _ in range(C.NUM_ADDENDA)
    ]
    return addenda


def set_payoffs(group: Group):
    manager = group.get_player_by_id(2)
    authority = group.get_player_by_id(3)
    worker_in_group = group.get_player_by_id(1)  # The worker in this group who can report

    # Find the paired victim worker (who loses earnings)
    victim_participant_id = manager.participant.vars.get('paired_worker_id')
    victim_worker = None
    for p in group.subsession.get_players():
        if p.participant.id == victim_participant_id:
            victim_worker = p
            break
    if not victim_worker:
        raise ValueError(f"Manager {manager.participant.id} has invalid victim_worker_participant_id: {victim_participant_id}")

    worker_earnings = victim_worker.points_earned

    # Manager theft logic (affects the paired victim worker)
    if not group.wants_to_take:
        group.percentage_taken = 0
    else:
        group.percentage_taken = group.field_maybe_none('percentage_taken') or 0

    if group.percentage_taken > 0:
        amount_taken = int((group.percentage_taken / 100) * worker_earnings)
        manager.manager_take_earnings = manager.points_earned + amount_taken
        victim_worker.amount_lost = amount_taken
    else:
        manager.manager_take_earnings = manager.points_earned
        victim_worker.amount_lost = 0

    # Transfer logic
    if group.wants_to_take and group.wants_to_pay_transfer:
        group.authority_transfer_asked = True
        authority_accepted_transfer = group.field_maybe_none('authority_accepted_transfer') or False
        if authority_accepted_transfer:
            authority.authority_earnings = C.TRANSFER_AMOUNT - C.INTERFERE_COST
            manager.transfer_earnings = C.TRANSFER_AMOUNT
            group.authority_accepted_transfer = True
        else:
            authority.authority_earnings = 0
            manager.transfer_earnings = 0
            group.authority_accepted_transfer = False
    else:
        group.authority_transfer_asked = False
        group.authority_accepted_transfer = False
        authority.authority_earnings = 0
        manager.transfer_earnings = 0

    # Reporting logic (in-group worker reports based on their manager’s actions)
    is_victim = worker_in_group == victim_worker
    report_threshold = (
        group.min_report_percentage_self if is_victim else group.min_report_percentage_other_worker
    )
    # If threshold is 51, no report is intended
    worker_in_group.intended_to_report = (
        report_threshold is not None and report_threshold < 51 and report_threshold <= group.percentage_taken
    )
    worker_in_group.set_treatment_probability()
    worker_in_group.report_would_have_succeeded = worker_in_group.intended_to_report and random.uniform(0, 1) < (
        worker_in_group.treatment_probability if group.authority_accepted_transfer else C.REPORT_PENALTY_PROBABILITIES[0]
    )
    worker_in_group.worker_reported = worker_in_group.intended_to_report  # Report only if intended
    worker_in_group.report_successful = worker_in_group.worker_reported and worker_in_group.report_would_have_succeeded

    # Earnings adjustments
    if worker_in_group.worker_reported and group.percentage_taken > 0:
        if worker_in_group.report_successful:
            worker_in_group.report_earnings = C.WORKER_REPORT_REWARD
            manager.total_earnings = 0  # Manager loses all earnings if report succeeds
        else:
            worker_in_group.report_earnings = -C.WORKER_REPORT_PENALTY
            manager.total_earnings = manager.manager_take_earnings - manager.transfer_earnings
    else:
        worker_in_group.report_earnings = 0
        manager.total_earnings = manager.manager_take_earnings - manager.transfer_earnings

    # Set total_earnings for all players
    if is_victim:
        # If the in-group worker is the victim, include amount_lost and report_earnings
        worker_in_group.total_earnings = worker_in_group.points_earned - worker_in_group.amount_lost + worker_in_group.report_earnings
    else:
        # Non-victim in-group worker only gets points_earned + report_earnings
        worker_in_group.total_earnings = worker_in_group.points_earned + worker_in_group.report_earnings
        # Victim worker (not in group) only loses amount_lost
        victim_worker.total_earnings = victim_worker.points_earned - victim_worker.amount_lost

    manager.total_earnings = manager.total_earnings  # Already set above
    authority.total_earnings = authority.points_earned + authority.authority_earnings

    # Set payoffs
    manager.payoff = manager.total_earnings
    authority.payoff = authority.total_earnings
    worker_in_group.payoff = worker_in_group.total_earnings
    if not is_victim:  # Only set victim_worker.payoff if different from worker_in_group
        victim_worker.payoff = victim_worker.total_earnings

    print(f"DEBUG: Round {group.subsession.round_number}, Group {group.id_in_subsession}: "
          f"Victim Worker {victim_worker.participant.id} (Group {victim_worker.group.id_in_subsession}), "
          f"Points Earned: {victim_worker.points_earned}, Amount Lost: {victim_worker.amount_lost}, "
          f"Total Earnings: {victim_worker.total_earnings}")
    print(f"DEBUG: In-Group Worker {worker_in_group.participant.id}, "
          f"Intended: {worker_in_group.intended_to_report}, Reported: {worker_in_group.worker_reported}, "
          f"Success: {worker_in_group.report_successful}, Total Earnings: {worker_in_group.total_earnings}")
    print(f"DEBUG: Manager {manager.participant.id} Earnings: {manager.total_earnings}, Payoff: {manager.payoff}")
    print(f"DEBUG: Authority {authority.participant.id} Earnings: {authority.total_earnings}")


#class Quiz(Page):
 #   form_model = 'player'
  #  form_fields = ['q1', 'q2', 'q3', 'q4']
   # timer_text = 'Time left:'
    #@staticmethod
  #  def is_displayed(player: Player):
   #     return player.round_number == 1
    #@staticmethod
 #   def vars_for_template(player: Player):
  #      payoff_example = round(C.ENDOWMENT- 20 + 300 * C.MULTIPLIER/C.PLAYERS_PER_GROUP, 2)
   #     return dict(
    #        payoff_example_tag=payoff_example
     #   )

    #@staticmethod
    #def get_timeout_seconds(player: Player):
     #   session = player.session
      #  return 6  # player.session.config['quiz_timeout_seconds']

class RET(Page):
    form_model = 'player'
    timer_text = 'Time left:'
    live_method = 'live_ret_addition'
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            addenda=[n for n in range(1, C.NUM_ADDENDA + 1)]
        )

    @staticmethod
    def get_timeout_seconds(player: Player):
        session = player.session
        return 60  # player.session.config['quiz_timeout_seconds']



class ManagerDecisionPage(Page):
    form_model = 'group'
    form_fields = ['wants_to_take', 'percentage_taken', 'wants_to_pay_transfer']
    timer_text = 'Time left:'

    @staticmethod
    def error_message(player, values):
        errors = {}

        print(
            f"DEBUG: Error Message Input - Wants to Take: {values.get('wants_to_take')}, Wants to Pay Transfer: {values.get('wants_to_pay_transfer')}, Percentage Taken: {values.get('percentage_taken')}")

        # Check if the player selected "Yes" for `wants_to_take` and provided `percentage_taken`
        if values['wants_to_take'] and (
                values['percentage_taken'] is None or not (1 <= values['percentage_taken'] <= 50)):
            errors['percentage_taken'] = "Please enter a percentage between 1 and 50."

        # Ensure transfer and percentage are only valid if taking
        if not values['wants_to_take']:
            values['wants_to_pay_transfer'] = False
            values['percentage_taken'] = 0  # Default to 0 if not taking
        elif not values['wants_to_take'] and values.get('wants_to_pay_transfer') is True:
            errors['wants_to_pay_transfer'] = "You cannot offer a transfer if you are not taking from the worker."
        print(f"DEBUG: Error Message Output - Wants to Take: {values['wants_to_take']}, Wants to Pay Transfer: {values['wants_to_pay_transfer']}")
        # Check if the player selected "Yes" for `wants_to_take` and provided `percentage_taken`
        #if values['wants_to_take'] == 'Yes' and (
         #       values['percentage_taken'] is None or not (1 <= values['percentage_taken'] <= 50)):
          #  errors['percentage_taken'] = "Please enter a percentage between 1 and 50."

            # Check if the player selected "Yes" for `wants_to_pay_transfer`, but only if they took
           # if values['wants_to_take'] and values['wants_to_pay_transfer']:
            #    pass  # No need to check transfer_amount since it's fixed

            # If no theft, reset transfer options
            #if not values['wants_to_take']:
             #   values['wants_to_pay_transfer'] = False

        # Check if the player selected "Yes" for `wants_to_pay_transfer` and provided `transfer_amount`
        #if values['wants_to_pay_transfer'] == 'Yes' and (
         #       values['transfer_amount'] is None or values['transfer_amount'] < 1):
          #  errors[
           #     'transfer_amount'] = f"Please specify a transfer amount of at least {player.group.interfere_cost} ECUs."

        return errors if errors else None

    @staticmethod
    def get_timeout_seconds(player: Player):
        return 180 if player.round_number == 1 or player.round_number == C.SWITCH_ROUND else 90
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        # Retrieve the paired worker for this manager
        paired_worker_id = player.participant.vars.get('paired_worker_id')
        worker = get_player_by_participant_id(group, paired_worker_id) if paired_worker_id else None
        print(f"DEBUG: Manager {player.id_in_group}, Paired Worker ID: {paired_worker_id}, Worker: {worker}")
        #timeout_seconds = ManagerDecisionPage.get_timeout_seconds(player)
        player.set_treatment_probability()

        return {
            'worker_id': paired_worker_id,
            'worker_solved_problems': worker.num_solved if worker else 0,  # Fallback if worker is None
            'worker_points_earned': worker.points_earned if worker else 0,  # Fallback if worker is None
            'percentage_choices': C.PERCENTAGE_CHOICES,
            'report_penalty_probabilities': C.REPORT_PENALTY_PROBABILITIES[0],
            'treatment_probability': player.treatment_probability,
            'interfere_cost': C.INTERFERE_COST,
            'timeout_seconds': ManagerDecisionPage.get_timeout_seconds(player),
            'can_offer_transfer': group.wants_to_take,  # Only allow transfer if taking
            'wants_to_take': group.wants_to_take,  # Pass current state for toggle logic

        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        paired_worker_id = player.participant.vars.get('paired_worker_id')
        paired_worker = get_player_by_participant_id(group, paired_worker_id) if paired_worker_id else None

        # Handle timeout scenario
        if timeout_happened:
            player.timeout_flag = True
            # On timeout, reset transfer and percentage if not taking
            if not group.wants_to_take:
                group.wants_to_pay_transfer = False
                group.percentage_taken = 0

        # Reset transfer_amount if the manager chooses not to pay a transfer
        #if group.wants_to_pay_transfer == 'No':
         #   group.transfer_amount = 0

        # Reset percentage_taken if the manager chooses not to take from the worker
        #if group.wants_to_take == 'No':
         #   group.percentage_taken = 0

            # Ensure transfer options are disabled if no theft
            if not group.wants_to_take:
                group.wants_to_pay_transfer = False
                group.percentage_taken = 0
            else:
                percentage_taken = group.field_maybe_none('percentage_taken') or 0
                if paired_worker and percentage_taken > 0:
                    amount_taken = int((percentage_taken / 100) * paired_worker.points_earned)
                    player.manager_take_earnings = player.points_earned + amount_taken
                    paired_worker.amount_lost = amount_taken
                else:
                    player.manager_take_earnings = player.points_earned
                    if paired_worker:
                        paired_worker.amount_lost = 0

            print(
                f"DEBUG: Before Next Page Output - Wants to Take: {group.wants_to_take}, Wants to Pay Transfer: {group.wants_to_pay_transfer}")

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2  # Only for the Manager

    #@staticmethod
    #def get_timeout_seconds(player: Player):
     #   return 120  # Adjust the time limit as needed

    #@staticmethod
    #def before_next_page(player: Player, timeout_happened):
        # Store timeout status to prompt user in template if they timed out
     #   player.participant.vars['worker_page_timeout'] = timeout_happened


class WorkerPage(Page):
    import random
    form_model = 'group'
    form_fields = ['min_report_percentage_other_worker', 'min_report_percentage_self']
    timer_text = 'Time left:'

    # Define timeout as a class variable, and use it directly in `vars_for_template`
   # timeout_seconds = 120  # Adjust this time limit as needed

    @staticmethod
    def get_timeout_seconds(player: Player):
        return 180 if player.round_number == 1 or player.round_number == C.SWITCH_ROUND else 90


    #def get_timeout_seconds(player: Player):
        # Setting different timers based on the round or conditions
     #   if player.round_number == 1:
      #      return 1200  # Longer timer for the first round
       # else:
        #    return 800  # Shorter timer for other rounds

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1  # Only display for Workers

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        if timeout_happened:
            player.timeout_flag = True  # Handle any server-side timeout logic here

        # Ensure the report thresholds are valid
        if group.field_maybe_none('min_report_percentage_other_worker') is None:
            group.min_report_percentage_other_worker = random.randint(1,
                                                                      C.MAX_PERCENTAGE // 5) * 5  # Random in steps of 10
        if group.field_maybe_none('min_report_percentage_self') is None:
            group.min_report_percentage_self = random.randint(1, C.MAX_PERCENTAGE // 5) * 5  # Random in steps of 10

            # Storing whether timeout happened in the participant's data
            player.participant.vars['worker_page_timeout'] = timeout_happened


    @staticmethod
    def vars_for_template(player: Player):
        max_percentage = C.MAX_PERCENTAGE + 1  # Max for the slider with an extra step for "none"
        slider_ticks = [1] + list(range(5, max_percentage + 1, 5))  # Create tick marks starting from 1, in steps of 5

        tick_width = 100 / len(slider_ticks)  # Calculate width percentage for each tick
        player.set_treatment_probability()

        return {
            'timeout_seconds': WorkerPage.get_timeout_seconds(player),
            'timeout_seconds_ms': WorkerPage.get_timeout_seconds(player) * 1000,  # Pass milliseconds for JavaScript
            'max_percentage': max_percentage,
            'slider_ticks': slider_ticks,  # Pass slider ticks to the template
            'tick_width': tick_width,  # Pass the tick width to the template
            'report_penalty_probabilities': C.REPORT_PENALTY_PROBABILITIES,
            'min_report_percentage_self': player.group.field_maybe_none('min_report_percentage_self') or 0,
            'min_report_percentage_other_worker': player.group.field_maybe_none('min_report_percentage_other_worker') or 0,
            'timeout_seconds': WorkerPage.get_timeout_seconds(player),  # Pass the dynamic timer value to HTML
            'timeout_happened': player.participant.vars.get('worker_page_timeout', False),
            'round_number': player.round_number,
            'total_rounds': C.NUM_ROUNDS,
            'report_penalty_probabilities': C.REPORT_PENALTY_PROBABILITIES[0],
            'treatment_probability': player.treatment_probability,
            'worker_report_reward': C.WORKER_REPORT_REWARD,
            'worker_report_penalty': C.WORKER_REPORT_PENALTY,
            'random_start_self': random.randint(1, 51),
            'random_start_other': random.randint(1, 51),
        }


class AuthorityPage(Page):
    form_model = 'group'
    form_fields = ['authority_accepted_transfer']
    template_name = 'ret/AuthorityPage.html'
    timer_text = 'Time left:'

    @staticmethod
    def get_timeout_seconds(player: Player):
        return 180 if player.round_number == 1 or player.round_number == C.SWITCH_ROUND else 90

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 3  # Only for the Authority

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        if timeout_happened:
            player.timeout_flag = True  # Handle any server-side timeout logic here
            group.authority_accepted_transfer = None
            print(f"DEBUG: Authority {player.id_in_group} timed out, default set")

    @staticmethod
    def error_message(player, values):
        pass


    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        player.set_treatment_probability()

        return {
            'treatment_probability': player.treatment_probability,
            'interfere_cost': C.INTERFERE_COST,
            'transfer_amount': C.TRANSFER_AMOUNT,
            'timeout_seconds': AuthorityPage.get_timeout_seconds(player),  # Pass timer value to HTML
        }
class ResultsWaitPage(WaitPage):
   after_all_players_arrive = set_payoffs
   title_text = " "

   body_text = "Please wait while other participants are making their decisions."


class DecisionResults(Page):
    form_model = 'group'
    timer_text = 'Time left:'

    #@staticmethod
    #def get_timeout_seconds(player: Player):
     #   return 120  # Set your desired timer duration
    @staticmethod
    def get_timeout_seconds(player: Player):
        return 40 if player.round_number == 1 or player.round_number == C.SWITCH_ROUND else 20

    def is_displayed(player: Player):
        return True
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Flag timeout status in player data
        # player.participant.vars['timeout_happened'] = timeout_happened
        # Actions if the timeout occurs (e.g., auto-submit)
        if timeout_happened:
        #  player.some_field = 0  # Or whatever action needed on timeout
        # You can leave this empty if you don't need to set any defaults.
            pass
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        player.set_treatment_probability()

        # Retrieve all players in the group
        players = group.get_players()

        # Identify the current player and the other two players
        other_players = [p for p in players if p != player]
        other_player1 = other_players[0]
        other_player2 = other_players[1]

        # Retrieve the reporting thresholds
        min_report_percentage_other_worker = group.field_maybe_none('min_report_percentage_other_worker')
        min_report_percentage_self = group.field_maybe_none('min_report_percentage_self')

        # Check if group.victim_worker_id exists and if the player is the direct victim
        victim_worker_id = group.field_maybe_none('victim_worker_id')
        is_victim = player.id_in_group == victim_worker_id if victim_worker_id is not None else False

        # Get the victim worker for display purposes (not reporting)
        manager = group.get_player_by_id(2)
        victim_participant_id = manager.participant.vars.get('paired_worker_id')
        victim_worker = None
        for p in player.subsession.get_players():
            if p.participant.id == victim_participant_id:
                victim_worker = p
                break

        players = group.get_players()
        other_players = [p for p in players if p != player]
        other_player1 = other_players[0]
        other_player2 = other_players[1]

        min_report_percentage_other_worker = group.field_maybe_none('min_report_percentage_other_worker')
        min_report_percentage_self = group.field_maybe_none('min_report_percentage_self')

        worker = next(p for p in players if p.id_in_group == 1)  # The group’s worker
        manager = next(p for p in players if p.id_in_group == 2)  # The group’s manager

        # Use the worker’s stored report status (about their own manager)
        worker_in_group = group.get_player_by_id(1)
        worker_reported = worker_in_group.worker_reported
        report_successful = worker_in_group.report_successful


        # Authority transfer details
        authority_transfer_asked = group.field_maybe_none('authority_transfer_asked')
        authority_accepted_transfer = group.field_maybe_none('authority_accepted_transfer')

        # Handle earnings display for each role
        total_earnings = player.total_earnings or 0
        worker_payoff = int(player.payoff) if player.id_in_group == 1 else 'N/A'
        manager_payoff = int(player.payoff) if player.id_in_group == 2 else 'N/A'
        authority_payoff = int(player.payoff) if player.id_in_group == 3 else 'N/A'
        paired_worker_id = player.participant.vars.get('paired_worker_id')
        worker = get_player_by_participant_id(group, paired_worker_id) if paired_worker_id else None
        worker_solved_problems = worker.num_solved if worker else 0
        worker_earnings_ecu = worker.points_earned if worker else 0

        # Use field_maybe_none() with a fallback default of 0 if the field is None
        transfer_amount = group.field_maybe_none('transfer_amount') or 0
        percentage_taken = group.field_maybe_none('percentage_taken') or 0
        wants_to_pay_transfer = group.field_maybe_none('wants_to_pay_transfer') or False


        # Report outcome
        report_outcome = (
            "There was nothing to report." if percentage_taken == 0 else
            "A successful report was made, and the manager lost his earnings." if worker_reported and report_successful else
            "An unsuccessful report was made." if worker_reported else
            "The worker did not report their manager."
        )

        # Authority outcome
        authority_outcome = (
            "There was no transfer to accept." if not wants_to_pay_transfer else
            "Accepted transfer." if authority_accepted_transfer else
            "Did not accept transfer."
        )

        return {
            'player': player,
            'total_earnings': total_earnings,
            'percentage_taken': percentage_taken,
            'transfer_amount': transfer_amount,
            'worker_reported': worker_reported,
            'report_successful': report_successful,
            'authority_accepted_transfer': authority_accepted_transfer,
            'authority_minimum_transfer': group.authority_minimum_transfer,
            'other_player1': other_player1,
            'other_player2': other_player2,
            'worker_payoff': worker_payoff,
            'manager_payoff': manager_payoff,
            'authority_payoff': authority_payoff,
            'is_victim': is_victim,
            'report_outcome': report_outcome,
            'authority_outcome': authority_outcome,
            'worker_solved_problems': worker_solved_problems,
            'worker_earnings_ecu': worker_earnings_ecu,
            'timeout_seconds': DecisionResults.get_timeout_seconds(player),  # Pass timer value to HTML
            'wants_to_pay_transfer': wants_to_pay_transfer,  # Ensure this is explicitly passe
        }
   # def vars_for_template(player: Player):
    #    group = player.group
     #   paired_worker_id = player.participant.vars.get('paired_worker_id')
      #  paired_worker = group.get_player_by_id(paired_worker_id) if paired_worker_id else None

        # Retrieve the reporting thresholds
#        min_report_percentage_other_worker = group.field_maybe_none('min_report_percentage_other_worker')
 #       min_report_percentage_self = group.field_maybe_none('min_report_percentage_self')

        # Determine if the worker is the direct victim
  #      is_victim = paired_worker == player

        # Use appropriate reporting threshold based on whether the worker is the direct victim
 #       report_threshold = min_report_percentage_self if is_victim else min_report_percentage_other_worker
  #      worker_reported = report_threshold is not None and report_threshold <= group.percentage_taken

        # Reporting success and outcome
 #       report_successful = worker_reported and random.uniform(0, 1) < C.REPORT_PENALTY_PROBABILITIES[0]
  #      report_outcome = (
   #         "The report was successful, and the manager lost his earnings."
    #        if report_successful else
     #       "The report was unsuccessful."
      #  )

  #      # Authority transfer details
   #     authority_transfer_asked = group.field_maybe_none('authority_transfer_asked')
    #    authority_accepted_transfer = group.field_maybe_none('authority_accepted_transfer')









class Results(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player: Player):
        return True

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group


        return {
            'payoff': player.payoff,
            'effort_points': player.field_maybe_none('effort_points'),

            'group_result': player.group_result,
        }

class RandomRoundWaitPage(WaitPage):
    title_text = " "
    body_text = "Please wait until the experiment continues."
    #wait_for_all_groups = True  # Ensures all groups finish before payment selection
    #after_all_players_arrive = 'set_random_round_payment'
    def after_all_players_arrive(self):
        if self.round_number == C.NUM_ROUNDS:
            self.subsession.set_random_round_payment()

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS  # Show only in the last round
class RandomRoundPayment(Page):
    timer_text = 'Time left:'
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS  # Show only in the last round

    @staticmethod
    def vars_for_template(player: Player):
        participant = player.participant
        selected_round = participant.vars.get('selected_round')
        selected_round_earnings = participant.vars.get('selected_round_earnings', 0)
        timeout_seconds = RandomRoundPayment.get_timeout_seconds(player)  # Add timeout_seconds here

        return {
            'role': player.get_role(),
            'round_number': player.round_number,
            'num_rounds': C.NUM_ROUNDS,
            'selected_round': selected_round,
            'selected_round_earnings': selected_round_earnings,
            'timeout_seconds': RandomRoundPayment.get_timeout_seconds(player),  # Pass timeout_seconds to the template

        }

    @staticmethod
    def get_timeout_seconds(player: Player):
        # Optional timeout if needed
        return 20



class WaitingFeedback(WaitPage):
    after_all_players_arrive = 'set_group_results'  # Set results after all players arrive

    title_text = " "

    body_text = "Please wait while other participants are making their decisions."

def set_group_results(group: Group):
    # Calculate RET task points for all players and store them in points_earned
    for p in group.get_players():
        if p.get_role() == "Authority":
            p.points_earned = C.ENDOWMENT  # Authority gets only salary
        else:
            p.points_earned = p.num_solved * C.BONUS_PER_SOLVED_ADDITION  # Workers and Managers get RET earnings
        print(f"DEBUG: Player {p.id_in_group}, Role: {p.get_role()}, Points Earned: {p.points_earned}")
        # No total_earnings update here; leave that to set_payoffs
        #p.total_earnings += p.points_earned
class GroupResults(Page):
    form_model = 'player'
    timer_text = 'Time left:'

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        # Gather performance and roles of all players in the group
        group_performance = [
            {
                'id': p.id_in_group,
                'role': p.get_role(),
                'num_solved': p.num_solved,
                'points_earned': p.points_earned  # Display RET earnings (with ENDOWMENT for authority)
            }
            for p in group.get_players()
        ]

        # Return a dictionary with `timeout_seconds` at the top level
        return {
            'group_performance': group_performance,
            'timeout_seconds': GroupResults.get_timeout_seconds(player),  # Ensure it’s at the top level
            'is_authority': player.id_in_group == 3,
            'salary': C.ENDOWMENT,
        }
    @staticmethod
    def get_timeout_seconds(player: Player):
        if player.round_number == 1:
            return 30  # Set a longer timeout for the first round if desired
        else:
            return 20  # Shorter timeout for other rounds

    def is_displayed(player: Player):
        return True  # Display for all players before they make decisions


    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        pass

class BeforeDecisionsWaitPage(WaitPage):
    wait_for_all_groups = True  # Ensures all players from all groups arrive

    title_text = " "

    body_text = "Please wait."

    def after_all_players_arrive(self):
        # Re-pair managers and workers each round
        self.subsession.pair_managers_with_workers()



class Baseline(Page):
    form_model = 'player'
    @staticmethod
    def is_displayed(player: Player):
        return True

class RoundResults(Page):
    form_model = 'player'
    timer_text = 'Time left:'

    @staticmethod
    def vars_for_template(player: Player):
        # Get role and round-specific earnings
        role = player.get_role()
        round_number = player.round_number
        total_earnings = player.total_earnings
        timeout_seconds = RoundResults.get_timeout_seconds(player)  # Add timeout_seconds here
        is_victim = player.participant.vars.get('paired_manager_id') is not None
        amount_lost = player.amount_lost if is_victim else 0

        return {
            'role': role,
            'total_earnings': total_earnings,
            'round_number': round_number,
            'timeout_seconds': RoundResults.get_timeout_seconds(player),  # Pass timeout_seconds to the template
            'amount_lost': amount_lost,
            'is_victim': is_victim,

        }

    @staticmethod
    def is_displayed(player: Player):
        return True  # Display for all players

    @staticmethod
    def get_timeout_seconds(player: Player):
        # Optional timeout if needed
        return 20

class YourRoleIs(Page):
    form_model = 'player'
    timer_text = 'Time left:'

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def get_timeout_seconds(player: Player):
        session = player.session
        return 20

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Automatically move to the next page if timeout occurs
        if timeout_happened:
            player.participant.vars['your_role_is_timeout'] = True  # Optional: record that timeout happened

class TreatmentChangeAnnouncement(Page):
    timer_text = 'Time left:'
    @staticmethod
    def is_displayed(player: Player):
        # Show only before Round 3, after Round 2 completes
        return player.round_number == C.SWITCH_ROUND - 1 and player.subsession.round_number == C.SWITCH_ROUND - 1

    @staticmethod
    def vars_for_template(player: Player):
        # Get the next round’s treatment_probability
        player.set_treatment_probability()  # Current round’s value (Round 2)
        next_round_probability = (
            C.ALPHA_HIGH if player.session.config.get("treatment_order", "low_to_high") == "low_to_high" else C.ALPHA_LOW
        )  # Round 3’s value after switch
        success_percentage = int(next_round_probability * 100)  # Convert to percentage
        return {
            'success_percentage': success_percentage,
            'round_number': player.round_number,
            'next_round': C.SWITCH_ROUND,
        }

    @staticmethod
    def get_timeout_seconds(player: Player):
        return 30  # Brief display, e.g., 30 seconds

class DecisionResultsWait(WaitPage):
    wait_for_all_groups = True

    after_all_players_arrive = 'set_payoffs'

    title_text = " "
    body_text = "Please wait while other participants are making their decisions."

class NextRound(WaitPage):
    after_all_players_arrive = set_payoffs

    title_text = " "
    body_text = "Please wait until the experiment continues."

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
page_sequence = [StartWaitPage, YourRoleIs, RET, WaitingFeedback, GroupResults,BeforeDecisionsWaitPage, ManagerDecisionPage, WorkerPage, AuthorityPage, ResultsWaitPage, DecisionResults, RoundResults, NextRound, TreatmentChangeAnnouncement, RandomRoundWaitPage, RandomRoundPayment ]