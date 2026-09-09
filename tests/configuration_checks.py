"""Run against a separate disposable ORM database, not the web server's DB."""
from otree.database import init_orm,db
init_orm()
from otree.session import create_session
import rbc,json,os
from pathlib import Path
cases=[({'num_rounds':0},15),({'num_rounds':21},15),({'num_rounds':1.5},15),({'num_rounds':True},15),({'group_size':4},15),({'group_size':7},15),({'group_size':0},15),({'group_size':-5},15),({'group_size':'5'},15),({'group_sizes':[5,5]},15),({},14),({},16),({'penalty':-1},15),({'real_world_currency_per_point':0},15)]
result=[]
for cfg,n in cases:
 try:create_session('rbc_site1_small_low',num_participants=n,modified_session_config_fields=cfg)
 except RuntimeError as e: db.rollback();result.append({'config':cfg,'participants':n,'rejected':True,'reason':str(e)})
 else:raise AssertionError(cfg)
for rn in [1,20]:
 s=create_session('rbc_site1_small_low',num_participants=15,modified_session_config_fields={'num_rounds':rn})
 sub=rbc.Subsession.objects_get(session=s,round_number=rn)
 assert all(rbc.Survey.is_displayed(p) and rbc.Payment.is_displayed(p) for p in sub.get_players())
 assert all(1<=p.participant.paid_round<=rn for p in sub.get_players())
out=Path(os.environ.get('QA_OUTPUT_DIR','tmp/qa_results'));out.mkdir(parents=True,exist_ok=True)
(out/'configuration.json').write_text(json.dumps({'invalid_cases':result,'valid_rounds':[1,20],'status':'PASS'},indent=2));print('CONFIGURATION CHECKS PASS')
