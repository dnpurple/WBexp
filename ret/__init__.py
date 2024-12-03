from .helpers import get_player_by_participant_id


import random
from random import choice
from otree.api import *
c = cu


doc = 'real effort task'

class C(BaseConstants):
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 3
    NAME_IN_URL = 'ret'
    NUM_ADDENDA = 3
    ADDENDUM_MAX_VALUE = 99
    MULTIPLIER = 5
    ENDOWMENT = 100
   # BASELINE_ROUND = 1
    #GROUP_ROUNDS = [i for i in range(1, NUM_ROUNDS + 1)]  # Rounds from 2 to 15
    QUIZ_FIELDS = ('q1', 'q2', 'q3', 'q4')
    QUIZ_CORRECT = ('1', '2', '3', '1')
    REPORT_PENALTY_PROBABILITIES = (0.97,)
    #TREATMENT_PROBABILITIES = (0.8,)
    OFFER_CHOICES = (0,)
    MAX_TRANSFER = 100
    MIN_TRANSFER = 0
    #TRANSFER_CHOICES = (0, 100, 10)
    TRANSFER_CHOICES = list(range(MIN_TRANSFER, MAX_TRANSFER + 1, 5))
    MAX_PERCENTAGE = 50
    MAX_PERCENTAGE_PLUS_ONE = MAX_PERCENTAGE + 1
    PERCENTAGE_CHOICES = list(range(0, MAX_PERCENTAGE + 1, 10))  # Percent choices from 0% to 50% in increments of 10
    BELIEF_ELICITATION_ROUNDS = (1, 2, 3)
    BONUS_PER_SOLVED_ADDITION = 300
    WORKER_REPORT_REWARD = 50  # For example, worker gets 50 points if report succeeds
    WORKER_REPORT_PENALTY = 20  # Worker loses 20 points if report fails
    MANAGER_REPORT_PENALTY = 100  # Manager loses 100 points if report succeeds
    INTERFERE_COST = 55
    #EXCHANGE_RATE = 55
    MAX_BELIEF_POINTS = 100  # Maximum points for a correct belief
    BELIEF_PENALTY_FACTOR = 0.2  # Penalty factor for belief scoring

    #from otree.api import models, widgets, cu
class Subsession(BaseSubsession):
    def creating_session(self):
        if self.round_number == 1:
            players = self.get_players()

            random.shuffle(players)
            group_matrix = [players[i:i + C.PLAYERS_PER_GROUP] for i in range(0, len(players), C.PLAYERS_PER_GROUP)]
            self.set_group_matrix(group_matrix)

            print(f"DEBUG: Group matrix: {self.get_group_matrix()}")

            # Call pairing function after groups are set
            self.pair_managers_with_workers()

            for player in self.get_players():
                print(
                    f"DEBUG: Player {player.id_in_group}, Participant ID: {player.participant.id}, Role: {player.get_role()}")

    def pair_managers_with_workers(self):
        players = self.get_players()
        managers = [p for p in players if p.get_role() == "Manager"]
        workers = [p for p in players if p.get_role() == "Worker"]

        # Ensure there are equal numbers of managers and workers
        if len(managers) != len(workers):
            raise ValueError("Mismatch in the number of managers and workers.")

        # Shuffle workers for random pairing
        random.shuffle(workers)
        pairs = list(zip(managers, workers))

        # Store pairings for debugging
        self.session.vars['pairings'] = [
            {'manager_id': manager.participant.id, 'worker_id': worker.participant.id}
            for manager, worker in pairs
        ]

        # Assign pairings using `participant.id`
        for manager, worker in pairs:
            manager.participant.vars['paired_worker_id'] = worker.participant.id
            worker.participant.vars['paired_manager_id'] = manager.participant.id
            print(f"DEBUG: Manager {manager.participant.id} paired with Worker {worker.participant.id}")
            print(
                f"DEBUG: Worker {worker.participant.id} has paired_manager_id: {worker.participant.vars.get('paired_manager_id')}")

            # Confirm assignments for **all players** in the group
            for player in self.get_players():
                print(f"DEBUG: Player {player.participant.id} vars: {player.participant.vars}")

        for group in self.get_groups():
            # Ensure that fields have default values when groups are formed
            group.wants_to_take = True
            group.wants_to_pay_transfer = False

            # Assign default values for each participant
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
    amount_taken = models.IntegerField(choices=C.TRANSFER_CHOICES, label='How much would you like to take from a worker')
    authority_transfer_asked = models.BooleanField(choices=[[True, 'Yes'], [False, 'No']], label='Do you want accept a transfer?', widget=widgets.RadioSelectHorizontal)

    victim_worker_id = models.IntegerField()  # Add a field to store the victim's ID
    authority_accepted_transfer = models.BooleanField(initial=False)  # <-- Add this field


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
    wants_to_pay_transfer = models.BooleanField(choices=[[True, 'Yes'], [False, 'No']], initial=False)

    percentage_taken = models.IntegerField(blank=True)  # Allow blank if not taking
    #transfer_amount = models.IntegerField(blank=True)  # Allow blank if not transferring
    transfer_amount = models.IntegerField(
        min=0,
        blank=True,  # Set to True if transfer amount is optional
        doc="Amount offered by the manager for the authority's acceptance."
    )

