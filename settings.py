from os import environ
SESSION_CONFIG_DEFAULTS = dict(real_world_currency_per_point=1, participation_fee=7.5)

SESSION_CONFIGS = [
    dict(
        name='whistleblowing_control',
        display_name='Whistleblowing Control (No Interference)',
        num_demo_participants=9,
        app_sequence=['intro', 'Comprehension', 'ret', 'crt', 'peq'],
        interference_level='NO',
        treatment_probability=0.97  # Probability for control (no interference)
    ),
    dict(
        name='whistleblowing_low_interference',
        display_name='Whistleblowing Low Interference',
        num_demo_participants=9,
        app_sequence=['intro', 'Comprehension', 'ret', 'crt', 'peq'],
        interference_level='LOW',
        treatment_probability=0.8  # Probability for low interference
    ),
    dict(
        name='whistleblowing_high_interference',
        display_name='Whistleblowing High Interference',
        num_demo_participants=9,
        app_sequence=['intro', 'Comprehension', 'ret', 'crt', 'peq'],
        interference_level='HIGH',
        treatment_probability=0.5  # Probability for high interference
    ),
]


###for basic testing

#SESSION_CONFIGS = [
 #   dict(
  #       name='ret',
   #      num_demo_participants=None,
    #     app_sequence=['intro', 'ret']
# ),

 #    dict(
  #       name='Whistlebowing',
   #      num_demo_participants=9,
    #     app_sequence=['ret', 'survey', 'peq'],
     #    my_key=0
    # ),
    # dict(
        # name='Comprehension',
        # num_demo_participants=None,
        # app_sequence=['Comprehension1']
#    # ),
#]

#putting things together
#SESSION_CONFIGS = [
    #dict(
        # name='whistlebowing_no_interference',
        #display_name= ' Whistleblowing No Interference'
        # num_demo_participants=9,
        # app_sequence=['intro', 'Comprehension', 'ret']
        #players_per_group=3,
        #session_treatment="NO"
# ),

    # dict(
        # name='whistlebowing_low_interference',
        # display_name= ' Whistleblowing Low Interference',
        # num_demo_participants=9,
        # app_sequence=['intro', 'Comprehension', 'ret'],
        # players_per_group=3,
        # session_treatment="LOW"
    # ),
    # dict(
        # name='whistlebowing_high_interference',
        # display_name= ' Whistleblowing High Interference',
        # num_demo_participants=9,
        # app_sequence=['intro', 'Comprehension', 'ret']
        # players_per_group=3,
        # session_treatment="HIGH"
    # ),
#]

#from Kushal
#SESSION_CONFIGS = [
 #   dict(
  #      name='focal_point_teams_yes_no',
   #     display_name='Focal point - Firms 2 / Employees 2 - YES_NO',
    #    num_demo_participants=4,
     #   app_sequence=['Comprehension1'],
      #  use_browser_bots=False,
       # show_instructions=False,
        #num_firms=2,
    #    players_per_group=2,
     #   session_treatment="YES_NO"
#    ),
 #   dict(
  #      name='focal_point_teams_no_yes',
   #     display_name='Focal point - Firms 2 / Employees 2 - NO_YES',
    #    num_demo_participants=4,
     #   app_sequence=['Comprehension1'],
      #  use_browser_bots=False,
       # show_instructions=False,
#        num_firms=2,
 #       players_per_group=2,
  #      session_treatment="NO_YES"
   # ),
#]


LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = False
DEMO_PAGE_INTRO_HTML = ''
PARTICIPANT_FIELDS = [ 'payoff_baseline', 'wants_to_pay_transfer', 'wants_to_take', 'player_moving', 'end_payoff_two', 'end_payoff_four', 'selected_round', 'payoff_ret', 'selected_round_earnings']

SESSION_FIELDS = ['show_round = True']

#PARTICIPANT_FIELDS = ['risk_level', 'chat', 'payoff_collective_risk', 'dropout', 'payoff_baseline', 'collective_risk_round_payoff', 'total_earnings']
#SESSION_FIELDS = []
ROOMS = []

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

SECRET_KEY = 'blahblah'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']

