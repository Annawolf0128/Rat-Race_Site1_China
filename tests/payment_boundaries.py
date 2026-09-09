"""Run only against a disposable oTree database, from project root."""
import json, statistics, os
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from types import SimpleNamespace
from otree.database import init_orm, db
init_orm()
from otree.session import create_session
from otree import settings
import rbc
from otree.forms.forms import get_form
from starlette.datastructures import FormData
s = create_session('rbc_site1_large_low', num_participants=15)
first = rbc.Subsession.objects_get(session=s, round_number=1)
p = first.get_players()[0].in_round(20)
p.participant.paid_round = 1
selected = p.in_round(1)
checks = 0
examples = []
for penalty in [20,40]:
    for x in range(101):
        for penalized in [False,True]:
            expected = Decimal(100)-Decimal(x*x)/200-(penalty if penalized else 0)
            selected.round_payoff = float(expected)
            rbc.settle_payment(p)
            assert Decimal(p.payoff) == expected
            assert Decimal(p.participant.payoff) == expected
            for repeat in range(3):
                rbc.settle_payment(p)
                shown = rbc.Payment.vars_for_template(p)
                assert Decimal(p.participant.payoff) == expected
                assert Decimal(shown['total']) == Decimal(p.participant.payoff_plus_participation_fee())
                cash = (expected * Decimal('0.5')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) + Decimal(15)
                assert Decimal(shown['total']) == cash
            checks += 1
            if penalty==20 and not penalized and x in [10,45,99]:
                examples.append(dict(x=x, points=str(expected), total=shown['total']))
# Actual payoff routine with independently calculated medians, using odd groups.
cases = [[0]*5,[100]*15,[10]*15,[0,50,50,50,100],[0,49,50,51,100]]
for xs in cases:
    players = [SimpleNamespace(x_choice=x) for x in xs]
    group = SimpleNamespace(get_players=lambda:players, session=SimpleNamespace(config={'penalty':40}))
    rbc.set_payoffs(group)
    assert group.median_x == statistics.median(xs)
    for player,x in zip(players,xs):
        assert player.penalty_paid == (40 if x<statistics.median(xs) else 0)
        assert Decimal(str(player.round_payoff)) == Decimal(100)-Decimal(x*x)/200-Decimal(str(player.penalty_paid))
for field in ['x_choice','belief_median']:
    for raw in ['', '-1','101','1.5','0','50','100']:
        form=get_form(p,[field],SimpleNamespace(),FormData({field:raw}))
        assert form.validate() == (raw in ['0','50','100'])
# Paid round selection, not sum of all rounds.
for rn in [1,10,20]:
    for q in p.in_all_rounds(): q.round_payoff=float(Decimal(100)-Decimal(q.round_number)/200)
    p.participant.paid_round=rn
    rbc.settle_payment(p)
    assert Decimal(p.participant.payoff)==Decimal(100)-Decimal(rn)/200
    old=Decimal(p.participant.payoff)
    for _ in range(100): rbc.Payment.vars_for_template(p)
    assert Decimal(p.participant.payoff)==old
result={'payment_cases':checks,'median_cases':cases,'refreshes_per_selected_round':100,'examples':examples,'status':'passed'}
out=Path(os.environ.get('QA_OUTPUT_DIR','tmp/qa_results')); out.mkdir(parents=True,exist_ok=True)
(out/'boundaries.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
