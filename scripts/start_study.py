"""Start the pinned oTree runtime and stop its timeout worker together."""
import argparse,os,signal,subprocess,sys
from pathlib import Path
from importlib.metadata import version

def validate_environment(env):
    if version('otree')!='5.11.5': raise RuntimeError('请安装 requirements.txt 中已验收的 oTree 5.11.5。')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--host',default='0.0.0.0');parser.add_argument('--port',type=int,default=8000);args=parser.parse_args()
    env=os.environ.copy()
    # This launcher deliberately uses oTree's default SQLite database.
    env.pop('DATABASE_URL', None)
    try:validate_environment(env)
    except RuntimeError as exc:parser.exit(1,str(exc)+'\n')
    # Local lab mode: open administrator pages without a login.
    env.pop('OTREE_AUTH_LEVEL', None)
    env['OTREE_PRODUCTION']='1'
    executable=str(Path(sys.executable).with_name('otree.exe' if os.name=='nt' else 'otree'))
    # Ensure oTree's own child process uses the same virtual environment.
    env['PATH']=str(Path(sys.executable).parent)+os.pathsep+env.get('PATH','')
    child=subprocess.Popen([executable,'prodserver',f'{args.host}:{args.port}'],cwd=Path(__file__).resolve().parents[1],env=env,start_new_session=os.name!='nt')
    def stop(*_):
        if os.name=='nt':
            if child.poll() is None: subprocess.run(['taskkill','/PID',str(child.pid),'/T','/F'],stdout=subprocess.DEVNULL)
        else:
            # The worker may remain after an unexpected server exit.
            try:os.killpg(child.pid,signal.SIGTERM)
            except ProcessLookupError:pass
    signal.signal(signal.SIGTERM,stop)
    try:return child.wait()
    except KeyboardInterrupt:stop();return child.wait()
    finally:stop()

if __name__=='__main__':sys.exit(main())
