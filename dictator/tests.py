import dictator as pages
from . import *
c = cu

class PlayerBot(Bot):
    def play_round(self):
        yield Instructions
        if self.player.id_in_group == 1:
            yield Decision, dict(decision=C.ENDOWMENTS)
        yield Results