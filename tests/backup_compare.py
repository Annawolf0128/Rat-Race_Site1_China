"""Compare a restored QA database against the stopped source database."""
import hashlib,json,os,psycopg2
from pathlib import Path
out=Path(os.environ.get('QA_OUTPUT_DIR','tmp/qa_results'))
tables=['otree_session','otree_participant','rbc_subsession','rbc_group','rbc_player','otree_pagetimebatch']
def snapshot(database):
 conn=psycopg2.connect(host='127.0.0.1',port=55432,dbname=database);conn.set_session(readonly=True,autocommit=True);cur=conn.cursor();result={}
 for table in tables:
  cur.execute('SELECT * FROM '+table+' ORDER BY id');rows=cur.fetchall()
  result[table]={'rows':len(rows),'sha256':hashlib.sha256(json.dumps(rows,default=str,ensure_ascii=False).encode()).hexdigest()}
 conn.close();return result
original=snapshot('china_qa');restored=snapshot('china_qa_restored');assert original==restored
(out/'backup_restore.json').write_text(json.dumps({'status':'PASS','tables':original},indent=2));print('BACKUP RESTORE: six tables identical')
