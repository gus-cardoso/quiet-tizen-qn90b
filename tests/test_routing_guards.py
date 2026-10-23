"""Exercise public routing orchestration with a fake TV, never live hardware."""
import base64,hashlib,json,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import tv
class FakeClient:
 def __init__(self,*args,**kwargs):
  self.operation='com.samsung.tv.csfs';self.home='com.samsung.tv.csfs';self.startup='org.tizen.tv-viewer';self.files={};self.fail_startup=False
 def capture(self,command,**kwargs):
  if command.startswith('readlink '):out='/usr/share/dotnet.tizen/netcoreapp/3.1.3'
  elif command=='cat /etc/tizen-release':out='Tizen6/TV'
  elif command=='uname -m':out='armv7l'
  elif command.startswith('printf %s '):
   encoded=command.split("'")[1];path=command.split(' > ')[1];self.files[path]=base64.b64decode(encoded);out=''
  elif command.startswith('sha256sum '):out=hashlib.sha256(self.files[command.split(' ',1)[1]]).hexdigest()+'  file'
  elif command.startswith('/usr/bin/dotnet '):
   if ' set ' in command:
    expected,target=command.rsplit(' set ',1)[1].split();
    if self.operation!=expected:return types.SimpleNamespace(output='drift\n[exit:3]')
    self.operation=target;out='get_result=0 home='+expected+'\nset_result=0\nverify_result=0 home='+target
   else:out='get_result=0 home='+self.operation
  elif command.startswith('vconftool get '):
   key=command.split()[-1];out=key+', value = '+(self.home if key.endswith('home_appid') else self.startup)+' (String)'
  elif command.startswith('vconftool set '):
   key,target=command.split()[-2:]
   if key.endswith('startup_appid') and target==tv.APP and self.fail_startup:return types.SimpleNamespace(output='denied\n[exit:1]')
   if key.endswith('home_appid'):self.home=target
   else:self.startup=target
   out=''
  elif command.startswith('sqlite3 -readonly '):out='QuietHome1|/opt/usr/apps/QuietHome1/bin/QuietHomeStandalone.dll|false'
  else:raise AssertionError('Unexpected SDK command: '+command)
  return types.SimpleNamespace(output=out+'\n[exit:0]')
class RoutingGuards(unittest.TestCase):
 def setUp(self):
  self.scratch=Path(__file__).resolve().parents[1]/'.local/test-runs';self.scratch.mkdir(parents=True,exist_ok=True)
  self.tmp=tempfile.TemporaryDirectory(dir=self.scratch);self.root=Path(self.tmp.name);self.snapshot=self.root/'.local/backups/phase';self.snapshot.mkdir(parents=True)
  entries=[]
  for name in tv.DBS:
   data=b'fixture database bytes';(self.snapshot/name).write_bytes(data);entries.append({'name':name,'sha256':hashlib.sha256(data).hexdigest()})
  self.meta={'host':'192.0.2.10','model':tv.MODEL,'firmware':tv.FIRMWARE,'remote':'/home/owner/share/tmp/sdk_tools/fixture','home':'com.samsung.tv.csfs','startup':'org.tizen.tv-viewer','files':entries}
  (self.snapshot/'manifest.json').write_text(json.dumps(self.meta))
  build=self.root/'.local/build/Routing';build.mkdir(parents=True)
  for n in ('Routing.dll','Routing.deps.json','Routing.runtimeconfig.json'):(build/n).write_bytes(b'helper fixture')
  self.client=FakeClient();module=types.ModuleType('samsung_tv_root.sdb');module.SdbClient=lambda *a,**kw:self.client
  self.stack=[patch.object(tv,'ROOT',self.root),patch.dict(sys.modules,{'samsung_tv_root.sdb':module}),patch.object(tv.subprocess,'check_output',return_value='192.0.2.10:26101 device '+tv.MODEL)]
  for item in self.stack:item.start()
 def tearDown(self):
  for item in reversed(self.stack):item.stop()
  self.assertTrue(self.root.resolve().is_relative_to(self.scratch.resolve()))
  self.tmp.cleanup()
 def invoke(self,action):
  argv=['tv.py',action,'--host','192.0.2.10','--callback','192.0.2.20','--sdb','fixture-sdb','--transport-src',str(self.root),'--firmware',tv.FIRMWARE,'--snapshot',str(self.snapshot),'--validated']
  with patch.object(sys,'argv',argv):tv.main()
 def test_apply_and_restore_three_selectors(self):
  self.invoke('route');self.assertEqual((self.client.operation,self.client.home,self.client.startup),(tv.APP,)*3)
  self.assertTrue((self.snapshot/'routing-before.json').is_file())
  self.invoke('restore');self.assertEqual((self.client.operation,self.client.home,self.client.startup),('com.samsung.tv.csfs','com.samsung.tv.csfs','org.tizen.tv-viewer'))
 def test_partial_assignment_rolls_back(self):
  self.client.fail_startup=True
  with self.assertRaises(RuntimeError):self.invoke('route')
  self.assertEqual((self.client.operation,self.client.home,self.client.startup),('com.samsung.tv.csfs','com.samsung.tv.csfs','org.tizen.tv-viewer'))
 def test_preexisting_selector_drift_stops_before_assignment(self):
  self.client.home='unrelated.App'
  with self.assertRaises(SystemExit):self.invoke('route')
  self.assertEqual(self.client.operation,'com.samsung.tv.csfs');self.assertEqual(self.client.home,'unrelated.App')
  self.assertFalse((self.snapshot/'routing-before.json').exists())
if __name__=='__main__':unittest.main()
