"""Focused public-release audit; inspect the staged diff as well."""
from pathlib import Path
import re,subprocess
ROOT=Path(__file__).resolve().parents[1]
FORBIDDEN={'.dll','.pdb','.tpk','.wgt','.db','.p12','.pfx','.pem','.key','.token','.sqlite','.zip','.jpg','.jpeg','.html'}
def main():
 try:
  names=subprocess.check_output(['git','-C',str(ROOT),'ls-files'],text=True,stderr=subprocess.DEVNULL).splitlines()
 except subprocess.CalledProcessError:
  names=[p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and not any(v in p.relative_to(ROOT).parts for v in ('.git','.local','bin','obj','__pycache__'))]
 issues=[]
 for name in names:
  p=ROOT/name
  if any(v in Path(name).parts for v in ('.local','app-icons','custom-art')) or p.suffix.lower() in FORBIDDEN:issues.append(name+': excluded private/build artifact')
  if p.suffix.lower() in ('.md','.cs','.py','.json','.xml','.csproj','.txt') or p.name in ('.gitignore','LICENSE'):
   text=p.read_text(encoding='utf-8')
   patterns=[r'C:[\\/]Users[\\/]',r'(?<![\d.])10\.\d{1,3}\.\d{1,3}\.\d{1,3}(?![\d.])',r'(?<![\d.])192\.168\.\d{1,3}\.\d{1,3}(?![\d.])',r'gh[pousr]_[A-Za-z0-9]{20,}',r'github_pat_[A-Za-z0-9_]{20,}',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']
   if any(re.search(pattern,text) for pattern in patterns):issues.append(name+': potential private content')
 if issues:raise SystemExit('\n'.join(issues))
 print('Focused public audit passed:',len(names),'files. Inspect notices and the staged diff manually.')
if __name__=='__main__':main()
