"""Explicit-target SDK diagnostics, backup and guarded Home routing; no root."""
import argparse,base64,hashlib,ipaddress,json,re,sqlite3,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MODEL='QN55QN90BAFXZA';FIRMWARE='T-PTMAKUC-1720.7';APP='QuietHome1.Home'
DBS=('.pkgmgr_parser.db','.app-context.db','.webappservice.db')
def value(text):
 m=re.search(r'value = (.*?) \(String\)',text)
 if not m:raise ValueError('Unexpected vconf output: '+text)
 return m.group(1)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['doctor','backup','route','restore','status']);p.add_argument('--host',required=True);p.add_argument('--callback',required=True);p.add_argument('--sdb',type=Path,required=True);p.add_argument('--transport-src',type=Path,required=True);p.add_argument('--firmware',required=True,help='Owner declaration from About This TV');p.add_argument('--snapshot',type=Path);p.add_argument('--validated',action='store_true',help='Owner completed all functional tests');a=p.parse_args()
 for ip in (a.host,a.callback):ipaddress.IPv4Address(ip)
 if a.firmware!=FIRMWARE:p.error('Firmware mismatch: investigate a separate profile before mutation')
 devices=subprocess.check_output([str(a.sdb),'devices'],text=True)
 serial=a.host+':26101'
 if not any(line.split()[:3]==[serial,'device',MODEL] for line in devices.splitlines()):p.error('Expected connected model/target absent. Run sdb connect for this explicit host first.')
 sys.path.insert(0,str(a.transport_src.resolve()))
 from samsung_tv_root.sdb import SdbClient
 c=SdbClient(a.sdb,a.host,timeout=10)
 def run(command):
  out=c.capture(command,callback_host=a.callback,timeout=20).output
  if not out.rstrip().endswith('[exit:0]'):raise RuntimeError(out)
  return out.rsplit('\n[exit:',1)[0].strip()
 def pref(key):return value(run('vconftool get '+key))
 if a.action=='doctor':
  print(run('id; uname -srmo; readlink -f /usr/share/dotnet.tizen/netcoreapp; cat /etc/tizen-release; true'))
  print('Home:',pref('db/appfw/home_appid'));print('Startup:',pref('db/appfw/startup_appid'));return
 if a.action in ('backup','route','restore'):
  runtime=run('readlink -f /usr/share/dotnet.tizen/netcoreapp')
  release=run('cat /etc/tizen-release')
  arch=run('uname -m')
  if runtime.rsplit('/',1)[-1]!='3.1.3' or 'Tizen6/TV' not in release or arch!='armv7l':p.error('Runtime/release/architecture mismatch: investigate before mutation')
 if a.action=='backup':
  phase=datetime.now(timezone.utc).strftime('qn90b-%Y%m%dT%H%M%SZ');local=ROOT/'.local/backups'/phase;local.mkdir(parents=True,exist_ok=False)
  remote='/home/owner/share/tmp/sdk_tools/'+phase;run('umask 077; mkdir '+remote)
  metadata={'host':a.host,'callback':a.callback,'model':MODEL,'firmware':a.firmware,'remote':remote,'home':pref('db/appfw/home_appid'),'startup':pref('db/appfw/startup_appid'),'files':[]}
  for name in DBS:
   target=remote+'/'+name;run('sqlite3 -readonly /opt/dbspace/'+name+' "'+".backup '"+target+"'"+'"')
   if run('sqlite3 -readonly '+target+" 'PRAGMA quick_check;'")!='ok':raise RuntimeError('TV backup corrupt')
   size=int(run('wc -c < '+target));digest=run('sha256sum '+target).split()[0];data=bytearray()
   for n in range((size+262143)//262144):data.extend(base64.b64decode(run('dd if='+target+' bs=262144 skip='+str(n)+' count=1 2>/dev/null | base64')))
   if len(data)!=size or hashlib.sha256(data).hexdigest()!=digest:raise RuntimeError('Backup transfer mismatch')
   (local/name).write_bytes(data)
   with sqlite3.connect((local/name).as_uri()+'?mode=ro',uri=True) as db:
    if db.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise RuntimeError('Local backup corrupt')
   metadata['files'].append({'name':name,'sha256':digest,'bytes':size});(local/'manifest.json').write_text(json.dumps(metadata,indent=2))
  print('Verified snapshot:',local);return
 if not a.snapshot:p.error('--snapshot is required; use a fresh verified backup')
 snapshot=a.snapshot.resolve();meta=json.loads((snapshot/'manifest.json').read_text())
 if (meta['host'],meta['model'],meta['firmware'])!=(a.host,MODEL,FIRMWARE):p.error('Snapshot target mismatch')
 if {f['name'] for f in meta['files']}!=set(DBS):p.error('Incomplete backup')
 for f in meta['files']:
  if hashlib.sha256((snapshot/f['name']).read_bytes()).hexdigest()!=f['sha256']:p.error('Snapshot hash mismatch')
 remote=meta['remote']
 for n in ('Routing.dll','Routing.deps.json','Routing.runtimeconfig.json'):
  data=(ROOT/'.local/build/Routing'/n).read_bytes();run("printf %s '"+base64.b64encode(data).decode()+"' | base64 -d > "+remote+'/'+n)
  if run('sha256sum '+remote+'/'+n).split()[0]!=hashlib.sha256(data).hexdigest():raise RuntimeError('Helper hash mismatch')
 def operation():
  out=run('/usr/bin/dotnet '+remote+'/Routing.dll')
  m=re.fullmatch(r'get_result=0 home=(\S+)',out)
  if not m:raise RuntimeError('Unexpected handler response: '+out)
  return m.group(1)
 def set_operation(expected,target):return run('/usr/bin/dotnet '+remote+'/Routing.dll set '+expected+' '+target)
 def set_pref(key,target):
  if not re.fullmatch(r'[A-Za-z0-9_.-]+',target):raise ValueError('Invalid saved app ID')
  run('vconftool set -f -t string '+key+' '+target)
  if pref(key)!=target:raise RuntimeError('Preference readback mismatch')
 state={'operation':operation(),'home':pref('db/appfw/home_appid'),'startup':pref('db/appfw/startup_appid')}
 print(json.dumps(state,indent=2))
 if a.action=='status':return
 saved=snapshot/'routing-before.json'
 if a.action=='route':
  if not a.validated:p.error('Complete owner functional tests before --validated')
  if saved.exists():p.error('Routing phase already exists; inspect it or take a new snapshot')
  if state['operation']!='com.samsung.tv.csfs' or state['home']!=meta['home'] or state['startup']!=meta['startup']:p.error('Original selector drift; investigate before mutation')
  identity=run('sqlite3 -readonly /opt/dbspace/.pkgmgr_parser.db "SELECT package,app_exec,app_disable FROM package_app_info WHERE app_id=\'QuietHome1.Home\';"')
  if identity!='QuietHome1|/opt/usr/apps/QuietHome1/bin/QuietHomeStandalone.dll|false':p.error('Unexpected launcher identity')
  saved.write_text(json.dumps(state,indent=2))
  run("printf %s '"+base64.b64encode(saved.read_bytes()).decode()+"' | base64 -d > "+remote+'/routing-before.json')
  try:
   set_operation(state['operation'],APP)
   set_pref('db/appfw/home_appid',APP);set_pref('db/appfw/startup_appid',APP)
   if operation()!=APP:raise RuntimeError('Handler readback mismatch')
  except Exception:
   if operation()==APP:set_operation(APP,state['operation'])
   set_pref('db/appfw/home_appid',state['home']);set_pref('db/appfw/startup_appid',state['startup']);raise
  print('Assigned and read back all three selectors. Test Home, standby/wake and full restart with the remote.')
 else:
  original=json.loads(saved.read_text())
  for k in ('operation','home','startup'):
   if state[k] not in (APP,original[k]):p.error('Selector drift: '+k)
  if state['operation']==APP:set_operation(APP,original['operation'])
  set_pref('db/appfw/home_appid',original['home']);set_pref('db/appfw/startup_appid',original['startup'])
  if operation()!=original['operation']:raise RuntimeError('Restored handler mismatch')
  print('Original routing restored. No apps removed and no live databases replaced.')
if __name__=='__main__':main()
