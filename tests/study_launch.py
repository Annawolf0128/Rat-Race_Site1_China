"""Exercise the actual production launcher on a dedicated PostgreSQL database."""
import os,sys,subprocess,secrets,time,urllib.request,urllib.parse,urllib.error,http.cookiejar,re,json
from pathlib import Path
out=Path(os.environ.get('QA_OUTPUT_DIR','tmp/qa_results'));out.mkdir(parents=True,exist_ok=True)
env=os.environ.copy();env.update(DATABASE_URL='postgresql://rabbit@127.0.0.1:55432/china_qa_auth',OTREE_ADMIN_PASSWORD=secrets.token_urlsafe(24),OTREE_SECRET_KEY=secrets.token_urlsafe(40))
# Test refusal of missing/SQLite production configuration without starting a server.
from importlib.util import spec_from_file_location,module_from_spec
spec=spec_from_file_location('study_launcher','scripts/start_study.py');m=module_from_spec(spec);spec.loader.exec_module(m)
for bad in [{},dict(env,DATABASE_URL='sqlite:///db.sqlite3')]:
 try:m.validate_environment(bad)
 except RuntimeError:pass
 else:raise AssertionError('Unsafe launch accepted')
log=(out/'study_launcher.log').open('w')
proc=subprocess.Popen([sys.executable,'scripts/start_study.py','--host','127.0.0.1','--port','8022'],env=env,stdout=log,stderr=subprocess.STDOUT)
base='http://localhost:8022'
try:
 for _ in range(40):
  try:
   with urllib.request.urlopen(base+'/login',timeout=1) as r: r.read()
   break
  except (urllib.error.URLError,TimeoutError):time.sleep(.25)
 else:raise AssertionError('Study server did not start')
 for path in ['/sessions','/export','/demo']:
  with urllib.request.urlopen(base+path) as r:assert '/login' in r.url
 try:urllib.request.urlopen(base+'/api/sessions')
 except urllib.error.HTTPError as e:assert e.code==403
 else:raise AssertionError('Anonymous API allowed')
 opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
 with opener.open(base+'/login') as r:html=r.read().decode()
 token=re.search(r'name="csrftoken"[^>]*value="([^"]+)"',html).group(1)
 with opener.open(base+'/login',urllib.parse.urlencode({'csrftoken':token,'username':'admin','password':env['OTREE_ADMIN_PASSWORD']}).encode()) as r:
  assert '/login' not in r.url
 with opener.open(base+'/sessions') as r:assert '/login' not in r.url
 with urllib.request.urlopen(base+'/room/china_lab?participant_label=Seat01') as r:
  html=r.read().decode();assert 'Debug info' not in html and '/login' not in r.url
 result={'status':'PASS','checks':['missing_config_refused','sqlite_refused','launcher_uses_study_mode','anonymous_admin_redirected','anonymous_api_forbidden','admin_login_success','participant_room_accessible','debug_hidden']}
finally:
 proc.terminate();proc.wait(timeout=15);log.close()
try:urllib.request.urlopen(base+'/login',timeout=1)
except urllib.error.URLError:result['checks'].append('launcher_stopped_server')
else:raise AssertionError('Server left running')
(out/'study_launch.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
