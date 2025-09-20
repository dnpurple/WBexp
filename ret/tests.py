# ret/tests.py
from otree.api import Bot, Submission, expect
from . import (
    C,
    RET, RETResults,
    BeforeDecisionsWaitPage,
    ManagerDecisionPage, WorkerPage, AuthorityPage,
    ResultsWaitPage, DecisionResults, RoundResults,
    RandomRoundWaitPage, RandomRoundPayment,
)

class PlayerBot(Bot):
    """
    Bot cycles through scenarios by round_number % 4:
      1: No theft
      2: Theft, no bribe
      3: Theft + bribe (authority accepts on even rounds)
      0: Theft + bribe (authority accepts on even rounds), higher pct

    Worker thresholds are set low (20) so reports will be intended when theft >= 20%.
    """

    def play_round(self):
        p = self.player
        g = p.group

        # --- RET (live page): skip interaction, simulate time-out, but pre-set output fields ---
        # Give predictable productivity so points/payoffs propagate through your pipeline.
        if p.id_in_group == 3:  # Authority gets salary via your page logic
            p.num_solved = 0
        else:
            # rotate 3..5 correct to exercise paycheck math
            p.num_solved = 3 + (p.round_number % 3)

        # Skip the live addition page; timeout is fine for testing the rest of the pipeline
        yield Submission(RET, {}, timeout_happened=True)
        yield RETResults

        # Pairing, state reset, etc.
        yield BeforeDecisionsWaitPage

        # --- Manager decision logic (drives the scenarios we want to test) ---
        # Round pattern for coverage
        rmod = p.round_number % 4

        if p.id_in_group == 2:
            # Manager
            if rmod == 1:
                # No theft; no bribe
                yield ManagerDecisionPage, dict(
                    wants_to_take=False,
                    percentage_taken=0,
                    wants_to_pay_transfer=False,
                )
            elif rmod == 2:
                # Theft, no bribe
                yield ManagerDecisionPage, dict(
                    wants_to_take=True,
                    percentage_taken=30,
                    wants_to_pay_transfer=False,
                )
            elif rmod == 3:
                # Theft + bribe (acceptance handled by Authority on even rounds)
                yield ManagerDecisionPage, dict(
                    wants_to_take=True,
                    percentage_taken=30,
                    wants_to_pay_transfer=True,
                )
            else:
                # Theft + bribe, higher percentage
                yield ManagerDecisionPage, dict(
                    wants_to_take=True,
                    percentage_taken=50,
                    wants_to_pay_transfer=True,
                )

        # --- Worker thresholds (pick values to force report when theft >= 20%) ---
        if p.id_in_group == 1:
            yield WorkerPage, dict(
                min_report_percentage_other_worker=20,
                min_report_percentage_self=20,
            )

        # --- Authority acceptance ---
        # Accept on even rounds; reject on odd rounds.
        if p.id_in_group == 3:
            accept = (p.round_number % 2 == 0)
            yield AuthorityPage, dict(authority_accepted_transfer=accept)

        # Payoff computation happens after this wait page:
        yield ResultsWaitPage

        # Results & bookkeeping pages
        yield DecisionResults
        yield RoundResults

        # Final random payment round machinery
        if p.round_number == C.NUM_ROUNDS:
            yield RandomRoundWaitPage
            yield RandomRoundPayment

        # --- Light sanity checks for the Worker on theft rounds ---
        # (Only run assertions when we are the worker; avoids role-specific coupling.)
        if p.id_in_group == 1:
            theft = bool(getattr(g, 'wants_to_take', False)) and (g.field_maybe_none('percentage_taken') or 0) > 0

            if theft:
                # With thresholds set to 20, intended_to_report should be True for pct >= 20.
                expect(p.intended_to_report, True)

                # If a report was evaluated, your set_payoffs() now stores a punishment_draw.
                # We only check that the draw exists when a report was intended.
                # (If you added the Group.punishment_draw field as we discussed.)
                if hasattr(g, 'punishment_draw'):
                    expect(g.punishment_draw is not None, True)