class Player(BasePlayer):
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
    prediction = models.IntegerField(label='What is the likelihood of interference?', max=100, min=0)
    effort_points = models.IntegerField()

    # Belief elicitation fields
    belief_manager_take = models.IntegerField(blank=True, null=True)
    belief_manager_transfer = models.IntegerField(blank=True, null=True)
    belief_manager_take_self = models.IntegerField(initial=0)
    belief_manager_transfer_self = models.IntegerField(initial=0)
    belief_manager_take_worker_2 = models.IntegerField(initial=0)
    belief_manager_transfer_worker_2 = models.IntegerField(initial=0)
    belief_manager_take_worker_3 = models.IntegerField(initial=0)
    belief_manager_transfer_worker_3 = models.IntegerField(initial=0)

    belief_authority_acceptance = models.IntegerField(blank=True, null=True)

    # Manager-specific beliefs about worker's reporting threshold
    belief_report_group = models.IntegerField(blank=True,
                                              label="Belief about reporting threshold for worker in the manager's group",
                                              min=0, max=50)
    belief_report_other = models.IntegerField(blank=True,
                                              label="Belief about reporting threshold for worker in another group",
                                              min=0, max=50)

    # Authority-specific beliefs about manager’s actions (assuming this for consistency)
    belief_take_group = models.IntegerField(blank=True,
                                            label="Belief about the take from worker in the authority's group", min=0,
                                            max=50)
    belief_transfer_group = models.IntegerField(blank=True,
                                                label="Belief about the transfer for worker in authority's group",
                                                min=1, max=101)

    belief_report_made_manager = models.IntegerField(blank=True, label='How likely do you think a report was made?',
                                                     max=100, min=0)
    belief_report_made_authority = models.IntegerField(blank=True, label='How likely do you think a report was made?',
                                                       max=100, min=0)
    belief_worker_report = models.IntegerField(
        blank=True,
        label='How likely do you think a report was made?',
        max=100,
        min=0
    )

    random_number_for_belief = models.IntegerField()
    total_earnings = models.IntegerField(initial=0)  # To track all earnings

    points_earned = models.IntegerField(initial=0)  # Earnings from the RET task
    transfer_earnings = models.IntegerField(initial=0)  # Earnings/deductions from transfers and reports
    belief_earnings = models.IntegerField(initial=0)  # Earnings from belief elicitation

    report_earnings = models.IntegerField(initial=0)  # Earnings from report/reward mechanics
    manager_earnings = models.IntegerField(initial=0)  # Manager's custom earnings
    authority_earnings = models.IntegerField(initial=0)  # Authority's custom earnings
    belief_payoff = models.IntegerField(initial=0)


    amount_lost = models.IntegerField(initial=0)
    manager_take_earnings = models.IntegerField(initial=0)

    player_role = models.StringField(initial="Unknown")  # Add role explicitly
    unique_id = models.StringField()  # A unique identifier for each player

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
    import random

    # Retrieve players by roles
    workers = [p for p in group.get_players() if p.id_in_group == 1]
    managers = [p for p in group.get_players() if p.id_in_group == 2]
    authority = group.get_player_by_id(3)

    # Check if the manager wants to take; if not, set percentage_taken to 0
    if not group.wants_to_take:
        group.percentage_taken = 0
    else:
        # Use the provided percentage taken
        group.percentage_taken = group.field_maybe_none('percentage_taken') or 0


    # Randomly select one worker as the "victim" if the manager chose to take
    victim_worker = random.choice(workers)
    worker_earnings = victim_worker.points_earned  # RET earnings from points_earned

    for manager in managers:
        if group.percentage_taken > 0:
            # Calculate amount taken based on percentage taken
            amount_taken = int((group.percentage_taken / 100) * worker_earnings)
            manager.manager_take_earnings = int(manager.points_earned + amount_taken)
            victim_worker.amount_lost = amount_taken
        else:
            # No take scenario
            manager.manager_take_earnings = manager.points_earned
            victim_worker.amount_lost = 0

    wants_to_pay_transfer = group.field_maybe_none('wants_to_pay_transfer') or False
    transfer_amount = group.field_maybe_none('transfer_amount') or 0
    authority_minimum_transfer = group.field_maybe_none('authority_minimum_transfer') or 0

    if wants_to_pay_transfer:
        # Set authority transfer status based on the minimum transfer the authority will accept
        if transfer_amount >= authority_minimum_transfer:
            group.authority_transfer_asked = True
            group.authority_accepted_transfer = True
            authority.authority_earnings = transfer_amount - C.INTERFERE_COST
        else:
            group.authority_transfer_asked = True
            group.authority_accepted_transfer = False
            authority.authority_earnings = 0
    else:
        group.authority_transfer_asked = False
        group.authority_accepted_transfer = False
        authority.authority_earnings = 0  # No transfer was offered

    # Reporting logic for each worker, based on whether they are the direct victim
    for worker in workers:
        is_direct_victim = worker == victim_worker
        report_threshold = (
            group.min_report_percentage_self if is_direct_victim else group.min_report_percentage_other_worker
        )
        worker_reported = report_threshold is not None and report_threshold <= group.percentage_taken

        # Determine if the report is successful based on transfer acceptance and penalty probabilities
        report_successful = worker_reported and random.uniform(0, 1) < (
            group.session.config['treatment_probability'] if group.authority_accepted_transfer else C.REPORT_PENALTY_PROBABILITIES[0]
        )

        if worker_reported:
            if report_successful:
                worker.report_earnings = C.WORKER_REPORT_REWARD
                manager.manager_earnings = 0  # Manager loses earnings on successful report
            else:
                worker.report_earnings = -C.WORKER_REPORT_PENALTY
        else:
            worker.report_earnings = 0

        # Calculate total earnings for each worker and manager
        worker.total_earnings = worker.points_earned + worker.report_earnings  # RET earnings + report result
        manager.total_earnings = manager.manager_take_earnings - manager.transfer_earnings  # Manager earnings (take + transfer)

    # Authority's total earnings include points from RET + any transfer (if accepted)
    authority.total_earnings = authority.points_earned + authority.authority_earnings

    # Debug prints to check payoffs (optional)
    print(f"Final Earnings - Worker {victim_worker.id_in_group}: {victim_worker.total_earnings}")
    print(f"Final Earnings - Manager {manager.id_in_group}: {manager.total_earnings}")
    print(f"Final Earnings - Authority {authority.id_in_group}: {authority.total_earnings}")
    print(f"Authority Transfer Asked: {group.authority_transfer_asked}, Accepted: {group.authority_accepted_transfer}")


