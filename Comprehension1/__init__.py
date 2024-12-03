from otree.api import *

c = cu

doc = ''


class C(BaseConstants):
    NAME_IN_URL = 'focal_comprehension'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    INSTRUCTIONS_TEMPLATE = 'bertrand_instructions/instructions.html'
    ECU_LABEL = 'ECUs'

    QUIZ_FIEDLS = [f'quiz_{n}' for n in range(1, 9)]
    QUIZ_LABELS_2 = [
        "If the firms in the market have a price of 87 and 76; what is the price at which the goods will be sold in the market?",
        "If your firm's price is 91 and the other firm's price is 95, at what price will the goods be sold?",
        "If your firm's price is 2 and the other firm's price is 90, what will be the profit of your firm, if there are 200 consumers in the market?",
        "If your firm's price is 89 and the other firm's price is 89 as well, what will be the profit of your firm, if there are 200 consumers in the market?",
        "If your firm's price is 71 and the other firm's price is 86, what will be the profit of the other firm?",
        "If your firm makes 6000 ECUs, how much money (in cents) will you get?",
        "My team will change every round.",
        "I will be provided with information or new instructions if my team is about to change."
    ]
    QUIZ_LABELS_4 = [
        "If the firms in the market have a price of 27 and 22; what is the price at which the goods will be sold in the market?",
        "If your firm's price is 23 and the other firm's price is 26, at what price will the goods be sold?",
        "If your firm's price is 2 and the other firm's price is 30, what will be the profit of your firm, if there are 200 consumers in the market?",
        "If your firm's price is 28 and the other firm's price is 28 as well, what will be the profit of your firm, if there are 200 consumers in the market?",
        "If your firm's price is 21 and the other firm's price is 26, what will be the profit of the other firm?",
        "If your firm makes 6000 ECUs, how much money (in cents) will you get?",
        "My team will change every round.",
        "I will be provided with information or new instructions if my team is about to change."
    ]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    quiz_1 = models.IntegerField()
    quiz_1_wrong_attempts = models.IntegerField(initial=0)

    quiz_2 = models.IntegerField()
    quiz_2_wrong_attempts = models.IntegerField(initial=0)

    quiz_3 = models.IntegerField()
    quiz_3_wrong_attempts = models.IntegerField(initial=0)

    quiz_4 = models.IntegerField()
    quiz_4_wrong_attempts = models.IntegerField(initial=0)

    quiz_5 = models.IntegerField()
    quiz_5_wrong_attempts = models.IntegerField(initial=0)

    quiz_6 = models.IntegerField()
    quiz_6_wrong_attempts = models.IntegerField(initial=0)

    quiz_7 = models.BooleanField()
    quiz_7_wrong_attempts = models.IntegerField(initial=0)

    quiz_8 = models.BooleanField()
    quiz_8_wrong_attempts = models.IntegerField(initial=0)



# PAGES
class Instructions(Page):
    pass


class Comprehension(Page):
    form_model = 'player'
    form_fields = C.QUIZ_FIEDLS

    @staticmethod
    def vars_for_template(player: Player):
        labels = C.QUIZ_LABELS_2 if player.session.config['session_treatment'] == "NO_YES" else C.QUIZ_LABELS_4
        return dict(
            fields=list(zip(C.QUIZ_FIEDLS, labels))
        )

    @staticmethod
    def error_message(player: Player, values):
        if player.session.config['session_treatment'] == "NO_YES":
                solutions = dict(
                    quiz_1=(76,'The firm with the lowest price will be able to sell in the market. Therefore, price at which the goods will be sold is 76.'),
                    quiz_2=(91, 'The goods will be sold at a price of 91.'),
                    quiz_3=(400, 'The goods will be sold at a price of 2 and the profits will be 2x200= 400.'),
                    quiz_4=(8900, 'The firms will share the market and sell their goods to 100 customer each and will make a profit of 89x100= 8900.'),
                    quiz_5=(0, '0 because the lowest price in the market is 71 at which the goods will be sold.'),
                    quiz_6=(60, 'You will get 60 cents.'),
                    quiz_7=(False, 'Your team will not change every round.'),
                    quiz_8=(True, 'If your team is about to change, you will be informed beforehand.')
                )
        else:
                solutions = dict(
                    quiz_1=(22, 'The firm with the lowest price will be able to sell in the market. Therefore, price at which the goods will be sold is 22.'),
                    quiz_2=(23, 'The goods will be sold at a price of 23.'),
                    quiz_3=(400, 'The goods will be sold at a price of 2 and the profits will be 2x200= 400.'),
                    quiz_4=(2800, 'The firms will share the market and sell their goods to 100 customers each and will make a profit of 28x100= 2800.'),
                    quiz_5=(0, '0 because the lowest price in the market is 21 at which the goods will be sold.'),
                    quiz_6=(60, 'You will get 60 cents.'),
                    quiz_7=(False, 'Your team will not change every round.'),
                    quiz_8=(True, 'If your team is about to change, you will be informed beforehand.')
                )

        error_msgs = {
            k: solutions[k][1] for k, v in values.items() if v != solutions[k][0]
        }

        for k in error_msgs.keys():
            num = getattr(player, f'{k}_wrong_attempts')
            setattr(player, f'{k}_wrong_attempts', num + 1)

        return error_msgs


class EndComprehension(Page):
    pass


page_sequence = [
    Instructions, Comprehension, EndComprehension
]