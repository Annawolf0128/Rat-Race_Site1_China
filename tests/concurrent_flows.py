"""Local-only HTTP integration/load test. Start disposable server on port 8020."""
import urllib.request, urllib.parse, json, time, threading, statistics, os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
BASE='http://localhost:8020'
OUT=Path(os.environ.get('QA_OUTPUT_DIR','tmp/qa_results'))
OUT.mkdir(parents=True,exist_ok=True)
def req(path,data=None,api=False):
    payload=(json.dumps(data).encode() if api else urllib.parse.urlencode(data).encode()) if data is not None else None
    request=urllib.request.Request(path if path.startswith('http') else BASE+path,data=payload,headers={'Content-Type':'application/json' if api else 'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(request,timeout=30) as r:
        body=r.read().decode(); url=r.url
    return json.loads(body) if api else {'url':url,'html':body,'page':url.split('/')[-2]}
def burst(jobs):
    barrier=threading.Barrier(len(jobs)); starts=[]; elapsed=[]
    def run(job):
        barrier.wait(); start=time.perf_counter(); starts.append(start)
        result=job(); elapsed.append(time.perf_counter()-start); return result
    with ThreadPoolExecutor(max_workers=len(jobs)) as pool: results=list(pool.map(run,jobs))
    return results,{'clients':len(jobs),'start_spread_ms':round((max(starts)-min(starts))*1000,2),'max_seconds':round(max(elapsed),3)}
def move(states,data): return burst([lambda s=s:req(s['url'],data) for s in states])[0]
def reach(states,target):
    deadline=time.monotonic()+30
    while any(s['page']!=target for s in states):
        assert time.monotonic()<deadline, [(s['page'],s['url']) for s in states]
        assert all(s['page'] in [target,'GroupFormationWaitPage','WaitForGroup'] for s in states),[(s['page'],s['html'][:200]) for s in states]
        states=burst([lambda s=s:req(s['url']) if s['page']!=target else s for s in states])[0]
        time.sleep(.03)
    return states
quiz=dict(quiz_match_median='no_penalty',quiz_cost='higher',quiz_equal_earnings='no_penalty_formula',quiz_below_earnings='penalty_formula',quiz_fixed_penalty='fixed')
survey=dict(survey_risk=5,survey_use_median='sometimes',survey_median_importance='somewhat',survey_use_prior_medians='sometimes',survey_prior_medians_importance='somewhat',survey_strategy='Synthetic regression test',survey_best='all_zero',survey_best_other='',survey_prior_bc='no',survey_game_theory='no',survey_gender='prefer_not',survey_age='25')
if __name__ == '__main__':
    configs=req('/api/session_configs',api=True)
    report=[]
    for cfg in configs:
        created=req('/api/sessions',dict(session_config_name=cfg['name'],num_participants=15),True)
        detail=req('/api/sessions/'+created['code'],api=True)
        codes=[p['code'] for p in detail['participants']]
        states=burst([lambda c=c:req('/InitializeParticipant/'+c) for c in codes])[0]
        states=reach(states,'Welcome'); states=move(states,{})
        assert all(s['page']=='Instructions' for s in states)
        states=move(states,{}); states=move(states,quiz)
        rounds=[]
        for rn in range(1,21):
            if cfg.get('elicit_belief'): states=move(states,{'belief_median':50})
            assert all(s['page']=='Choice' for s in states),[s['page'] for s in states]
            xs=([10]*15 if rn==1 else [0]*15 if rn==2 else [100]*15 if rn==3 else [0,50,50,50,100]*3 if rn==4 else [0,50,51,99,100]*3)
            states,timing=burst([lambda s=s,x=x:req(s['url'],{'x_choice':x}) for s,x in zip(states,xs)])
            states=reach(states,'Results'); rounds.append(timing)
            states=move(states,{})
        assert all(s['page']=='Survey' for s in states)
        states=move(states,survey)
        assert all(s['page']=='Payment' for s in states),[s['page'] for s in states]
        for _ in range(3): states=burst([lambda s=s:req(s['url']) for s in states])[0]
        row={'config':cfg['name'],'code':created['code'],'participants':codes,'rounds':rounds,'all_reached_payment':True}
        report.append(row); (OUT/'concurrent.json').write_text(json.dumps(report,indent=2))
        print(cfg['name'],created['code'],'PASS',flush=True)
