from otree.api import *
import math
c = cu


class C(BaseConstants):
    NAME_IN_URL = 'focal_crt'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    REWARD_PER_CORRECT_ANSWER = 0.50  # 50 cents per correct answer
    EXCHANGE_RATE = 55


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    num_failed_attempts = models.IntegerField(initial=0)
    failed_too_many = models.BooleanField(initial=False)

    quiz1 = models.IntegerField(
        label='A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost (in cents)?')
    quiz1_wrong = models.IntegerField(initial=0)

    quiz2 = models.IntegerField(
        label='If it takes 5 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?')
    quiz2_wrong = models.IntegerField(initial=0)

    quiz3 = models.IntegerField(
        label='In a lake, there is a patch of lily pads. Every day, the patch doubles in size. If it takes 48 days for the patch to cover the entire lake, how long would it take for the patch to cover half the lake?')
    quiz3_wrong = models.IntegerField(initial=0)

    quiz4 = models.IntegerField(
        label='A box of staples has a length of 6 cm, a width of 7 cm, and a volume of 378 cm cubed. What is the height of the box?')
    quiz4_wrong = models.IntegerField(initial=0)

    quiz5 = models.IntegerField(
        label='A basketball player averaged 20 points a game over the course of six games. His scores in five of those games were 23, 18, 16, 24, and 27. How many points did he score in the sixth game?')
    quiz5_wrong = models.IntegerField(initial=0)

    quiz6 = models.IntegerField(
        label='A physical education class has three times as many girls as boys. During a class basketball game, the girls average 18 points each, and the class as a whole averages 17 points per person. How many points does each boy score on average?')
    quiz6_wrong = models.IntegerField(initial=0)

    def calculate_crt_payoff(self):
        # Define correct answers
        solutions = {
            'quiz1': 5,
            'quiz2': 5,
            'quiz3': 47,
            'quiz4': 9,
            'quiz5': 12,
            'quiz6': 14,
        }

        # Count correct answers
        correct_count = sum(
            1 for quiz, answer in solutions.items() if getattr(self, quiz) == answer
        )

        # Add a fixed 50 cents per correct answer directly to player.payoff
        crt_earnings = correct_count * C.REWARD_PER_CORRECT_ANSWER
        self.payoff += crt_earnings

        # Store CRT earnings in participant.vars for use in other apps if needed
        self.participant.vars['crt_earnings'] = crt_earnings


class CRT(Page):
    form_model = 'player'
    form_fields = ['quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5', 'quiz6']

    @staticmethod
    def error_message(player: Player, values):
        solutions = dict(
            quiz1=(5, 5),
            quiz2=(5, 5),
            quiz3=(47, 47),
            quiz4=(9, 9),
            quiz5=(12, 12),
            quiz6=(14, 14),
        )
        errors = {
            k: solutions[k][1] for k, v in values.items() if v != solutions[k][0]
        }

        for k in errors.keys():
            num = getattr(player, f'{k}_wrong')
            setattr(player, f'{k}_wrong', num + 1)

        if errors:
            player.num_failed_attempts += 1
            if player.num_failed_attempts >= 1:
                player.failed_too_many = True
            else:
                return errors

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Calculate and add the CRT payoff
        player.calculate_crt_payoff()


class Next(Page):

    @staticmethod
    def vars_for_template(player: Player):
        # Retrieve CRT earnings, selected round earnings, and baseline earnings from participant variables
        crt_earnings = player.participant.vars.get('crt_earnings', 0)  # CRT earnings
        selected_round_earnings = player.participant.vars.get('selected_round_earnings', 0)  # Random round earnings
        baseline_earnings = player.participant.vars.get('payoff_baseline', 0)  # Baseline earnings in ECUs

        # Convert selected round earnings and baseline earnings to currency
        selected_round_earnings_currency = selected_round_earnings / C.EXCHANGE_RATE
        baseline_earnings_currency = baseline_earnings / C.EXCHANGE_RATE

        # Calculate total earnings by combining all components
        total_earnings = math.ceil(selected_round_earnings_currency + crt_earnings + baseline_earnings_currency)

        # Set participant payoff for use in the payment tab
        player.participant.payoff = total_earnings

        # Return total earnings to display or use in templates if needed
        return {
            'total_earnings': total_earnings
        }

    @staticmethod
    def is_displayed(player: Player):
        return player.failed_too_many


page_sequence = [CRT, Next]