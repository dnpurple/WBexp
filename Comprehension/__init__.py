from otree.api import *

c = cu
doc = ''


class C(BaseConstants):
    NAME_IN_URL = 'wb_comprehension'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    INSTRUCTIONS_TEMPLATE = 'my_instructions/instructions.html'
    ECU_LABEL = 'ECUs'
    PERCENTAGE_LABEL = '%'

    QUIZ_FIELDS = [f'quiz_{n}' for n in range(1, 9)]
    QUIZ_LABELS_NO = [
        "If a manager takes from a worker, will the worker lose all their earnings?",
        "Can a report be made if the manager takes from a worker?",
        "What is the likelihood of a successful report?",
        "Can anything be done to change the likelihood of a successful report if no transfer is accepted?",
        "Will a worker receive a reward if their report is successful?",
        "If a report is successful, is the worker that was taken from reimbursed?",
        "My group will change at some point in the experiment.",
        "My role will change at some point in the experiment."
    ]
    QUIZ_LABELS_LOW = [
        "If a manager takes from a worker, will the worker lose all their earnings?",
        "Can a report be made if the manager takes from a worker?",
        "What is the likelihood of a successful report if no transfer is accepted?",
        "Can anything be done to change the likelihood of a successful report?",
        "Will a worker receive a reward if their report is successful?",
        "If a report is successful, is the worker that was taken from reimbursed?",
        "My group will change at some point in the experiment.",
        "My role will change at some point in the experiment."
    ]
    QUIZ_LABELS_HIGH = [
        "If a manager takes from a worker, will the worker lose all their earnings?",
        "Can a report be made if the manager takes from a worker?",
        "What is the likelihood of a successful report if no transfer is accepted?",
        "Can anything be done to change the likelihood of a successful report?",
        "Will a worker receive a reward if their report is successful?",
        "If a report is successful, is the worker that was taken from reimbursed?",
        "My group will change at some point in the experiment.",
        "My role will change at some point in the experiment."
    ]

    # Local treatment mapping
    TREATMENT_MAP = {
        'low_to_high': 0.7,  # LOW interference (0.7) for comprehension
        'high_to_low': 0.3,  # HIGH interference (0.3) for comprehension
    }


class Subsession(BaseSubsession):
    pass  # No need to set session fields since we’re using config directly


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    quiz_1 = models.BooleanField()
    quiz_1_wrong_attempts = models.IntegerField(initial=0)

    quiz_2 = models.BooleanField()
    quiz_2_wrong_attempts = models.IntegerField(initial=0)

    quiz_3 = models.IntegerField()
    quiz_3_wrong_attempts = models.IntegerField(initial=0)

    quiz_4 = models.BooleanField()
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
    timer_text = 'Time left:'
    @staticmethod
    def vars_for_template(player: Player):
        # Get treatment order from session config
        treatment_order = player.session.config['treatment_order']
        interference_level = C.TREATMENT_MAP[treatment_order]  # 0.7 or 0.3

        return {
            'treatment_probability': int(interference_level * 100),  # e.g., 70 or 30
            'interference_level': 'LOW' if interference_level == 0.7 else 'HIGH'
        }


class Comprehension(Page):
    form_model = 'player'
    form_fields = C.QUIZ_FIELDS
    #timeout_seconds = 300  # 5-minute timer

    @staticmethod
    def vars_for_template(player: Player):
        # Get treatment order from session config
        treatment_order = player.session.config['treatment_order']
        interference_level = C.TREATMENT_MAP[treatment_order]  # 0.7 or 0.3

        # Map interference level to quiz labels
        treatment_mapping = {
            0.7: C.QUIZ_LABELS_LOW,  # LOW interference (0.7)
            0.3: C.QUIZ_LABELS_HIGH  # HIGH interference (0.3)
        }
        labels = treatment_mapping.get(interference_level, C.QUIZ_LABELS_NO)

        return dict(
            fields=list(zip(C.QUIZ_FIELDS, labels))
        )

    @staticmethod
    def error_message(player: Player, values):
        # Get treatment order from session config
        treatment_order = player.session.config['treatment_order']
        interference_level = C.TREATMENT_MAP[treatment_order]  # 0.7 or 0.3

        # Define solutions for each interference level
        solutions_mapping = {
            0.7: dict(  # LOW interference (0.7)
                quiz_1=(False, "The manager can only take up to 50% of a matched worker's earnings."),
                quiz_2=(True, 'Workers can report the manager in their groups if the manager takes from a worker.'),
                quiz_3=(97, 'The likelihood of a successful report is 97%.'),
                quiz_4=(True, 'The likelihood of a successful report will fall if the authority accepts a transfer.'),
                quiz_5=(True, 'Yes, the worker earns a reward for a successful report. They also receive a penalty if the report is unsuccessful.'),
                quiz_6=(False, 'No, the matched worker is not reimbursed.'),
                quiz_7=(False, 'Groups remain constant throughout the experiment.'),
                quiz_8=(False, 'Your role will remain the same throughout the experiment.')
            ),
            0.3: dict(  # HIGH interference (0.3)
                quiz_1=(False, "The manager can only take up to 50% of a matched worker's earnings."),
                quiz_2=(True, 'Workers can report the manager in their groups if the manager takes from a worker.'),
                quiz_3=(97, 'The likelihood of a successful report is 97%.'),
                quiz_4=(True, 'The likelihood of a successful report will fall if the authority accepts a transfer.'),
                quiz_5=(True, 'Yes, the worker earns a reward for a successful report. They also receive a penalty if the report is unsuccessful.'),
                quiz_6=(False, 'No, the matched worker is not reimbursed.'),
                quiz_7=(False, 'Groups remain constant throughout the experiment.'),
                quiz_8=(False, 'Your role will remain the same throughout the experiment.')
            ),
            None: dict(  # Default (no interference)
                quiz_1=(False, "The manager can only take up to 50% of a matched worker's earnings."),
                quiz_2=(True, 'Workers can report the manager in their groups if the manager takes from a worker.'),
                quiz_3=(97, 'The likelihood of a successful report is 97%.'),
                quiz_4=(False, 'The likelihood of a successful report cannot be changed.'),
                quiz_5=(True, 'Yes, the worker earns a reward for a successful report. They also receive a penalty if the report is unsuccessful.'),
                quiz_6=(False, 'No, the matched worker is not reimbursed.'),
                quiz_7=(False, 'Groups remain constant throughout the experiment.'),
                quiz_8=(False, 'Your role will remain the same throughout the experiment.')
            ),
        }

        solutions = solutions_mapping.get(interference_level, solutions_mapping[None])
        error_msgs = {k: solutions[k][1] for k, v in values.items() if v != solutions[k][0]}

        for k in error_msgs.keys():
            num = getattr(player, f'{k}_wrong_attempts')
            setattr(player, f'{k}_wrong_attempts', num + 1)

        return error_msgs


class EndComprehension(Page):
    pass

class SyncWaitPage(WaitPage):
    title_text = ""
    body_text = "Please wait until all participants have arrived."

    wait_for_all_groups = True  # Waits for all participants in the session


    # No need for after_all_players_arrive; default behavior advances when all arrive


page_sequence = [Instructions, Comprehension, SyncWaitPage]