#def calculate_individual_belief_payoff(belief, actual):
 #   """ Helper function to calculate payoff based on belief and actual outcome """
  #  import random
   # random_number = random.randint(0, 100)
    #if belief >= random_number:
     #   if actual:
      #      return int(cu(100))  # Full reward if belief was correct and actual event happened
       # else:
        #    return int(cu(0))  # No reward if belief was wrong
    #else:
     #   return int(cu(50) * (random_number / 100))  # Partial reward based on random number

def calculate_accuracy_payoff(accuracy: float) -> int:
    """
    Determine payoff based on accuracy thresholds:
    - Over 90% accuracy: 100 ECUs
    - Between 80% and 90% accuracy: 40 ECUs
    - Less than 80% accuracy: 0 ECUs
    """
    if accuracy > 90:
        return 100
    elif accuracy > 80:
        return 40
    else:
        return 0

def calculate_belief_payoff(player: Player):
    group = player.group
    print(f"DEBUG: paired_worker_id for Player {player.id_in_group}: {player.participant.vars.get('paired_worker_id')}")

    if player.id_in_group == 1:  # Worker role
        actual_take = group.percentage_taken if group.wants_to_take else 0
        actual_transfer = group.transfer_amount if group.wants_to_pay_transfer else 0

        # Use the correct belief field based on the paired worker
        paired_worker_id = player.participant.vars.get('paired_worker_id')
        if paired_worker_id == player.id_in_group:
            belief_take = player.belief_manager_take_self
            belief_transfer = player.belief_manager_transfer_self
        elif paired_worker_id == 2:
            belief_take = player.belief_manager_take_worker_2
            belief_transfer = player.belief_manager_transfer_worker_2
        elif paired_worker_id == 3:
            belief_take = player.belief_manager_take_worker_3
            belief_transfer = player.belief_manager_transfer_worker_3
        if paired_worker_id is None:
            print(f"WARNING: Player {player.id_in_group} has no paired_worker_id.")
            return  # Skip calculation for this player
        else:
            raise ValueError("Unexpected paired_worker_id value")

        # Calculate accuracies
        take_accuracy = 100 - abs(belief_take - actual_take)
        transfer_accuracy = 100 - abs(belief_transfer - actual_transfer)

        # Sum the earnings from each belief accuracy
        belief_earnings = sum(
            calculate_accuracy_payoff(accuracy)
            for accuracy in [take_accuracy, transfer_accuracy]
        )
    elif player.id_in_group == 2:  # Manager role
        actual_report_group = group.min_report_percentage_self
        actual_report_other = group.min_report_percentage_other_worker
        actual_authority_transfer = group.authority_minimum_transfer

        report_group_accuracy = 100 - abs(player.belief_report_group - actual_report_group)
        report_other_accuracy = 100 - abs(player.belief_report_other - actual_report_other)
        authority_accuracy = 100 - abs(player.belief_authority_acceptance - actual_authority_transfer)

        belief_earnings = sum(
            calculate_accuracy_payoff(accuracy)
            for accuracy in [report_group_accuracy, report_other_accuracy, authority_accuracy]
        )

    elif player.id_in_group == 3:  # Authority role
        actual_take = group.percentage_taken if group.wants_to_take else 0
        actual_transfer = group.transfer_amount if group.wants_to_pay_transfer else 0
        actual_report_group = group.min_report_percentage_self
        actual_report_other = group.min_report_percentage_other_worker

        #take_accuracy = 100 - abs(player.belief_take_group - actual_take)
        #transfer_accuracy = 100 - abs(player.belief_transfer_group - actual_transfer)
        report_group_accuracy = 100 - abs(player.belief_report_group - actual_report_group)
        report_other_accuracy = 100 - abs(player.belief_report_other - actual_report_other)

        belief_earnings = sum(
            calculate_accuracy_payoff(accuracy)
            for accuracy in [
                #take_accuracy,
                #transfer_accuracy,
                report_group_accuracy,
                report_other_accuracy,
            ]
        )

    player.belief_earnings = belief_earnings
    player.total_earnings += belief_earnings


#def calculate_belief_payoff(player: Player):
 #  # group = player.group
