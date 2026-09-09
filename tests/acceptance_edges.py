"""Odd-group acceptance: entry, release, validation, waits, stale requests."""
from concurrent_flows import *
import urllib.error, re, random

def expect_status(fn,status):
    try: fn()
    except urllib.error.HTTPError as e: assert e.code==status,(e.code,status)
    else: raise AssertionError('Expected HTTP '+str(status))
def create(cfg):
    created=req('/api/sessions',dict(session_config_name=cfg['name'],num_participants=15),True)
    codes=[p['code'] for p in req('/api/sessions/'+created['code'],api=True)['participants']]
    return created['code'],codes

def finish(states,cfg,start=1):
    for rn in range(start,21):
        if cfg.get('elicit_belief'): states=move(states,{'belief_median':rn})
        states=move(states,{'x_choice':10 if rn==1 else rn*5%101})
        states=reach(states,'Results'); states=move(states,{})
    states=move(states,survey)
    assert all(s['page']=='Payment' for s in states)
    return states

if __name__=='__main__':
    results=[]
    for cfg in req('/api/session_configs',api=True):
        code,codes=create(cfg); checks=[]; n=cfg['group_size']
        early=burst([lambda c=c:req('/InitializeParticipant/'+c) for c in codes[:n-1]])[0]
        assert all(s['page']=='GroupFormationWaitPage' for s in early)
        early=burst([lambda s=s:req(s['url']) for s in early])[0]
        assert all(s['page']=='GroupFormationWaitPage' for s in early); checks.append('group_formation_wait_and_refresh')
        states=burst([lambda c=c:req('/InitializeParticipant/'+c) for c in codes])[0]
        states=reach(states,'Welcome')
        assert req(states[0]['url'],{})['page']=='Welcome'; checks.append('welcome_cannot_self_release')
        # Remain at Welcome long enough for the background wait task (>10 s).
        time.sleep(13)
        assert all(s['page']=='Welcome' for s in burst([lambda s=s:req(s['url']) for s in states])[0])
        checks.append('welcome_long_wait_no_auto_start')
        release(code); states=burst([lambda s=s:req(s['url']) for s in states])[0]
        assert all(s['page']=='Instructions' for s in states); checks.append('admin_release_all')
        assert all(str(cfg['penalty']) in s['html'] for s in states)
        states=move(states,{})
        bad=dict(quiz,quiz_match_median='penalty'); response=req(states[0]['url'],bad)
        assert response['page']=='Quiz' and '第 1 题答错了' in response['html']
        for field,val in quiz.items():
            expected='penalty' if field=='quiz_match_median' else val
            inputs=re.findall(r'<input\b[^>]*>',response['html'])
            assert any('name="'+field+'"' in x and 'value="'+expected+'"' in x and 'checked' in x for x in inputs),field
        checks.append('wrong_quiz_rejected_all_answers_retained')
        expect_status(lambda:req(states[0]['url'],{'timeout_happened':'1'}),409)
        assert req(states[0]['url'])['page']=='Quiz';checks.append('forced_quiz_blocked')
        states=move(states,quiz)
        if cfg.get('elicit_belief'):
            for value in ['',-1,101,'1.5']:
                assert req(states[0]['url'],{'belief_median':value})['page']=='Belief'
            expect_status(lambda:req(states[0]['url'],{'timeout_happened':'1'}),409)
            states=move(states,{'belief_median':50}); checks.append('belief_validation_and_force_guard')
        for value in ['',-1,101,'1.5']:
            assert req(states[0]['url'],{'x_choice':value})['page']=='Choice'
        expect_status(lambda:req(states[0]['url'],{'timeout_happened':'1'}),409)
        # Authenticated administrator endpoint also must not advance unanswered choices.
        release(code)
        assert all(s['page']=='Choice' for s in burst([lambda s=s:req(s['url']) for s in states])[0])
        checks.append('choice_validation_admin_force_blocked')
        old=states[-1]['url']
        ready=move(states[:-1],{'x_choice':10})
        ready=burst([lambda s=s:req(s['url']) for s in ready])[0]
        if n==15: assert all(s['page']=='WaitForGroup' for s in ready)
        else: assert sum(s['page']=='Results' for s in ready)==10 and sum(s['page']=='WaitForGroup' for s in ready)==4
        time.sleep(13)
        assert req(old)['page']=='Choice'
        last=req(old,{'x_choice':10}); states=reach(ready+[last],'Results')
        assert all('99.500' in s['html'] for s in states)
        checks.append('delayed_last_and_independent_groups')
        # Replay a different value against an already completed Choice URL.
        assert req(old,{'x_choice':100})['page']=='Results'
        assert '99.500' in req(states[-1]['url'])['html']; checks.append('stale_choice_cannot_overwrite')
        states=move(states,{})
        for rn in range(2,21):
            if cfg.get('elicit_belief'): states=move(states,{'belief_median':50})
            xs=([0]*15 if rn==2 else [100]*15 if rn==3 else [0,50,50,50,100]*3 if rn==4 else [random.Random(rn*100+i).randrange(101) for i in range(15)])
            states=burst([lambda s=s,x=x:req(s['url'],{'x_choice':x}) for s,x in zip(states,xs)])[0]
            states=reach(states,'Results'); states=move(states,{})
        assert all(s['page']=='Survey' for s in states)
        assert req(states[0]['url'],{})['page']=='Survey'
        assert req(states[0]['url'],dict(survey,survey_best='other',survey_best_other=' '))['page']=='Survey'
        expect_status(lambda:req(states[0]['url'],{'timeout_happened':'1'}),409)
        one=req(states[0]['url'],dict(survey,survey_best='other',survey_best_other='有效的测试说明'))
        assert one['page']=='Payment' and req(states[1]['url'])['page']=='Survey'
        states=[one]+move(states[1:],survey)
        for _ in range(5): states=burst([lambda s=s:req(s['url']) for s in states])[0]
        assert all(s['page']=='Payment' for s in states)
        checks+=['survey_required_and_other_branch','payment_independent_of_other_surveys','payment_refresh']
        results.append({'config':cfg['name'],'code':code,'participants':codes,'checks':checks})
        (OUT/'acceptance_edges.json').write_text(json.dumps(results,indent=2));print(cfg['name'],code,'ALL EDGES PASS',flush=True)
