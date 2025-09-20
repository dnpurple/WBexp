from .helpers import get_player_by_participant_id


import random
from random import choice
from otree.api import *
c = cu


doc = 'real effort task'

class C(BaseConstants):
    NAME_IN_URL = 'wb_part_b'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 20
    #NAME_IN_URL = 'ret'
    NUM_ADDENDA = 3
    ADDENDUM_MAX_VALUE = 99
    MULTIPLIER = 5
    ENDOWMENT = 500
   # BASELINE_ROUND = 1
    #GROUP_ROUNDS = [i for i in range(1, NUM_ROUNDS + 1)]  # Rounds from 2 to 15
    QUIZ_FIELDS = ('q1', 'q2', 'q3', 'q4')
    QUIZ_CORRECT = ('1', '2', '3', '1')
    REPORT_PENALTY_PROBABILITIES = (0.97,)
    PENALTY_PERCENTAGE = 97
    #TREATMENT_PROBABILITIES = (0.8,)
    #OFFER_CHOICES = (0,)
    MAX_PERCENTAGE = 50
    MAX_PERCENTAGE_PLUS_ONE = MAX_PERCENTAGE + 1
    PERCENTAGE_CHOICES = list(range(0, MAX_PERCENTAGE + 1, 10))  # Percent choices from 0% to 50% in increments of 10

    BONUS_PER_SOLVED_ADDITION = 100
    WORKER_REPORT_REWARD = 200  # For example, worker gets 50 points if report succeeds
    WORKER_REPORT_PENALTY = 100  # Worker loses 20 points if report fails
    #MANAGER_REPORT_PENALTY = 100  # Manager loses 100 points if report succeeds
    INTERFERE_COST = 5
    TRANSFER_AMOUNT = 60
    ALPHA_LOW = 0.7  # Low interference (less corruption)
    ALPHA_HIGH = 0.3  # High interference (more corruption)
    SWITCH_ROUND = 10  # The round at which the treatment changes


