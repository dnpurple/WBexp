from otree.api import *

c = cu

doc = ''


class C(BaseConstants):
    NAME_IN_URL = 'comprehension'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    INSTRUCTIONS_TEMPLATE = 'my_instructions/instructions.html'
    ECU_LABEL = 'ECUs'
    Percentage_LABEL = '%'

    QUIZ_FIEDLS = [f'quiz_{n}' for n in range(1, 9)]
    QUIZ_LABELS_NO = [
        "If a manger takes from a worker, will the worker lose all their earnings?",
        "Can a report be made if the managers takes from a worker?",
        "Can anything be done to change the likelihood of a successful report?",
        "What is the likelihood of a successful report?",
        "Will a worker receive a reward if their report is successful?",
        "If a report is successful, is the matched worker reimbursed?",
        "My firm will change at some point in the experiment.",
        "My role will change at some point in the experiment."
    ]
    QUIZ_LABELS_LOW = [
        "If a manger takes from a worker, will the worker lose all their earnings?",
        "Can a report be made if the managers takes from a worker?",
        "Can anything be done to change the likelihood of a successful report?",
        "What is the likelihood of a successful report if no transfer is accepted?",
        "Will a worker receive a reward if their report is successful?",
        "If a report is successful, is the matched worker reimbursed?",
        "My firm will change at some point in the experiment.",
        "My role will change at some point in the experiment."
    ]
    QUIZ_LABELS_HIGH = [
        "If a manger takes from a worker, will the worker lose all their earnings?",
        "Can a report be made if the managers takes from a worker?",
        "Can anything be done to change the likelihood of a successful report?",
        "What is the likelihood of a successful report if no transfer is accepted?",
        "Will a worker receive a reward if their report is successful?",
        "If a report is successful, is the matched worker reimbursed?",
        "My firm will change at some point in the experiment.",
        "My role will change at some point in the experiment."
    ]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    quiz_1 = models.BooleanField()
    quiz_1_wrong_attempts = models.IntegerField(initial=0)

    quiz_2 = models.BooleanField()
    quiz_2_wrong_attempts = models.IntegerField(initial=0)

    quiz_3 = models.BooleanField()
    quiz_3_wrong_attempts = models.IntegerField(initial=0)

    quiz_4 = models.IntegerField()
    quiz_4_wrong_attempts = models.IntegerField(initial=0)

    quiz_5 = models.BooleanField()
    quiz_5_wrong_attempts = models.IntegerField(initial=0)

    quiz_6 = models.BooleanField()
    quiz_6_wrong_attempts = models.IntegerField(initial=0)

    quiz_7 = models.BooleanField()
    quiz_7_wrong_attempts = models.IntegerField(initial=0)

    quiz_8 = models.BooleanField()
    quiz_8_wrong_attempts = models.IntegerField(initial=0)



# PAGES
class Instructions(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return {
            'treatment_probability': int(player.session.config['treatment_probability'] * 100),  # Convert to percentage
            'interference_level': player.session.config['interference_level']  # Pass interference level to template
        }


class Comprehension(Page):
    form_model = 'player'
    form_fields = C.QUIZ_FIEDLS

    @staticmethod
    def vars_for_template(player: Player):
        # Mapping the interference levels to the respective quiz labels
        treatment_mapping = {
            "NO": C.QUIZ_LABELS_NO,
            "LOW": C.QUIZ_LABELS_LOW,
            "HIGH": C.QUIZ_LABELS_HIGH,
        }

        # Retrieve the labels based on the session's `interference_level`
        labels = treatment_mapping.get(player.session.config['interference_level'], C.QUIZ_LABELS_NO)

        return dict(
            fields=list(zip(C.QUIZ_FIEDLS, labels))
        )

    @staticmethod
    def error_message(player: Player, values):
        # Define solutions for each interference level
        solutions_mapping = {
            "NO": dict(
                quiz_1=(False, "The manager can only take up to 50% of a matched worker's earnings."),
                quiz_2=(True, 'Workers can report the manager in their groups if the manager takes from a worker.'),
                quiz_3=(False, 'The likelihood of a successful report cannot be changed'),
                quiz_4=(97, 'The likelihood of a successful report is 97%.'),
                quiz_5=(True,
                        'Yes, the worker earns a reward for a successful report. They also receive a penalty if the report is unsuccessful.'),
                quiz_6=(False, 'No, the matched worker is not reimbursed.'),
                quiz_7=(False, 'Firms remain constant throughout the experiment'),
                quiz_8=(False, 'Your role will remain the same throughout the experiment.')
            ),
            "LOW": dict(
                quiz_1=(False, "The manager can only take up to 50% of a matched worker's earnings."),
                quiz_2=(True, 'Workers can report the manager in their groups if the manager takes from a worker.'),
                quiz_3=(True, 'The likelihood of a successful report will fall if the authority accepts a transfer'),
                quiz_4=(97, 'The likelihood of a successful report is 97%.'),
                quiz_5=(True,
                        'Yes, the worker earns a reward for a successful report. They also receive a penalty if the report is unsuccessful.'),
                quiz_6=(False, 'No, the matched worker is not reimbursed.'),
                quiz_7=(False, 'Firms remain constant throughout the experiment'),
                quiz_8=(False, 'Your role will remain the same throughout the experiment.')
            ),
            "HIGH": dict(
                quiz_1=(False, "The manager can only take up to 50% of a matched worker's earnings."),
                quiz_2=(True, 'Workers can report the manager in their groups if the manager takes from a worker.'),
                quiz_3=(True, 'The likelihood of a successful report will fall if the authority accepts a transfer'),
                quiz_4=(97, 'The likelihood of a successful report is 97%.'),
                quiz_5=(True,
                        'Yes, the worker earns a reward for a successful report. They also receive a penalty if the report is unsuccessful.'),
                quiz_6=(False, 'No, the matched worker is not reimbursed.'),
                quiz_7=(False, 'Firms remain constant throughout the experiment'),
                quiz_8=(False, 'Your role will remain the same throughout the experiment.')
            ),
        }

        # Retrieve the correct solutions based on the session's `interference_level`
        solutions = solutions_mapping.get(player.session.config['interference_level'], solutions_mapping["NO"])

        # Check for errors
        error_msgs = {
            k: solutions[k][1] for k, v in values.items() if v != solutions[k][0]
        }

        # Increment wrong attempts for incorrect answers
        for k in error_msgs.keys():
            num = getattr(player, f'{k}_wrong_attempts')
            setattr(player, f'{k}_wrong_attempts', num + 1)

        return error_msgs


class EndComprehension(Page):
    pass


page_sequence = [
    Instructions, Comprehension, EndComprehension
]