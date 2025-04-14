from otree.api import *

c = cu

doc = ''


class C(BaseConstants):
    NAME_IN_URL = 'wb_survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    DICTATOR_ENDOWMENT = 100  # Points for Dictator Game
    DONATION_MAX = 1600  # Points for WP13459R



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    #Demographics
    age = models.IntegerField(label='What is your age?', max=125, min=13)
    gender = models.StringField(choices=[['Male', 'Male'], ['Female', 'Female'], ['Non-binary', 'Non-binary'],
                                         ['Prefer not to say', 'Prefer not to say']], label='What is your gender?',
                                widget=widgets.RadioSelect)
    major = models.StringField(
        choices=[['Agriculture, Food and Life Sciences', 'Agriculture, Food and Life Sciences'], ['Architecture and Design', 'Architecture and Design'],
                 ['Arts and Sciences', 'Arts and Sciences'],
                 ['Business', 'Business'], ['Education and Health', 'Education and Health'], ['Engineering', 'Engineering'],
                 ['Law', 'Law'], ['Others', 'Others']],
        label='Which of the following best describes your major of study?', widget=widgets.RadioSelect)
    econ = models.IntegerField(label='How many Economics classes have you taken so far? (must specify a number)',
                               max=32, min=0)
    uni = models.IntegerField(
        label='How many years of university study have you completed (enter 0 if in first year)? (must specify a number)',
        max=10, min=0)
    gpa = models.FloatField(label='What is your university GPA? (must specify a number)', max=7, min=0)

    # Dictator Game (Hypothetical)
    dictator_kept = models.IntegerField(
        min=0,
        max=C.DICTATOR_ENDOWMENT,
        label="Imagine you have 100 points to allocate. How many points would you keep for yourself? (The rest would go to an anonymous participant, hypothetically.)"
    )

    # GPS Social Preference Questions

    risk_preference = models.IntegerField(
        choices=[[0, '0'], [1, '1'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7'], [8, '8'], [9, '9'], [10, '10']],
        label='Please tell us, in general, how willing or unwilling you are to take risks. Please use a scale from 0 to 10, where 0 means you are "completely unwilling to take risks" and a 10 means you are "very willing to take risks". You can also use any numbers between 0 and 10 to indicate where you fall on the scale, like 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10.',
        widget=widgets.RadioSelectHorizontal)
    time_discounting = models.IntegerField(
        choices=[[0, '0'], [1, '1'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7'], [8, '8'], [9, '9'],
                 [10, '10']],
        label='In comparison to others, are you a person who is generally willing to give up something today in order to benefit from that in the future or are you not willing to do so? Please use a scale from 0 to 10, where a 0 means, “you are completely unwilling to give up something today" and a 10 means “you are very willing to give up something today". You can also use the values in-between to indicate where you fall on the scale.',
        widget=widgets.RadioSelectHorizontal)
    trust = models.IntegerField(
        choices=[[0, '0'], [1, '1'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7'], [8, '8'], [9, '9'],
                 [10, '10']],
        label='How well does the following statement describe you as a person? As long as I am not convinced otherwise, I assume that people have only the best intentions. Please use a scale from 0 to 10, where 0 means “does not describe me at all" and a 10 means “describes me perfectly". You can also use the values in-between to indicate where you fall on the scale.',
        widget=widgets.RadioSelectHorizontal)
    positive_reciprocity_quantitative = models.IntegerField(
        choices=[[5, '5'], [10, '10'], [15, '15'], [20, '20'], [25, '25'], [30, '30']],
        label='Imagine the following situation: you are shopping in an unfamiliar city and realize you lost your way. You ask a stranger for directions. The stranger offers to take you with their car to your destination. The ride takes about 20 minutes and costs the stranger about 20 points in total. The stranger does not want money for it. You carry six bottles of wine with you. The cheapest bottle costs 5 points, the most expensive one 30 points. You decide to give one of the bottles to the stranger as a thank-you gift. Which bottle do you give? Respondents can choose from the following options: The bottle for 5, 10, 15, 20, 25, or 30 points)',
        widget=widgets.RadioSelectHorizontal
    )
    negative_reciprocity_self = models.IntegerField(
        choices=[[0, '0'], [1, '1'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7'], [8, '8'], [9, '9'],
                 [10, '10']],
        label='How willing are you to punish someone who treats you unfairly, even if there may be costs for you? Please use a scale from 0 to 10, where 0 means "completely unwilling to do so" and 10 means "very willing to do so". You can also use any number between 0 and 10 to indicate where you fall on the scale.',
        widget=widgets.RadioSelectHorizontal
    )
    negative_reciprocity_others = models.IntegerField(
        choices=[[0, '0'], [1, '1'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7'], [8, '8'], [9, '9'],
                 [10, '10']],
        label='How willing are you to punish someone who treats others unfairly, even if there may be costs for you? Please use a scale from 0 to 10, where 0 means "completely unwilling to do so" and 10 means "very willing to do so". You can also use any number between 0 and 10 to indicate where you fall on the scale.',
        widget=widgets.RadioSelectHorizontal
    )
    altruism_qualitative = models.IntegerField(
        choices=[[0, '0'], [1, '1'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7'], [8, '8'], [9, '9'],
                 [10, '10']],
        label='How willing are you to give to good causes without expecting anything in return? Please use a scale from 0 to 10, where 0 means "completely unwilling to do so" and 10 means "very willing to do so". You can also use any number between 0 and 10 to indicate where you fall on the scale.',
        widget=widgets.RadioSelectHorizontal
    )
    positive_reciprocity_qualitative = models.IntegerField(
        choices=[[0, '0'], [1, '1'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7'], [8, '8'], [9, '9'],
                 [10, '10']],
        label='How well does the following statement describe you as a person? When someone does me a favor, I am willing to return it. Please use a scale from 0 to 10, where 0 means "does not describe me at all" and 10 means "describes me perfectly". You can also use any number between 0 and 10 to indicate where you fall on the scale.',
        widget=widgets.RadioSelectHorizontal
    )
    negative_reciprocity_revenge = models.IntegerField(
        choices=[[0, '0'], [1, '1'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7'], [8, '8'], [9, '9'],
                 [10, '10']],
        label='How well does the following statement describe you as a person? If I am treated very unjustly, I will take revenge at the first occasion, even if there is a cost to do so. Please use a scale from 0 to 10, where 0 means "does not describe me at all" and 10 means "describes me perfectly". You can also use any number between 0 and 10 to indicate where you fall on the scale.',
        widget=widgets.RadioSelectHorizontal
    )
    altruism_quantitative = models.IntegerField(
        min=0,
        max=C.DONATION_MAX,
        label='Imagine the following situation: Today you unexpectedly received 1,600 U.S. dollars. How much of this amount would you donate to a good cause? (Values between 0 and 1,600 dollars are allowed)'
    )


    # TIPI (Personality)
    Extraverted_enthusiastic = models.StringField(
        choices= [['Disagree strongly', 'Disagree strongly'], ['Disagree moderately', 'Disagree moderately'],
                  ['Disagree a little', 'Disagree a little'], ['Neither agree nor disagree', 'Neither agree nor disagree'],
                  ['Agree a little', 'Agree a little'], ['Agree moderately', 'Agree moderately'],
                  ['Agree strongly', 'Agree strongly']],
        label = 'I see myself as: Extraverted, enthusiastic.', widget = widgets.RadioSelect)
    Critical_quarrelsome = models.StringField(
        choices=[['Disagree strongly', 'Disagree strongly'], ['Disagree moderately', 'Disagree moderately'],
                 ['Disagree a little', 'Disagree a little'],
                 ['Neither agree nor disagree', 'Neither agree nor disagree'],
                 ['Agree a little', 'Agree a little'], ['Agree moderately', 'Agree moderately'],
                 ['Agree strongly', 'Agree strongly']],
        label='I see myself as: Critical, quarrelsome.', widget=widgets.RadioSelect)
    Dependable_self_disciplined = models.StringField(
        choices=[['Disagree strongly', 'Disagree strongly'], ['Disagree moderately', 'Disagree moderately'],
                 ['Disagree a little', 'Disagree a little'],
                 ['Neither agree nor disagree', 'Neither agree nor disagree'],
                 ['Agree a little', 'Agree a little'], ['Agree moderately', 'Agree moderately'],
                 ['Agree strongly', 'Agree strongly']],
        label='I see myself as: Dependable, self-disciplined.', widget=widgets.RadioSelect)
    Anxious_easily_upset = models.StringField(
        choices=[['Disagree strongly', 'Disagree strongly'], ['Disagree moderately', 'Disagree moderately'],
                 ['Disagree a little', 'Disagree a little'],
                 ['Neither agree nor disagree', 'Neither agree nor disagree'],
                 ['Agree a little', 'Agree a little'], ['Agree moderately', 'Agree moderately'],
                 ['Agree strongly', 'Agree strongly']],
        label='I see myself as: Anxious, easily upset.', widget=widgets.RadioSelect)
    Open_to_new_experiences_complex = models.StringField(
        choices=[['Disagree strongly', 'Disagree strongly'], ['Disagree moderately', 'Disagree moderately'],
                 ['Disagree a little', 'Disagree a little'],
                 ['Neither agree nor disagree', 'Neither agree nor disagree'],
                 ['Agree a little', 'Agree a little'], ['Agree moderately', 'Agree moderately'],
                 ['Agree strongly', 'Agree strongly']],
        label='I see myself as: Open to new experiences, complex.', widget=widgets.RadioSelect)
    Reserved_quiet = models.StringField(
        choices=[['Disagree strongly', 'Disagree strongly'], ['Disagree moderately', 'Disagree moderately'],
                 ['Disagree a little', 'Disagree a little'],
                 ['Neither agree nor disagree', 'Neither agree nor disagree'],
                 ['Agree a little', 'Agree a little'], ['Agree moderately', 'Agree moderately'],
                 ['Agree strongly', 'Agree strongly']],
        label='I see myself as: Reserved, quiet.', widget=widgets.RadioSelect)
    Sympathetic_warm = models.StringField(
        choices=[['Disagree strongly', 'Disagree strongly'], ['Disagree moderately', 'Disagree moderately'],
                 ['Disagree a little', 'Disagree a little'],
                 ['Neither agree nor disagree', 'Neither agree nor disagree'],
                 ['Agree a little', 'Agree a little'], ['Agree moderately', 'Agree moderately'],
                 ['Agree strongly', 'Agree strongly']],
        label='I see myself as: Sympathetic, warm.', widget=widgets.RadioSelect)
    Disorganized_careless = models.StringField(
        choices=[['Disagree strongly', 'Disagree strongly'], ['Disagree moderately', 'Disagree moderately'],
                 ['Disagree a little', 'Disagree a little'],
                 ['Neither agree nor disagree', 'Neither agree nor disagree'],
                 ['Agree a little', 'Agree a little'], ['Agree moderately', 'Agree moderately'],
                 ['Agree strongly', 'Agree strongly']],
        label='I see myself as: Disorganized, careless.', widget=widgets.RadioSelect)
    Calm_emotionally_stable = models.StringField(
        choices=[['Disagree strongly', 'Disagree strongly'], ['Disagree moderately', 'Disagree moderately'],
                 ['Disagree a little', 'Disagree a little'],
                 ['Neither agree nor disagree', 'Neither agree nor disagree'],
                 ['Agree a little', 'Agree a little'], ['Agree moderately', 'Agree moderately'],
                 ['Agree strongly', 'Agree strongly']],
        label='I see myself as: Calm, emotionally stable.', widget=widgets.RadioSelect)
    Conventional_uncreative = models.StringField(
        choices=[['Disagree strongly', 'Disagree strongly'], ['Disagree moderately', 'Disagree moderately'],
                 ['Disagree a little', 'Disagree a little'],
                 ['Neither agree nor disagree', 'Neither agree nor disagree'],
                 ['Agree a little', 'Agree a little'], ['Agree moderately', 'Agree moderately'],
                 ['Agree strongly', 'Agree strongly']],
        label='I see myself as: Conventional, uncreative.', widget=widgets.RadioSelect)

    # Behavioral Feedback
    reasoning = models.LongStringField(
        label='How did you make your decisions today? Please explain in a few lines.'
    )
    instructions = models.LongStringField(
        label='Were the instructions clear? Please explain in a few lines.'
    )
    understanding = models.LongStringField(
        label='Did you understand the game? Any recommendations? Please explain in a few lines.'
    )


class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'major', 'econ', 'uni', 'gpa']
    timer_text = 'Time left:'
    timeout_seconds = 120  # 4 minutes (adjust as needed)


class TIPI(Page):
    form_model = 'player'
    form_fields = ['Extraverted_enthusiastic','Critical_quarrelsome','Dependable_self_disciplined','Anxious_easily_upset',
                   'Open_to_new_experiences_complex','Reserved_quiet','Sympathetic_warm','Disorganized_careless',
                   'Calm_emotionally_stable','Conventional_uncreative']
    timer_text = 'Time left:'
    timeout_seconds = 300


class Behavioral(Page):
    form_model = 'player'
    form_fields = [
        'dictator_kept',  # Dictator Game
        'risk_preference',  # WP13417R
        'time_discounting',  # WP13418R
        'negative_reciprocity_self',  # WP13419R
        'negative_reciprocity_others',  # WP13420R
        'altruism_qualitative',  # WP13421R
        'positive_reciprocity_qualitative',  # WP13422R
        'negative_reciprocity_revenge',  # WP13423R
        'trust',  # WP13424R
        'positive_reciprocity_quantitative',  # WP13458R
        'altruism_quantitative',  # WP13459R
        'reasoning',
    ]
    timer_text = 'Time left:'
    timeout_seconds = 420


class Thankyou(Page):
    pass

class SurveySyncWaitPage(WaitPage):
    title_text = "Waiting for All Participants"
    body_text = "Please wait until all participants have completed the survey."

    wait_for_all_groups = True

page_sequence = [
    Demographics,
    TIPI,
    Behavioral,
    Thankyou,
    SurveySyncWaitPage  # Moved wait page to end
]
