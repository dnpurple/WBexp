# ret/tests.py
from otree.api import Bot, Submission
from . import (
    C, YourRoleIs, RET, RETResults,
    ManagerDecisionPage, WorkerPage, AuthorityPage,
    DecisionResults, RoundResults, TreatmentChangeAnnouncement,
    RandomRoundPayment
)
import random


class PlayerBot(Bot):
    def play_round(self):

        # Only round 1 shows this in your app
        if self.round_number == 1:
            yield YourRoleIs

        # Live RET page: just advance; no form fields. Avoid brittle HTML checks.
        yield Submission(RET, check_html=False)

        # RET results page (no inputs)
        yield RETResults

        # --- Role-specific decision pages (no WaitPages should be yielded) ---

        # Manager (id_in_group == 2)
        if self.player.id_in_group == 2:
            take = random.random() < 0.5
            if take:
                yield ManagerDecisionPage, dict(
                    wants_to_take=True,
                    percentage_taken=random.choice([10, 20, 30, 40, 50]),  # 1..50 required if taking
                    wants_to_pay_transfer=random.choice([True, False]),
                )
            else:
                # If not taking, transfer must be False and percentage 0 to satisfy your validator
                yield ManagerDecisionPage, dict(
                    wants_to_take=False,
                    percentage_taken=0,
                    wants_to_pay_transfer=False,
                )

        # Worker thresholds (id_in_group == 1)
        if self.player.id_in_group == 1:
            yield WorkerPage, dict(
                min_report_percentage_other_worker=25,
                min_report_percentage_self=25,
            )

        # Authority toggle (id_in_group == 3)
        if self.player.id_in_group == 3:
            yield AuthorityPage, dict(
                authority_accepted_transfer=random.choice([True, False])
            )

        # Results pages (no inputs)
        yield DecisionResults
        yield RoundResults

        # Treatment change announcement appears on round SWITCH_ROUND-1 (== 9)
        if self.round_number == C.SWITCH_ROUND - 1:
            yield TreatmentChangeAnnouncement

        # End-of-experiment payment page (no WaitPage yield)
        if self.round_number == C.NUM_ROUNDS:
            yield RandomRoundPayment