class Subsession(BaseSubsession):
    def creating_session(self):
        # set treatment each round
        for p in self.get_players():
            p.set_treatment_probability()
    
        if self.round_number == 1:
            # build the round-1 groups and set round-1 fields
            self.initialize_group_structure()
            # persist the internal codes into participant.vars so we can copy them every round
            self._assign_internal_codes_round1()
    
        # copy persisted codes into THIS round's Player rows (for export),
        # but do NOT blank out if we don't have values yet
        self._copy_internal_codes_every_round()


    def initialize_group_structure(self):
        if self.round_number == 1:
            players = self.get_players()

            random.shuffle(players)
            group_matrix = [players[i:i + C.PLAYERS_PER_GROUP] for i in range(0, len(players), C.PLAYERS_PER_GROUP)]
            self.set_group_matrix(group_matrix)


            # NEW: Set internal codes for each group after matrix is created
            for group in self.get_groups():
                group_players = group.get_players()
                # Sort by id_in_group to ensure consistent order: Worker(1), Manager(2), Authority(3)
                sorted_players = sorted(group_players, key=lambda p: p.id_in_group)
                
                worker = next(p for p in sorted_players if p.id_in_group == 1)
                manager = next(p for p in sorted_players if p.id_in_group == 2)
                authority = next(p for p in sorted_players if p.id_in_group == 3)
                
                # Set internal codes for all players in the group
                worker.internal_manager_code = manager.participant.code
                worker.internal_worker_code = worker.participant.code  # Self-reference
                manager.internal_worker_code = worker.participant.code
                manager.internal_manager_code = manager.participant.code  # Self-reference
                authority.internal_worker_code = worker.participant.code
                authority.internal_manager_code = manager.participant.code
                
                print(f"Group {group.id}: Worker={worker.participant.code}, Manager={manager.participant.code}")





         #   for player in self.get_players():
          #      print(
           #         f"DEBUG: Player {player.id_in_group}, Participant ID: {player.participant.id}, Role: {player.get_role()}")




    #def pair_managers_with_workers(cls, subsession):
    def pair_managers_with_workers(self):
        players = self.get_players()
        managers = [p for p in players if p.get_role() == 'Manager']
        workers  = [p for p in players if p.get_role() == 'Worker']
    
        if len(managers) != len(workers):
            raise ValueError("Mismatch in number of managers and workers!")
    
        random.shuffle(workers)
        pairs = zip(managers, workers)
    
        # Clear previous pairings for everyone
        for p in players:
            p.participant.vars.pop('paired_worker_id', None)
            p.participant.vars.pop('paired_manager_id', None)
            p.pair_id = ''
            p.external_worker_code = ''
            p.external_manager_code = ''
            p.in_group_match = False
    
        # Make new pairs
        for manager, worker in pairs:
            # Save link both ways
            manager.participant.vars['paired_worker_id'] = worker.participant.id
            worker.participant.vars['paired_manager_id'] = manager.participant.id
    
            # Group bookkeeping you already rely on elsewhere
            g = manager.group
            g.victim_worker_id = worker.participant.id
            g.manager_id = manager.participant.id
    
            # Stable pair_id built from the 2 participant codes (same pair => same id across rounds)
            sorted_codes = sorted([manager.participant.code, worker.participant.code])
            pair_id_str = '-'.join(sorted_codes)
            manager.pair_id = pair_id_str
            worker.pair_id = pair_id_str
    
            # Round-specific “external” partner codes
            manager.external_worker_code = worker.participant.code
            worker.external_manager_code = manager.participant.code
    
            # **Robust** in-group flag: are these 2 people in the same fixed oTree group this round?
            same_group = (manager.group == worker.group)
            manager.in_group_match = same_group
            worker.in_group_match = same_group
    
            print(f"Pair: Manager {manager.participant.code}, Worker {worker.participant.code}, "
                  f"pair_id={pair_id_str}, in_group={same_group}")
    
        # Reset defaults clearly for the new round (no stale theft/report state)
        for g in self.get_groups():
            g.wants_to_take = False
            g.wants_to_pay_transfer = False
            g.percentage_taken = 0
            g.transfer_amount = 0
            g.authority_accepted_transfer = None
            g.bribe_offered_and_accepted = False
            for pl in g.get_players():
                part = pl.participant
                part.vars['selected_round'] = None
                part.vars['selected_round_earnings'] = 0
    


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

    def _assign_internal_codes_round1(self):
        """
        Called only in round 1 after the group matrix is set.
        Saves internal codes both on this round's Player rows and in participant.vars
        so we can copy them to every subsequent round.
        """
        for g in self.get_groups():
            # Roles by id_in_group: 1=Worker, 2=Manager, 3=Authority
            w = g.get_player_by_id(1)
            m = g.get_player_by_id(2)
    
            w_code = w.participant.code
            m_code = m.participant.code
    
            for p in g.get_players():
                # Persist for all rounds
                p.participant.vars['internal_worker_code'] = w_code
                p.participant.vars['internal_manager_code'] = m_code
                # Write into this round's Player row (will show up in export for round 1)
                p.internal_worker_code = w_code
                p.internal_manager_code = m_code


    
    def _copy_internal_codes_every_round(self):
        """
        Copy internal codes from participant.vars onto this round's Player rows,
        but don't overwrite with empty strings.
        """
        for p in self.get_players():
            iw = p.participant.vars.get('internal_worker_code')
            if iw:
                p.internal_worker_code = iw
            im = p.participant.vars.get('internal_manager_code')
            if im:
                p.internal_manager_code = im
            # keep your stable per-participant id if useful in analysis
            p.unique_id = p.participant.code




class Group(BaseGroup):
    #offer_accepted = models.BooleanField()
    #amount_offered = models.IntegerField(choices=C.OFFER_CHOICES)
   # authority_transfer_asked = models.BooleanField(choices=[[True, 'Yes'], [False, 'No']], label='Do you want accept a transfer?', widget=widgets.RadioSelectHorizontal)

    victim_worker_id = models.IntegerField()  # Add a field to store the victim's ID
    manager_id = models.IntegerField()
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

    bribe_offered_and_accepted = models.BooleanField(initial=False, doc="1 iff manager offered a transfer AND authority accepted it" )


    percentage_taken = models.IntegerField(blank=True)  # Allow blank if not taking
    transfer_amount = models.IntegerField(blank=True)  # Allow blank if not transferring
    #transfer_amount = models.IntegerField(
     #   min=0,
      #  blank=True,  # Set to True if transfer amount is optional
       # doc="Amount offered by the manager for the authority's acceptance."
    #)


