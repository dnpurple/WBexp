# ret/tests.py
from otree.api import Bot, Submission
from . import *      # brings your Page classes into scope
import random

class PlayerBot(Bot):
    def play_round(self):
        # Round 1 starts with this page in your page_sequence
        if self.round_number == 1:
            yield YourRoleIs

        # Real-effort page (live). No form fields -> just advance.
        # check_html=False avoids brittle HTML checks on a dynamic page.
        yield Submission(RET, check_html=False)

        # Points are computed here; no inputs needed.
        yield RETResults

        # Global wait to re-pair etc.
        yield BeforeDecisionsWaitPage

        # --- Decisions by role ---

        # Manager decision page (group-level form).
        if self.player.id_in_group == 2:
            # choose a consistent, valid combo
            take = random.random() < 0.5
            if take:
                pct = random.choice([10, 20, 30, 40, 50])  # 1..50 allowed
                offer = random.random() < 0.5
                yield ManagerDecisionPage, dict(
                    wants_to_take=True,
                    percentage_taken=pct,
                    wants_to_pay_transfer=offer,
                )
            else:
                # If not taking, your error_message forbids offering a transfer
                yield ManagerDecisionPage, dict(
                    wants_to_take=False,
                    percentage_taken=0,
                    wants_to_pay_transfer=False,
                )

        # Worker thresholds (group-level form)
        if self.player.id_in_group == 1:
            # Any 1..50 are fine; your code handles None by randomizing, but we’ll be explicit.
            yield WorkerPage, dict(
                min_report_percentage_other_worker=25,
                min_report_percentage_self=25,
            )

        # Authority acceptance toggle (group-level form)
        if self.player.id_in_group == 3:
            # Either True or False is valid regardless of whether a transfer was actually offered
            yield AuthorityPage, dict(authority_accepted_transfer=random.choice([True, False]))

        # Payoffs computed here (your WaitPage calls set_payoffs)
        yield ResultsWaitPage

        # Display pages
        yield DecisionResults
        yield RoundResults

        # Treatment-change announcement appears only on round 9 (SWITCH_ROUND - 1)
        if self.round_number == C.SWITCH_ROUND - 1:
            yield TreatmentChangeAnnouncement

        # End-of-experiment only on last round
        if self.round_number == C.NUM_ROUNDS:
            yield RandomRoundWaitPage
            yield RandomRoundPayment

