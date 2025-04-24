from os import environ

import os
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [os.environ.get('REDIS_URL')],
        },
    },
}

SESSION_CONFIG_DEFAULTS = dict(real_world_currency_per_point=1, participation_fee=5)


SESSION_CONFIGS = [
    dict(
        name='low_to_high',
        display_name='Low to High Interference',
        num_demo_participants=9,
        app_sequence=['intro', 'Comprehension',  'ret', 'crt', 'peq'],
        treatment_order="low_to_high",
    ),
    dict(
        name="high_to_low",
        display_name="High to Low Interference",
        num_demo_participants=9,
        app_sequence=['intro', 'Comprehension', 'ret', 'crt', 'peq'],
        treatment_order="high_to_low",
    ),
]


ROOMS = [
    dict(
        name='high_low_1',
        display_name='High to Low 1',
        participant_label_file='_rooms/workstation.txt',
    ),
    dict(
        name='low_high_1',
        display_name='Low to High 1',
        participant_label_file='_rooms/workstation.txt',
    ),
dict(
        name='high_low_2',
        display_name='High to Low 2',
        participant_label_file='_rooms/workstation.txt',
    ),
dict(
        name='low_high_2',
        display_name='Low to High 2',
        participant_label_file='_rooms/workstation.txt',
    ),


]


LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = False
DEMO_PAGE_INTRO_HTML = ''
PARTICIPANT_FIELDS = ['payoff_baseline', 'wants_to_pay_transfer', 'wants_to_take', 'player_moving', 'end_payoff_two', 'end_payoff_four', 'selected_round', 'payoff_ret', 'selected_round_earnings']
SESSION_FIELDS = ['show_round', 'treatment_phase']  # Corrected syntax
DEBUG = False

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

SECRET_KEY = 'blahblah'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']
