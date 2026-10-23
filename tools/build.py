"""Build and package locally. Does not sign, install, or touch a TV."""
import argparse,json,os,subprocess,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--framework',type=Path,required=True);p.add_argument('--dotnet',default=os.environ.get('DOTNET','dotnet'));a=p.parse_args()
 for name in ('Tizen.NUI','Tizen.Applications.Common','Tizen.System','Tizen'):
  if not (a.framework/(name+'.dll')).is_file():p.error('Missing matching reference: '+name)
 for project,name in [('launcher/src/Home.csproj','Home'),('launcher/routing/Routing.csproj','Routing')]:
  subprocess.run([a.dotnet,'build',str(ROOT/project),'-c','Release','-o',str(ROOT/'.local/build'/name),'-p:TV_FRAMEWORK_DIR='+str(a.framework.resolve()),'-p:Deterministic=true','-p:PathMap='+str(ROOT)+'=/_/quiet-tizen-qn90b'],check=True)
 manifest=ROOT/'launcher/tizen-manifest.xml';meta=ET.parse(manifest).getroot();out=ROOT/'.local/package';out.mkdir(parents=True,exist_ok=True)
 archive=out/(meta.get('package')+'-'+meta.get('version')+'-unsigned.tpk')
 assets=ROOT/'launcher/assets';catalog=assets/'apps.local.json'
 if not catalog.exists():catalog=assets/'apps.json'
 apps=json.loads(catalog.read_text(encoding='utf-8'))
 for app in apps:
  path=Path(app['Asset'])
  if path.is_absolute() or '..' in path.parts or not (assets/path).is_file():raise ValueError('Invalid/missing asset: '+str(path))
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  z.write(manifest,'tizen-manifest.xml');z.write(ROOT/'launcher/shared/res/quiet-home.png','shared/res/quiet-home.png')
  for n in ('QuietHomeStandalone.dll','QuietHomeStandalone.deps.json','QuietHomeStandalone.runtimeconfig.json'):z.write(ROOT/'.local/build/Home'/n,'bin/'+n)
  for path in assets.rglob('*'):
   if path.is_file() and path.name not in ('apps.json','apps.local.json'):
    chosen=assets/'custom-art/dock-ps5-official.svg' if path.name=='free-dock-ps5.svg' and (assets/'custom-art/dock-ps5-official.svg').is_file() else path
    z.write(chosen,'bin/quiet-home/'+path.relative_to(assets).as_posix())
  z.writestr('bin/quiet-home/apps.json',json.dumps(apps,indent=2))
  if any(Path(n).name.startswith('Tizen') and n.endswith('.dll') for n in z.namelist()):raise ValueError('Samsung DLL unexpectedly bundled')
 print('Unsigned package:',archive);print('Sign this existing TPK with your own Samsung TV profile. Do not package the directory.')
if __name__=='__main__':main()
