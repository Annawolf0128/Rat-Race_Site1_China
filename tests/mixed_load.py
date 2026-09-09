"""60 simultaneous decisions across four full sessions with a fifth idle session."""
from acceptance_edges import *
configs={c['name']:c for c in req('/api/session_configs',api=True)}
idle_cfg=configs['rbc_site1_small_low']; idle_code,idle_codes=create(idle_cfg)
idle=reach(burst([lambda c=c:req('/InitializeParticipant/'+c) for c in idle_codes])[0],'Welcome')
runs=[]; states=[]
for name in ['rbc_site1_large_low','rbc_site1_large_low','rbc_site1_large_high','rbc_site1_large_high']:
 cfg=configs[name];code,codes=create(cfg)
 ss=reach(burst([lambda c=c:req('/InitializeParticipant/'+c) for c in codes])[0],'Welcome')
 release(code);ss=burst([lambda s=s:req(s['url']) for s in ss])[0]
 ss=move(ss,{});ss=move(ss,quiz)
 states+=ss;runs.append({'config':name,'code':code,'participants':codes})
# Explicitly overlap background tasks for the idle Welcome participants.
time.sleep(15)
timings=[]
for rn in range(1,21):
 xs=[(rn*13+i*7)%101 for i in range(60)]
 states,t=burst([lambda s=s,x=x:req(s['url'],{'x_choice':x}) for s,x in zip(states,xs)])
 states=reach(states,'Results');timings.append(t)
 if rn==10: time.sleep(15)
 states=move(states,{})
states=move(states,survey);assert all(s['page']=='Payment' for s in states)
assert all(req(s['url'])['page']=='Welcome' for s in idle)
release(idle_code);idle=burst([lambda s=s:req(s['url']) for s in idle])[0]
idle=move(idle,{});idle=move(idle,quiz);finish(idle,idle_cfg)
runs.append({'config':idle_cfg['name'],'code':idle_code,'participants':idle_codes})
(OUT/'mixed_load.json').write_text(json.dumps({'sessions':runs,'choice_bursts':timings,'all_reached_payment':True},indent=2))
print('60 CLIENTS + IDLE SESSION: PASS',flush=True)