class Player(BasePlayer):
    treatment_probability = models.FloatField()
    timeout_flag = models.BooleanField(initial=False)
    #group_result = models.IntegerField(initial=0)
    num_attempts = models.IntegerField(initial=0)
    num_solved = models.IntegerField(initial=0)
    #my_field2 = models.IntegerField()
    #q1 = models.IntegerField(choices=[[1, 'Yes'], [2, 'No']], label='1.  Do you play in groups?', widget=widgets.RadioSelect)
    #q1_num_errors = models.IntegerField(initial=0)
    #q2 = models.IntegerField(choices=[[1, 'yes'], [2, 'no']], label='Will your group members change?', widget=widgets.RadioSelect)
    #q2_num_errors = models.IntegerField(initial=0)
    #q3 = models.IntegerField(choices=[[1, '1'], [2, '2'], [3, '3'], [4, '4']], label='How many numbers will you add to earn ECUs  ', widget=widgets.RadioSelect)
    #q3_num_errors = models.IntegerField(initial=0)
    #q4 = models.IntegerField(choices=[[1, 'Authority'], [2, 'Worker'], [3, 'Manager']], label='Who earns ECUs even is they do not any numbers correctly?', widget=widgets.RadioSelect)
    #q4_num_errors = models.IntegerField(initial=0)
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

    report_reward = models.IntegerField(initial=0)
    #report_earnings = models.IntegerField(initial=0)  # Earnings from report/reward mechanics
    #manager_earnings = models.IntegerField(initial=0)  # Manager's custom earnings
    #authority_earnings = models.IntegerField(initial=0)  # Authority's custom earnings
    #belief_payoff = models.IntegerField(initial=0)


    amount_lost = models.IntegerField(initial=0)
    amount_stolen = models.IntegerField(initial=0)  # amount manager steals from paired worker

    transfer_paid = models.IntegerField(initial=0)  # manager to authority
    transfer_received = models.IntegerField(initial=0)  #


    manager_take_earnings = models.IntegerField(initial=0)

    player_role = models.StringField(initial="Unknown")  # Add role explicitly
    unique_id = models.StringField()  # A unique identifier for each player

    in_group_match = models.BooleanField(
        initial=False,
        doc="Whether manager was matched with the worker from their own group"
    )

    pair_id = models.StringField(blank=True, initial='')  # Unique ID for the matched pair per round
    external_worker_code = models.StringField(blank=True, initial='', doc="Participant code of the worker paired with this manager")
    external_manager_code = models.StringField(blank=True, initial='', doc="Participant code of the manager paired with this worker")
    internal_manager_code = models.StringField(blank=True, initial='', doc="Participant code of the manager in this player's fixed group")
    internal_worker_code = models.StringField(blank=True, initial='', doc="Participant code of the worker in this player's fixed group")

    def set_treatment_probability(self):
        treatment_order = self.session.config.get("treatment_order", "low_to_high")
        if treatment_order == "low_to_high":
            self.treatment_probability = C.ALPHA_LOW if self.round_number <= C.SWITCH_ROUND else C.ALPHA_HIGH
        else:  # high_to_low
            self.treatment_probability = C.ALPHA_HIGH if self.round_number <= C.SWITCH_ROUND else C.ALPHA_LOW
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

    # Find matched victim worker (unchanged)
    victim_participant_id = manager.participant.vars.get('paired_worker_id')
    victim_worker = None
    for p in group.subsession.get_players():
        if p.participant.id == victim_participant_id:
            victim_worker = p
            break
    if victim_worker is None:
        raise ValueError(f"Paired victim_worker with participant ID {victim_participant_id} not found!")

    # --- Theft (unchanged) ---
    pct = group.field_maybe_none('percentage_taken') or 0
    wants_to_take = bool(group.field_maybe_none('wants_to_take'))
    amount_taken = int((pct / 100) * victim_worker.points_earned) if (wants_to_take and pct > 0) else 0
    manager.amount_stolen = amount_taken
    victim_worker.amount_lost = amount_taken

    # --- Bribe offered & accepted flag (NEW: single source of truth) ---
    wants_to_pay_transfer     = bool(group.field_maybe_none('wants_to_pay_transfer'))
    authority_accepted_trans  = bool(group.field_maybe_none('authority_accepted_transfer'))

    group.bribe_offered_and_accepted = wants_to_pay_transfer and authority_accepted_trans

    # If you want to require theft for a “bribe” to count, use:
    group.bribe_offered_and_accepted = wants_to_take and wants_to_pay_transfer and authority_accepted_trans

    # --- Transfers based on the flag (also set group.transfer_amount as you wanted) ---
    if group.bribe_offered_and_accepted:
        group.transfer_amount     = C.TRANSFER_AMOUNT
        authority.transfer_received = C.TRANSFER_AMOUNT - C.INTERFERE_COST
        manager.transfer_paid       = C.TRANSFER_AMOUNT
    else:
        group.transfer_amount       = 0
        authority.transfer_received = 0
        manager.transfer_paid       = 0

    # --- Reporting logic: success chance uses treatment_probability ONLY if a bribe was both offered & accepted ---
    theft_occurred = amount_taken > 0
    worker = group.get_player_by_id(1)
    is_victim = (worker == victim_worker)
    report_threshold = (group.field_maybe_none('min_report_percentage_self') if is_victim
                        else group.field_maybe_none('min_report_percentage_other_worker'))
    if report_threshold is None:
        report_threshold = 51

    worker.intended_to_report = (theft_occurred and (report_threshold <= pct < 51))

    if worker.intended_to_report:
        success_chance = (worker.treatment_probability
                          if group.bribe_offered_and_accepted
                          else C.REPORT_PENALTY_PROBABILITIES[0])
        report_successful = random.uniform(0, 1) < success_chance
        worker.worker_reported  = True
        worker.report_successful = report_successful

        # Your stated payoffs: +100 if successful, -100 if unsuccessful
        worker.report_reward = 100 if report_successful else -100

        if report_successful:
            # Manager is punished (you said: do NOT zero amount_stolen)
            manager.total_earnings = 0
            manager.payoff = 0
    else:
        worker.worker_reported   = False
        worker.report_successful = False
        worker.report_reward     = 0

    # --- Earnings (unchanged except for the report_reward size) ---
    if not worker.report_successful:
        manager.total_earnings = manager.points_earned + manager.amount_stolen - manager.transfer_paid

    worker.total_earnings    = worker.points_earned + worker.report_reward - worker.amount_lost
    authority.total_earnings = authority.points_earned + authority.transfer_received

    worker.payoff    = worker.total_earnings
    manager.payoff   = manager.total_earnings
    authority.payoff = authority.total_earnings

    # Populate effort_points explicitly
    for pl in group.get_players():
        pl.effort_points = pl.points_earned




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



        if values['wants_to_take']:
            if values['percentage_taken'] is None or not (1 <= values['percentage_taken'] <= 50):
                errors['percentage_taken'] = "Please enter a percentage between 1 and 50."
        else:
            if values['wants_to_pay_transfer']:
                errors['wants_to_pay_transfer'] = "You cannot offer a transfer if you're not taking from the worker."



        return errors if errors else None

    @staticmethod
    def get_timeout_seconds(player: Player):
        return 180 if player.round_number == 1 or player.round_number == C.SWITCH_ROUND else 90
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        round_number = player.round_number

        # Retrieve the paired worker for this manager
        paired_worker_id = player.participant.vars.get('paired_worker_id')
        victim_worker = get_player_by_participant_id(group, paired_worker_id, player.round_number) if paired_worker_id else None

        player.set_treatment_probability()
        treatment_percentage = int(float(player.treatment_probability) * 100) if player.treatment_probability is not None else 0
        print(f"Player {player.id_in_group}: treatment_probability = {player.treatment_probability}, type = {type(player.treatment_probability)}")


        return {
            'victim_worker': victim_worker,
            'worker_points_earned': victim_worker.points_earned if victim_worker else 0,
            'worker_solved_problems': victim_worker.num_solved if victim_worker else 0,
            'percentage_choices': C.PERCENTAGE_CHOICES,
            'report_penalty_probabilities': C.REPORT_PENALTY_PROBABILITIES[0],
            'treatment_probability': player.treatment_probability,
            'interfere_cost': C.INTERFERE_COST,
            'timeout_seconds': ManagerDecisionPage.get_timeout_seconds(player),
            'can_offer_transfer': group.wants_to_take,  # Only allow transfer if taking
            'wants_to_take': group.wants_to_take,  # Pass current state for toggle logic
            'points_earned': player.points_earned,
            'treatment_percentage': treatment_percentage,
            'penalty_percentage': C.PENALTY_PERCENTAGE,
            'external_worker_code': player.external_worker_code,  # Add for debugging

        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        paired_worker_id = player.participant.vars.get('paired_worker_id')
        paired_worker = get_player_by_participant_id(group, paired_worker_id,
                                                     player.round_number) if paired_worker_id else None

        if timeout_happened:
            player.timeout_flag = True
            if not group.wants_to_take:
                group.wants_to_pay_transfer = False
                group.percentage_taken = 0

        # Explicitly ensure percentage_taken is defined
        if group.field_maybe_none('percentage_taken') is None:
            group.percentage_taken = 0

        # Ensure consistency: if the manager doesn't take, reset transfer and percentage
        if not group.wants_to_take:
            group.wants_to_pay_transfer = False
            group.percentage_taken = 0
            player.manager_take_earnings = player.points_earned
            if paired_worker:
                paired_worker.amount_lost = 0
        else:
            # Manager wants to take; calculate amount stolen
            if paired_worker and group.percentage_taken > 0:
                amount_taken = int((group.percentage_taken / 100) * paired_worker.points_earned)
                player.manager_take_earnings = player.points_earned + amount_taken
                paired_worker.amount_lost = amount_taken
            else:
                player.manager_take_earnings = player.points_earned
                if paired_worker:
                    paired_worker.amount_lost = 0


    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2  # Only for the Manager



class WorkerPage(Page):
    import random
    form_model = 'group'
    form_fields = ['min_report_percentage_other_worker', 'min_report_percentage_self']
    timer_text = 'Time left:'

    @staticmethod
    def get_timeout_seconds(player: Player):
        return 180 if player.round_number == 1 or player.round_number == C.SWITCH_ROUND else 90


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

        #my attempt at making the probabilities as percentages

        treatment_percentage = int(float(player.treatment_probability) * 100) if player.treatment_probability is not None else 0
        print(f"Player {player.id_in_group}: treatment_probability = {player.treatment_probability}, type = {type(player.treatment_probability)}")
        
        
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
            'penalty_percentage': C.PENALTY_PERCENTAGE,
            'treatment_percentage': treatment_percentage,
            'worker_report_reward': C.WORKER_REPORT_REWARD,
            'worker_report_penalty': C.WORKER_REPORT_PENALTY,
            'random_start_self': random.randint(1, 51),
            'random_start_other': random.randint(1, 51),
            'points_earned': player.points_earned,
            'penalty_percentage': C.PENALTY_PERCENTAGE,
            'external_manager_code': player.external_manager_code,  # Add for debugging
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


    @staticmethod
    def error_message(player, values):
        pass


    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        player.set_treatment_probability()
        treatment_percentage = int(float(player.treatment_probability) * 100) if player.treatment_probability is not None else 0
        print(f"Player {player.id_in_group}: treatment_probability = {player.treatment_probability}, type = {type(player.treatment_probability)}")

        return {
            'treatment_probability': player.treatment_probability,
            'interfere_cost': C.INTERFERE_COST,
            'transfer_amount': C.TRANSFER_AMOUNT,
            'timeout_seconds': AuthorityPage.get_timeout_seconds(player),  # Pass timer value to HTML
            'points_earned': player.points_earned,
            'treatment_percentage': treatment_percentage,

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

        # Identify the manager and worker in THIS group
        manager = group.get_player_by_id(2)
        worker_in_group = group.get_player_by_id(1)

        # Retrieve the reporting thresholds
        min_report_percentage_other_worker = group.field_maybe_none('min_report_percentage_other_worker')
        min_report_percentage_self = group.field_maybe_none('min_report_percentage_self')

        # Check if group.victim_worker_id exists and if the player is the direct victim
       # victim_worker_id = group.field_maybe_none('victim_worker_id')
        #is_victim = player.id_in_group == victim_worker_id if victim_worker_id is not None else False
        victim_participant_id = manager.participant.vars.get('paired_worker_id')
        is_victim = (player.participant.id == victim_participant_id) if victim_participant_id is not None else False


        # Get the victim worker for display purposes (not reporting)
        
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
        worker_reported = worker_in_group.worker_reported
        report_successful = worker_in_group.report_successful


        # Authority transfer details
        #authority_transfer_asked = group.field_maybe_none('authority_transfer_asked')
        authority_accepted_transfer = group.field_maybe_none('authority_accepted_transfer')

        # Handle earnings display for each role
        total_earnings = player.total_earnings or 0
        worker_payoff = int(player.payoff) if player.id_in_group == 1 else 'N/A'
        manager_payoff = int(player.payoff) if player.id_in_group == 2 else 'N/A'
        authority_payoff = int(player.payoff) if player.id_in_group == 3 else 'N/A'
        paired_worker_id = player.participant.vars.get('paired_worker_id')
        worker = get_player_by_participant_id(group, paired_worker_id, player.round_number) if paired_worker_id else None
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




def set_group_results(group: Group):
    # Calculate RET task points for all players and store them in points_earned
    for p in group.get_players():
        if p.get_role() == "Authority":
            p.points_earned = C.ENDOWMENT  # Authority gets only salary
        else:
            p.points_earned = p.num_solved * C.BONUS_PER_SOLVED_ADDITION  # Workers and Managers get RET earnings


class RETResults(Page):
    form_model = 'player'
    timer_text = 'Time left:'

    @staticmethod
    def vars_for_template(player: Player):
        # Calculate payoff individually without needing the whole group
        if player.id_in_group == 3:
            player.points_earned = C.ENDOWMENT
        else:
            player.points_earned = player.num_solved * C.BONUS_PER_SOLVED_ADDITION

        player_performance = {
            'id': player.id_in_group,
            'role': player.get_role(),
            'num_solved': player.num_solved,
            'points_earned': player.points_earned
        }

        # Return a dictionary with `timeout_seconds` at the top level
        return {
            'player_performance': player_performance,
            'timeout_seconds': RETResults.get_timeout_seconds(player),  # Ensure it’s at the top level
            'is_authority': player.id_in_group == 3,
            'salary': C.ENDOWMENT,
        }
    @staticmethod
    def get_timeout_seconds(player: Player):
        return 30 if player.round_number == 1 else 20

    def is_displayed(player: Player):
        return True  # Display for all players before they make decisions


    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        #player.payoff = player.points_earned  # Ensure payoff is stored properly
         # Defensive: compute points_earned again in case vars_for_template was never hit
        if player.id_in_group == 3:
            player.points_earned = C.ENDOWMENT
        else:
            player.points_earned = player.num_solved * C.BONUS_PER_SOLVED_ADDITION

        # Mirror points_earned to effort_points, and initialize payoff
        player.effort_points = player.points_earned
        player.payoff = player.points_earned

class BeforeDecisionsWaitPage(WaitPage):
    wait_for_all_groups = True  # Ensures all players from all groups arrive

    title_text = " "

    body_text = "Please wait."

    def after_all_players_arrive(self):
        # Re-pair managers and workers each round
        #self.subsession.pair_managers_with_workers(self.subsession)
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

#class NextRound(WaitPage):
 #   after_all_players_arrive = set_payoffs

  #  title_text = " "
   # body_text = "Please wait until the experiment continues."


page_sequence = [YourRoleIs, RET, RETResults, BeforeDecisionsWaitPage, ManagerDecisionPage, WorkerPage, AuthorityPage, ResultsWaitPage, DecisionResults, RoundResults,  TreatmentChangeAnnouncement, RandomRoundWaitPage, RandomRoundPayment ]