#    import random
 #   player.random_number_for_belief = random.randint(0, 100)

    # Worker beliefs
   # if player.id_in_group == 1:
    #    belief_authority_transfer = player.field_maybe_none('belief_authority_acceptance') or 0
     #   belief_manager_transfer = player.field_maybe_none('belief_manager_transfer') or 0
      #  belief_manager_take = player.field_maybe_none('belief_manager_take') or 0

#        actual_authority_transfer = group.field_maybe_none('authority_minimum_transfer') != 0
#        actual_manager_transfer = group.field_maybe_none(
 #           'transfer_amount') or 0 != 0  # Updated to use field_maybe_none()
  #      actual_manager_take = group.field_maybe_none('percentage_taken') or 0 != 0  # Updated to use field_maybe_none()

        # Ensure belief_payoff is initialized
 #       if player.belief_payoff is None:
  #          player.belief_payoff = 0  # Initialize if not already set

        # Calculate belief payoffs for each question
#        player.belief_payoff += int(calculate_individual_belief_payoff(belief_authority_transfer, actual_authority_transfer))
 #       player.belief_payoff += int(calculate_individual_belief_payoff(belief_manager_transfer, actual_manager_transfer))
  #      player.belief_payoff += int(calculate_individual_belief_payoff(belief_manager_take, actual_manager_take))

    # Manager beliefs
#    elif player.id_in_group == 2:
 #       belief_authority_transfer = player.field_maybe_none('belief_authority_acceptance') or 0
  #      belief_worker_report = player.field_maybe_none('belief_worker_report') or 0

   #     actual_authority_transfer = group.field_maybe_none('authority_minimum_transfer') != 0
    #    actual_worker_report = group.field_maybe_none('min_report_percentage_self') != -1

 #       if player.belief_payoff is None:
  #          player.belief_payoff = 0  # Initialize if not already set

   #     player.belief_payoff += int(calculate_individual_belief_payoff(belief_authority_transfer, actual_authority_transfer))
    #    player.belief_payoff += int(calculate_individual_belief_payoff(belief_worker_report, actual_worker_report))

    # Authority beliefs
#    elif player.id_in_group == 3:
 #       belief_worker_report = player.field_maybe_none('belief_worker_report') or 0
  #      actual_worker_report = group.field_maybe_none('min_report_percentage_self') != -1

   #     if player.belief_payoff is None:
    #        player.belief_payoff = 0  # Initialize if not already set

     #   player.belief_payoff += calculate_individual_belief_payoff(belief_worker_report, actual_worker_report)

        # Update total earnings and belief earnings
#    player.belief_earnings = player.belief_payoff  # Store belief earnings
 #   player.total_earnings += player.belief_payoff  # Add belief earnings to total earnings

def set_payoffs_and_calculate_beliefs(group: Group):
    # Call the existing set_payoffs function to compute payoffs for the group
    set_payoffs(group)

    # Loop over each player in the group and calculate their belief payoffs
    for player in group.get_players():
        if player.round_number in C.BELIEF_ELICITATION_ROUNDS:
            calculate_belief_payoff(player)


