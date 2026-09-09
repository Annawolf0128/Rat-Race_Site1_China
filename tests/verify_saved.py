"""Read-only assertions after the local QA server has been stopped."""
import base64,json,pickle,sqlite3,statistics,os
from decimal import Decimal
from pathlib import Path
out=Path(os.environ.get('QA_OUTPUT_DIR','tmp/qa_results'))
conn=sqlite3.connect('file:db.sqlite3?mode=ro',uri=True); conn.row_factory=sqlite3.Row
runs=json.loads((out/'concurrent.json').read_text())+json.loads((out/'edges.json').read_text())
if (out/'browser_run.json').exists(): runs.append(json.loads((out/'browser_run.json').read_text()))
results=[]
for run in runs:
    session=conn.execute('select * from otree_session where code=?',(run['code'],)).fetchone()
    cfg=pickle.loads(base64.b64decode(session['config']))
    nrounds=cfg.get('num_rounds',20)
    participants=conn.execute('select * from otree_participant where session_id=?',(session['id'],)).fetchall()
    rows=conn.execute('select * from rbc_player where session_id=? and round_number<=?',(session['id'],nrounds)).fetchall()
    assert all(p['_current_page_name']=='Payment' for p in participants)
    matrix=None
    for rn in range(1,nrounds+1):
        rr=[r for r in rows if r['round_number']==rn]
        groups={r['group_id'] for r in rr}
        members=sorted(sorted(r['participant_id'] for r in rr if r['group_id']==g) for g in groups)
        assert all(len(m)==cfg['group_size'] for m in members)
        assert matrix is None or matrix==members
        matrix=members
        for g in groups:
            gr=[r for r in rr if r['group_id']==g]
            median=statistics.median(r['x_choice'] for r in gr)
            assert conn.execute('select median_x from rbc_group where id=?',(g,)).fetchone()[0]==median
            for r in gr:
                pen=cfg['penalty'] if r['x_choice']<median else 0
                assert r['penalty_paid']==pen
                expected=Decimal(100)-Decimal(r['x_choice']**2)/200-pen
                assert Decimal(str(r['round_payoff']))==expected
                assert (r['belief_median'] is not None)==bool(cfg.get('elicit_belief'))
    for p in participants:
        paid=pickle.loads(base64.b64decode(p['_vars']))['paid_round']
        rr=[r for r in rows if r['participant_id']==p['id']]
        selected=next(r for r in rr if r['round_number']==paid)
        assert Decimal(str(p['payoff']))==Decimal(str(selected['round_payoff']))
        assert sum(Decimal(str(r['_payoff'])) for r in rr)==Decimal(str(p['payoff']))
        assert all(Decimal(str(r['_payoff']))==0 for r in rr if r['round_number']!=nrounds)
    results.append({'code':run['code'],'decisions_verified':len(rows),'participants_at_payment':len(participants),'fixed_groups':True,'stored_payment_exact':True})
(out/'verified.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results))
