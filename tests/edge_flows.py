"""Four-round test-only even groups, delayed last player and duplicate request."""
from concurrent_flows import *
def setup(size,group,rounds=4):
    created=req('/api/sessions',dict(session_config_name='rbc_site1_large_high',num_participants=size,modified_session_config_fields={'expected_session_size':size,'group_size':group,'num_rounds':rounds}),True)
    detail=req('/api/sessions/'+created['code'],api=True)
    codes=[p['code'] for p in detail['participants']]
    for c in codes: req('/api/participant_vars/'+c,{'vars':{'paid_round':1}},True)
    states=burst([lambda c=c:req('/InitializeParticipant/'+c) for c in codes])[0]
    states=reach(states,'Welcome'); states=move(states,{}); states=move(states,{}); states=move(states,quiz)
    return created,codes,states
if __name__=='__main__':
    report=[]
    for size,group in [(4,4),(15,15),(15,5)]:
        created,codes,states=setup(size,group)
        rows=[]
        for rn in range(1,5):
            xs=([10]*size if rn==1 else ([0,50,51,100] if size==4 else [0,50,50,50,100]*3) if rn==2 else [0]*size if rn==3 else [100]*size)
            last=states[-1]
            states1,timing=burst([lambda s=s,x=x:req(s['url'],{'x_choice':x}) for s,x in zip(states[:-1],xs[:-1])])
            # Large/even groups must wait for missing final member.
            if group==size: assert all(s['page']=='WaitForGroup' for s in states1)
            else:
                time.sleep(.1)
                refreshed=burst([lambda s=s:req(s['url']) for s in states1])[0]
                assert sum(s['page']=='Results' for s in refreshed)==10
                assert sum(s['page']=='WaitForGroup' for s in refreshed)==4
            # Duplicate same-page POST should not advance two pages or book twice.
            duplicate,_=burst([lambda:req(last['url'],{'x_choice':xs[-1]}) for _ in range(2)])
            states=reach(states1+[duplicate[0]],'Results')
            if size==4 and rn==2:
                assert all('50.5' in s['html'] for s in states)
            rows.append({'round':rn,'choices':xs,'median':statistics.median(xs),'delayed_last_pass':True,'duplicate_post_pass':True})
            states=move(states,{})
        states=move(states,survey)
        assert all(s['page']=='Payment' and '64.75' in s['html'] and '99.500' in s['html'] for s in states)
        report.append({'code':created['code'],'size':size,'group':group,'participants':codes,'rounds':rows,'payment':64.75})
        print(created['code'],'edges PASS',flush=True)
    (OUT/'edges.json').write_text(json.dumps(report,indent=2))