class Instructions(Page):
    form_model = 'player'
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1
class Quiz(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2', 'q3', 'q4']
    timer_text = 'Time left:'
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1
    @staticmethod
    def vars_for_template(player: Player):
        payoff_example = round(C.ENDOWMENT- 20 + 300 * C.MULTIPLIER/C.PLAYERS_PER_GROUP, 2)
        return dict(
            payoff_example_tag=payoff_example
        )

    @staticmethod
    def get_timeout_seconds(player: Player):
        session = player.session
        return 6  # player.session.config['quiz_timeout_seconds']
   # @staticmethod
    #def before_next_page(player: Player, timeout_happened):
     #   participant = player.participant
        #participant.dropout = timeout_happened
    #@staticmethod
    #def error_message(player: Player, values):
     #   errors = dict()
      #  session = player.session
       # has_error = any(v != session.vars['quiz'][k] for k, v in values.items())
        #if has_error:
         #   return "At least one answer is incorrect."

        #session = player.session
        #for k, v in values.items():
         #   if v != session.vars['quiz'][k]:
          #      errors[k] = f'Wrong answer.'

        # MODULE - 5 - Exercise 9 (Quiz - Challenge)
        # LONG WAY:
       # if k == 'q1':
             # player.q1_num_errors += 1
       # elif k == 'q2':
           # player.q2_num_errors += 1
       # elif k == 'q3':
           #  player.q3_num_errors += 1
       # elif k == 'q4':
           # player.q4_num_errors += 1

        # SHORT WAY:
        # setattr(player, f'{k}_num_errors', getattr(player, f'{k}_num_errors') + 1)

        # MODULE - 5 - Exercise 8 (Quiz - Challenge)
      #  return errors

   # @staticmethod
   # def app_after_this_page(player: Player, upcoming_apps):
    #    participant = player.participant
     #   if participant.dropout:
      #      return upcoming_apps[-1]
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
        return 900  # player.session.config['quiz_timeout_seconds']

class BeliefElicitationInstructions(Page):
    form_model = 'player'
    timer_text = 'Time left:'

    @staticmethod
    def vars_for_template(player: Player):

        # Return a dictionary with `timeout_seconds` at the top level
        return {
            'timeout_seconds': BeliefElicitationInstructions.get_timeout_seconds(player)  # Ensure it’s at the top level
        }

    @staticmethod
    def get_timeout_seconds(player: Player):
        if player.round_number == C.BELIEF_ELICITATION_ROUNDS[0]:
            return 120  # Shorter timeout for other rounds
        else:
            return 60

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number in C.BELIEF_ELICITATION_ROUNDS

    # Show this page only in the first round of BELIEF_ELICITATION_ROUNDS
    #@staticmethod
    #def is_displayed(player: Player):
     #   return player.round_number == C.BELIEF_ELICITATION_ROUNDS[0]




class BeliefElicitationPageWorkerA(Page):
    form_model = 'player'
    form_fields = [
        'belief_manager_take_self',
        'belief_manager_transfer_self',
        'belief_manager_take_worker_2',
        'belief_manager_transfer_worker_2',
        'belief_manager_take_worker_3',
        'belief_manager_transfer_worker_3',

    ]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number in C.BELIEF_ELICITATION_ROUNDS and player.id_in_group == 1
        return player.get_role() in ["Manager", "Worker"]  # Exclude Authorities

    #@staticmethod
    ##def before_next_page(player, timeout_happened):
     #   if timeout_happened:
      #      player.timeout_flag = True  # Handle any server-side timeout logic here

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        all_workers = [
            p for p in player.subsession.get_players() if p.get_role() == "Worker"
        ]

        # Current worker (you)
        current_worker = player

        # Workers from other groups (excluding the current worker)
        other_workers = [w for w in all_workers if w != current_worker]

        # Prepare the data for the table
        workers_display_data = [
            {
                'label': "You" if worker == current_worker else f"Worker {i + 1}",
                'earnings': worker.points_earned or 0,
                'belief_take_field': f'belief_manager_take_worker_{i + 1}',
                'belief_transfer_field': f'belief_manager_transfer_worker_{i + 1}',
            }
            for i, worker in enumerate(other_workers, start=1)
        ]

        workers_display_data.insert(0, {
            'label': "You",
            'earnings': current_worker.points_earned or 0,
            'belief_take_field': 'belief_manager_take_self',
            'belief_transfer_field': 'belief_manager_transfer_self',
        })


        return {
            'workers_data': workers_display_data,
            'authority_minimum_transfer': group.field_maybe_none('authority_minimum_transfer'),
            'transfer_amount': group.field_maybe_none('transfer_amount'),
            'percentage_taken': group.field_maybe_none('percentage_taken'),
        }

    #@staticmethod
    #def get_timeout_seconds(player: Player):
     #   return 300

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        paired_worker_id = player.participant.vars.get('paired_worker_id')

        if not paired_worker_id:
            print(f"WARNING: Paired worker not found for Player {player.participant.id}")
            return

        # Get the matched worker using the paired_worker_id
        matched_worker = get_player_by_participant_id(group, paired_worker_id)

        if not matched_worker:
            print(f"ERROR: Matched worker could not be resolved for Player {player.participant.id}")
            return

        # Retrieve the player's guesses for all workers
        guesses = {
            'self': player.belief_manager_take_self,
            'transfer_self': player.belief_manager_transfer_self,
            'worker_2': player.belief_manager_take_worker_2,
            'transfer_worker_2': player.belief_manager_transfer_worker_2,
            'worker_3': player.belief_manager_take_worker_3,
            'transfer_worker_3': player.belief_manager_transfer_worker_3,
        }

        # Match the guesses with the corresponding worker
        if matched_worker.id_in_group == 1:
            belief_take = guesses['self']
            belief_transfer = guesses['transfer_self']
        elif matched_worker.id_in_group == 2:
            belief_take = guesses['worker_2']
            belief_transfer = guesses['transfer_worker_2']
        elif matched_worker.id_in_group == 3:
            belief_take = guesses['worker_3']
            belief_transfer = guesses['transfer_worker_3']
        else:
            print(f"ERROR: Unexpected matched worker ID: {matched_worker.id_in_group}")
            return

        # Use actual manager's actions to calculate accuracy
        actual_take = group.percentage_taken if group.wants_to_take else 0
        actual_transfer = group.transfer_amount if group.wants_to_pay_transfer else 0

        # Calculate accuracies
        take_accuracy = 100 - abs(belief_take - actual_take)
        transfer_accuracy = 100 - abs(belief_transfer - actual_transfer)

        # Calculate payoff based on belief accuracy
        player.belief_earnings = sum(
            calculate_accuracy_payoff(accuracy)
            for accuracy in [take_accuracy, transfer_accuracy]
        )

        # Debugging output
        print(f"DEBUG: Player {player.participant.id} belief earnings: {player.belief_earnings}")

        #paired_worker_id = player.participant.vars.get('paired_worker_id')
 #       if paired_worker_id == player.participant.id:
  #          player.belief_manager_take = player.field_maybe_none('belief_manager_take_self') or 0
   #         player.belief_manager_transfer = player.field_maybe_none('belief_manager_transfer_self') or 0
    #    elif paired_worker_id == 2:
     #       player.belief_manager_take = player.field_maybe_none('belief_manager_take_worker_2') or 0
      #      player.belief_manager_transfer = player.field_maybe_none('belief_manager_transfer_worker_2') or 0
       # elif paired_worker_id == 3:
        #    player.belief_manager_take = player.field_maybe_none('belief_manager_take_worker_3') or 0
         #   player.belief_manager_transfer = player.field_maybe_none('belief_manager_transfer_worker_3') or 0
#        else:
 #           player.belief_manager_take = 0
  #          player.belief_manager_transfer = 0

class BeliefElicitationPageWorkerB(Page):
    form_model = 'player'
    form_fields = ['belief_authority_acceptance', 'belief_manager_transfer', 'belief_manager_take']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number in C.BELIEF_ELICITATION_ROUNDS and player.id_in_group == 1
        return player.get_role() in ["Manager", "Worker"]  # Exclude Authorities

    #@staticmethod
    ##def before_next_page(player, timeout_happened):
     #   if timeout_happened:
      #      player.timeout_flag = True  # Handle any server-side timeout logic here

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        return {
            'max_percentage_plus_one': C.MAX_PERCENTAGE_PLUS_ONE,
            'authority_minimum_transfer': group.field_maybe_none('authority_minimum_transfer'),
            'transfer_amount': group.field_maybe_none('transfer_amount'),
            'percentage_taken': group.field_maybe_none('percentage_taken'),
            #'timeout_seconds': BeliefElicitationPageWorker.get_timeout_seconds(player),

        }

    #@staticmethod
    #def get_timeout_seconds(player: Player):
     #   return 300

    @staticmethod
    def before_next_page(player, timeout_happened):
        # Handle the `belief_authority_acceptance` field
        if player.field_maybe_none('belief_authority_acceptance') == C.MAX_PERCENTAGE_PLUS_ONE:
            player.belief_authority_acceptance = 0
        else:
            player.belief_authority_acceptance = player.field_maybe_none('belief_authority_acceptance') or 0


class BeliefElicitationPageManagerA(Page):
    form_model = 'player'
    form_fields = ['belief_authority_acceptance', 'belief_worker_report', 'belief_report_group', 'belief_report_other']
#i dont need those last 2 form fields


  #  @staticmethod
  #  def before_next_page(player, timeout_happened):
   #     if timeout_happened:
    #        player.timeout_flag = True  # Handle any server-side timeout logic here

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number in C.BELIEF_ELICITATION_ROUNDS and player.id_in_group == 2

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group  # Use player directly since this is a static method



        # Get all workers' data relevant to the belief task
        workers = group.get_players()  # Adjust this to filter only workers if needed
        return {
            'workers': [{'id': worker.id_in_group, 'earnings': worker.points_earned} for worker in workers if
                        worker.role == 'worker'],
            'max_percentage_plus_one':  C.MAX_PERCENTAGE_PLUS_ONE,
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Handle the `belief_report_group` field
        if player.field_maybe_none('belief_report_group') == C.MAX_PERCENTAGE_PLUS_ONE:
            player.belief_report_group = 0
        else:
            player.belief_report_group = player.field_maybe_none('belief_report_group') or 0

        # Handle the `belief_report_other` field
        if player.field_maybe_none('belief_report_other') == C.MAX_PERCENTAGE_PLUS_ONE:
            player.belief_report_other = 0
        else:
            player.belief_report_other = player.field_maybe_none('belief_report_other') or 0



    #@staticmethod
    #def get_timeout_seconds(player: Player):
     #   return 300  # Adjust to the desired timeout in seconds

class BeliefElicitationPageManagerB(Page):
    form_model = 'player'
    form_fields = ['belief_authority_acceptance', 'belief_worker_report']

  #  @staticmethod
  #  def before_next_page(player, timeout_happened):
   #     if timeout_happened:
    #        player.timeout_flag = True  # Handle any server-side timeout logic here

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number in C.BELIEF_ELICITATION_ROUNDS and player.id_in_group == 2

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group  # Use player directly since this is a static method



        # Get all workers' data relevant to the belief task
        workers = group.get_players()  # Adjust this to filter only workers if needed
        return {
            'workers': [{'id': worker.id_in_group, 'earnings': worker.points_earned} for worker in workers if
                        worker.role == 'worker'],
            #'max_percentage_plus_one': max_percentage_plus_one,
            'max_percentage_plus_one': C.MAX_PERCENTAGE_PLUS_ONE,  # Assuming C.MAX_PERCENTAGE is defined in your settings
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Handle the `belief_authority_acceptance` field
        if player.field_maybe_none('belief_authority_acceptance') == C.MAX_PERCENTAGE_PLUS_ONE:
            player.belief_authority_acceptance = 0
        else:
            player.belief_authority_acceptance = player.field_maybe_none('belief_authority_acceptance') or 0

    #@staticmethod
    #def get_timeout_seconds(player: Player):
     #   return 300  # Adjust to the desired timeout in seconds


class BeliefElicitationPageAuthority(Page):
    form_model = 'player'
    form_fields = ['belief_take_group', 'belief_transfer_group', 'belief_report_group', 'belief_report_other']

   # @staticmethod
    #def before_next_page(player, timeout_happened):
     #   if timeout_happened:
      #      player.timeout_flag = True  # Handle any server-side timeout logic here

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number in C.BELIEF_ELICITATION_ROUNDS and player.id_in_group == 3
        return player.get_role() in ["Manager", "Worker"]  # Exclude Authorities

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        workers = [
            {'id': worker.participant.id, 'earnings': worker.points_earned}
            for worker in group.get_players() if worker.get_role() == "Worker"
        ]
        return {
            'workers': workers,  # All workers' data

            'max_percentage_plus_one': C.MAX_PERCENTAGE_PLUS_ONE,
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Handle the `belief_report_group` field
        if player.field_maybe_none('belief_report_group') == C.MAX_PERCENTAGE_PLUS_ONE:
            player.belief_report_group = 0
        else:
            player.belief_report_group = player.field_maybe_none('belief_report_group') or 0

        # Handle the `belief_report_other` field
        if player.field_maybe_none('belief_report_other') == C.MAX_PERCENTAGE_PLUS_ONE:
            player.belief_report_other = 0
        else:
            player.belief_report_other = player.field_maybe_none('belief_report_other') or 0

    #@staticmethod
    #def get_timeout_seconds(player: Player):
     #   return 300  # Adjust to the desired timeout in seconds

class ManagerDecisionPage(Page):
    form_model = 'group'
    form_fields = ['wants_to_take', 'percentage_taken', 'wants_to_pay_transfer', 'transfer_amount']

    @staticmethod
    def error_message(player, values):
        errors = {}

        # Check if the player selected "Yes" for `wants_to_take` and provided `percentage_taken`
        if values['wants_to_take'] == 'Yes' and (
                values['percentage_taken'] is None or not (1 <= values['percentage_taken'] <= 50)):
            errors['percentage_taken'] = "Please enter a percentage between 1 and 50."

        # Check if the player selected "Yes" for `wants_to_pay_transfer` and provided `transfer_amount`
        if values['wants_to_pay_transfer'] == 'Yes' and (
                values['transfer_amount'] is None or values['transfer_amount'] < 1):
            errors[
                'transfer_amount'] = f"Please specify a transfer amount of at least {player.group.interfere_cost} ECUs."

        return errors if errors else None

    @staticmethod
    def get_timeout_seconds(player: Player):
        if player.round_number == 1:
            return 900  # Longer timer for the first round
        else:
            return 800  # Shorter timer for other rounds

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        # Retrieve the paired worker for this manager
        paired_worker_id = player.participant.vars.get('paired_worker_id')
        worker = get_player_by_participant_id(group, paired_worker_id) if paired_worker_id else None
        timeout_seconds = ManagerDecisionPage.get_timeout_seconds(player)

        return {
            'worker_id': paired_worker_id,
            'worker_solved_problems': worker.num_solved if worker else 0,  # Fallback if worker is None
            'worker_points_earned': worker.points_earned if worker else 0,  # Fallback if worker is None
            'percentage_choices': C.PERCENTAGE_CHOICES,
            'report_penalty_probabilities': C.REPORT_PENALTY_PROBABILITIES[0],
            'treatment_probabilities': player.session.config['treatment_probability'],
            'interfere_cost': C.INTERFERE_COST,
            'timeout_seconds': timeout_seconds,
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        paired_worker_id = player.participant.vars.get('paired_worker_id')
        paired_worker = get_player_by_participant_id(group, paired_worker_id) if paired_worker_id else None

        # Handle timeout scenario
        if timeout_happened:
            player.timeout_flag = True

        # Reset transfer_amount if the manager chooses not to pay a transfer
        if group.wants_to_pay_transfer == 'No':
            group.transfer_amount = 0

        # Reset percentage_taken if the manager chooses not to take from the worker
        if group.wants_to_take == 'No':
            group.percentage_taken = 0

        # Safely calculate `amount_taken` only if `percentage_taken` is a valid number and greater than 0
        percentage_taken = group.field_maybe_none('percentage_taken') or 0
        if paired_worker and percentage_taken > 0:
            amount_taken = int((percentage_taken / 100) * paired_worker.points_earned)
            player.manager_take_earnings = player.points_earned + amount_taken
            paired_worker.amount_lost = amount_taken
        else:
            # Default values if no amount is taken
            player.manager_take_earnings = player.points_earned
            if paired_worker:
                paired_worker.amount_lost = 0

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

    # Define timeout as a class variable, and use it directly in `vars_for_template`
   # timeout_seconds = 120  # Adjust this time limit as needed

    def get_timeout_seconds(player: Player):
        # Setting different timers based on the round or conditions
        if player.round_number == 1:
            return 30  # Longer timer for the first round
        else:
            return 800  # Shorter timer for other rounds

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
            'treatment_probabilities': player.session.config['treatment_probability'],
            'worker_report_reward': C.WORKER_REPORT_REWARD,
            'worker_report_penalty': C.WORKER_REPORT_PENALTY,
            'random_start_self': random.randint(1, 51),
            'random_start_other': random.randint(1, 51),
        }


class AuthorityPage(Page):
    form_model = 'group'
    form_fields = ['authority_minimum_transfer']
    template_name = 'ret/AuthorityPage.html'

    @staticmethod
    def get_timeout_seconds(player: Player):
        if player.round_number == 1:
            return 60  # Longer timer for the first round
        else:
            return 800  # Shorter timer for other rounds

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 3  # Only for the Authority

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        if timeout_happened:
            player.timeout_flag = True  # Handle any server-side timeout logic here

        # Ensure authority_minimum_transfer is valid
        if group.authority_minimum_transfer == C.MAX_TRANSFER + 1:
            group.authority_minimum_transfer = -1  # A specific value indicating "reject all"

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        max_transfer = C.MAX_TRANSFER + 1  # Pass max transfer as a variable

        # Check if authority_minimum_transfer has a label, set it if possible
        authority_minimum_transfer_label = group.field_maybe_none('authority_minimum_transfer') or "No minimum transfer set"
        slider_ticks = list(range(0, max_transfer + 1, 10))

        return {
            'max_transfer': max_transfer,
            'authority_minimum_transfer_label': authority_minimum_transfer_label,
            'interfere_cost': C.INTERFERE_COST,
            'timeout_seconds': AuthorityPage.get_timeout_seconds(player),  # Pass timer value to HTML
            'slider_ticks': slider_ticks,
        }
class ResultsWaitPage(WaitPage):
   after_all_players_arrive = set_payoffs_and_calculate_beliefs
   title_text = " "

   body_text = "Please wait while other participants are making their decisions."

class Feedback(Page):
    form_model = 'player'
class DecisionResults(Page):
    form_model = 'group'
    timer_text = 'Time left:'

    #@staticmethod
    #def get_timeout_seconds(player: Player):
     #   return 120  # Set your desired timer duration
    @staticmethod
    def get_timeout_seconds(player: Player):
        if player.round_number == 1:
            return 600  # Set a longer timeout for the first round if desired
        else:
            return 300  # Shorter timeout for other rounds

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

        # Use appropriate reporting threshold based on whether the worker is the direct victim
        report_threshold = min_report_percentage_self if is_victim else min_report_percentage_other_worker
        worker_reported = report_threshold is not None and report_threshold <= group.percentage_taken

        # Reporting success and outcome
        report_successful = worker_reported and random.uniform(0, 1) < C.REPORT_PENALTY_PROBABILITIES[0]
        report_outcome = (
            "The report was successful, and the manager lost his earnings."
            if report_successful else
            "The report was unsuccessful."
        )

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
            'worker_solved_problems': worker_solved_problems,
            'worker_earnings_ecu': worker_earnings_ecu,
            'timeout_seconds': DecisionResults.get_timeout_seconds(player)  # Pass timer value to HTML

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
        belief_payoff = player.payoff  # Already includes the belief payoff

        return {
            'payoff': player.payoff,
            'effort_points': player.field_maybe_none('effort_points'),
            'belief_payoff': belief_payoff,
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
        return 600



class WaitingFeedback(WaitPage):
    after_all_players_arrive = 'set_group_results'  # Set results after all players arrive

    title_text = " "

    body_text = "Please wait while other participants are making their decisions."

def set_group_results(group: Group):
    # Calculate RET task points for all players and store them in points_earned
    for p in group.get_players():
        p.points_earned = p.num_solved * C.BONUS_PER_SOLVED_ADDITION  # Store RET task earnings
        #p.group_result = p.points_earned  # Keep this if you still need group_result for other purposes

        #if p.get_role() == "Authority":
            # Add base salary (ENDOWMENT) for the authority
         #   p.points_earned += C.ENDOWMENT
        # Optionally, update total earnings to include the RET task points
        p.total_earnings += p.points_earned
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
                #'points_earned': p.num_solved * C.BONUS_PER_SOLVED_ADDITION
            }
            for p in group.get_players()
        ]

        # Return a dictionary with `timeout_seconds` at the top level
        return {
            'group_performance': group_performance,
            'timeout_seconds': GroupResults.get_timeout_seconds(player)  # Ensure it’s at the top level
        }
    @staticmethod
    def get_timeout_seconds(player: Player):
        if player.round_number == 1:
            return 600  # Set a longer timeout for the first round if desired
        else:
            return 300  # Shorter timeout for other rounds

    def is_displayed(player: Player):
        return True  # Display for all players before they make decisions


    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Optionally, ensure that any fields needed for the decision phase are set up here
        pass

class BeforeDecisionsWaitPage(WaitPage):
    wait_for_all_groups = True  # Ensures all players from all groups arrive

    title_text = " "

    body_text = "Please wait."

    def after_all_players_arrive(self):
        # Call the pairing function to reassign pairings for each round
        self.subsession.pair_managers_with_workers()
        # Logic to execute once all players have arrived
        # For example, you could set variables or assign pairings here



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

        return {
            'role': role,
            'total_earnings': total_earnings,
            'round_number': round_number,
            'timeout_seconds': RoundResults.get_timeout_seconds(player),  # Pass timeout_seconds to the template

        }

    @staticmethod
    def is_displayed(player: Player):
        return True  # Display for all players

    @staticmethod
    def get_timeout_seconds(player: Player):
        # Optional timeout if needed
        return 600

class YourRoleIs(Page):
    form_model = 'player'
    timer_text = 'Time left:'

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def get_timeout_seconds(player: Player):
        session = player.session
        return 900

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Automatically move to the next page if timeout occurs
        if timeout_happened:
            player.participant.vars['your_role_is_timeout'] = True  # Optional: record that timeout happened

class DecisionResultsWait(WaitPage):
    wait_for_all_groups = True

    after_all_players_arrive = 'set_payoffs'

    title_text = " "
    body_text = "Please wait while other participants are making their decisions."

class NextRound(WaitPage):
    after_all_players_arrive = set_payoffs_and_calculate_beliefs

    title_text = " "
    body_text = "Please wait until the experiment continues."
page_sequence = [YourRoleIs, RET, WaitingFeedback, GroupResults,BeforeDecisionsWaitPage, ManagerDecisionPage, WorkerPage, AuthorityPage, BeliefElicitationInstructions, BeliefElicitationPageWorkerA, BeliefElicitationPageWorkerB, BeliefElicitationPageManagerA, BeliefElicitationPageManagerB, BeliefElicitationPageAuthority, ResultsWaitPage, DecisionResults, RoundResults, NextRound, RandomRoundWaitPage, RandomRoundPayment ]