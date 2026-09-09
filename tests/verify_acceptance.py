"""Verify completed acceptance sessions through PostgreSQL and HTTP CSV exports."""
from concurrent_flows import *
from decimal import Decimal
import psycopg2,psycopg2.extras,base64,pickle,csv,io,re
conn=psycopg2.connect(os.environ['DATABASE_URL']);conn.set_session(readonly=True,autocommit=True)
cur=conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
runs=json.loads((OUT/'concurrent.json').read_text())+json.loads((OUT/'acceptance_edges.json').read_text())+json.loads((OUT/'mixed_load.json').read_text())['sessions']+json.loads((OUT/'browser_runs.json').read_text())
if (OUT/'room_restart.json').exists():
 rr=json.loads((OUT/'room_restart.json').read_text())
 if rr['phase']=='completed':runs.append(rr)
if (OUT/'additional.json').exists(): runs+=json.loads((OUT/'additional.json').read_text())
results=[];page_times=list(csv.DictReader(io.StringIO(req('/ExportPageTimes')['html'])))
for run in runs:
 cur.execute('select * from otree_session where code=%s',(run['code'],));session=cur.fetchone()
 cfg=pickle.loads(base64.b64decode(session['config']));rounds=cfg.get('num_rounds',20)
 cur.execute('select * from otree_participant where session_id=%s',(session['id'],));pps=cur.fetchall()
 assert len(pps)==15 and all(p['_current_page_name']=='Payment' and p['_round_number']==20 for p in pps)
 cur.execute('select * from rbc_player where session_id=%s order by round_number,participant_id',(session['id'],));players=cur.fetchall()
 cur.execute('select id,median_x from rbc_group where session_id=%s',(session['id'],));groups={r['id']:r['median_x'] for r in cur.fetchall()}
 assert len(players)==300
 matrix=None;belief_count=0
 for rn in range(1,21):
  pr=[p for p in players if p['round_number']==rn];gids={p['group_id'] for p in pr}
  members=sorted(sorted(p['participant_id'] for p in pr if p['group_id']==gid) for gid in gids)
  assert all(len(m)==cfg['group_size'] for m in members)
  assert matrix is None or matrix==members;matrix=members
  for gid in gids:
   gp=[p for p in pr if p['group_id']==gid];median=statistics.median(p['x_choice'] for p in gp)
   assert median==groups[gid] and int(median)==median
   for p in gp:
    assert type(p['x_choice']) is int and 0<=p['x_choice']<=100
    penalty=cfg['penalty'] if p['x_choice']<median else 0
    expected=Decimal(100)-Decimal(p['x_choice']**2)/200-penalty
    assert Decimal(str(p['round_payoff']))==expected and p['penalty_paid']==penalty
    assert (p['belief_median'] is not None)==bool(cfg.get('elicit_belief'))
    if p['belief_median'] is not None:assert 0<=p['belief_median']<=100;belief_count+=1
    assert p['consent_given'] is None
 paid_rounds=set()
 for pp in pps:
  paid=pickle.loads(base64.b64decode(pp['_vars']))['paid_round'];paid_rounds.add(paid)
  prs=[p for p in players if p['participant_id']==pp['id']];selected=next(p for p in prs if p['round_number']==paid);last=next(p for p in prs if p['round_number']==20)
  events=[e for e in page_times if e['participant_code']==pp['code']]
  content_names=['Welcome','Instructions','Quiz','Belief','Choice','Results','Survey']
  expected_pages=['Welcome','Instructions','Quiz']
  for _ in range(20): expected_pages+=(['Belief'] if cfg.get('elicit_belief') else [])+['Choice','Results']
  expected_pages+=['Survey']
  actual=[e['page_name'] for e in sorted(events,key=lambda e:int(e['page_index'])) if e['page_name'] in content_names]
  assert actual==expected_pages,(run['code'],pp['code'],actual)
  assert all(e['timeout_happened']=='0' or e['page_name']=='Welcome' for e in events)
  assert not any(e['page_name']=='Consent' for e in events)
  assert Decimal(str(pp['payoff']))==Decimal(str(selected['round_payoff']))
  assert sum(Decimal(str(p['_payoff'])) for p in prs)==Decimal(str(pp['payoff']))
  assert all(Decimal(str(p['_payoff']))==0 for p in prs if p['round_number']!=20)
  assert all(last[k] is not None and str(last[k]).strip() for k in survey if k!='survey_best_other')
  if last['survey_best']=='other':assert last['survey_best_other'].strip()
 assert len(paid_rounds)==1
 # Download the actual application CSV endpoint using the token provided by its Data page.
 page=req('/SessionData/'+run['code'])['html'];href=re.search(r'href="(/ExportSessionWide/[^"&]+\?token=[^"&]+)"',page).group(1)
 data=req(href)['html'];csvrows=list(csv.DictReader(io.StringIO(data.lstrip('\ufeff'))));assert len(csvrows)==15
 for row in csvrows:
  pp=next(p for p in pps if p['code']==row['participant.code'])
  assert Decimal(row['participant.payoff'])==Decimal(str(pp['payoff']))
  for rn in range(1,21):assert row[f'rbc.{rn}.player.x_choice']!=''
 (OUT/'exports').mkdir(exist_ok=True);(OUT/'exports'/(run['code']+'.csv')).write_text(data)
 results.append({'code':run['code'],'config':cfg['name'],'participants':15,'choices':300,'beliefs':belief_count,'paid_round':next(iter(paid_rounds)),'fixed_groups':True,'median_penalty_payoff':True,'survey_complete':True,'payment_exact':True,'csv_export_matches_db':True,'page_sequence_verified':True,'no_forced_answers':True})
(OUT/'page_times.csv').write_text(req('/ExportPageTimes')['html'])
(OUT/'verified.json').write_text(json.dumps(results,indent=2));print('VERIFIED',len(results),'sessions',sum(r['choices'] for r in results),'choices')
