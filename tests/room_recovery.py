"""Room label and same-identity re-entry checks; prepare restart checkpoints."""
from acceptance_edges import *
from concurrent_flows import OUT
# No session has been assigned to the dedicated local room yet.
waiting=req('/room/china_lab?participant_label=Seat01')
assert 'Waiting for your session' in waiting['html'] or '请等待' in waiting['html']
created=req('/api/sessions',dict(session_config_name='rbc_site1_large_low_belief',num_participants=15,room_name='china_lab'),True)
labels=['Seat%02d'%i for i in range(1,16)]
states=burst([lambda l=l:req('/room/china_lab?participant_label='+l) for l in labels])[0]
states=reach(states,'Welcome')
codes=[s['url'].split('/p/')[1].split('/')[0] for s in states]
assert len(set(codes))==15
again=burst([lambda l=l:req('/room/china_lab?participant_label='+l) for l in labels])[0]
assert [s['url'].split('/p/')[1].split('/')[0] for s in again]==codes
invalid=req('/room/china_lab?participant_label=Seat99')
assert '/p/' not in invalid['url']
release(created['code']);states=burst([lambda s=s:req(s['url']) for s in states])[0]
states=move(states,{});states=move(states,quiz);states=move(states,{'belief_median':50})
# One missing participant remains at Choice; others wait with saved decisions.
ready=move(states[:-1],{'x_choice':10});assert all(s['page']=='WaitForGroup' for s in ready)
checkpoint={'code':created['code'],'participants':codes,'labels':labels,'states':ready+[states[-1]],'phase':'before_restart','checks':['room_before_session_wait','all_15_distinct_labels','same_label_same_participant','invalid_label_rejected','submitted_14_waiting_missing_1']}
(OUT/'room_restart.json').write_text(json.dumps(checkpoint,indent=2));print('ROOM CHECKS PASS; RESTART CHECKPOINT READY',flush=True)
