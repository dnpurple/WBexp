import intro as pages
from . import *
c = cu

class PlayerBot(Bot):
    def play_round(self):
        yield Consent, dict(consent=True)
        yield Welcome
        yield PaymentInfo
        yield GeneralInfo