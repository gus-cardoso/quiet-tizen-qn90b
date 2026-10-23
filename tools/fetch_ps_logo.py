"""Optional local PlayStation symbol download; no logo redistribution."""
from pathlib import Path
from urllib.request import Request,urlopen
from xml.etree import ElementTree as ET
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
URL='https://www.playstation.com/etc.clientlibs/global_pdc/clientlibs/auto-clientlibs/pdc.designkit/resources/ps-icons-map__dig__brand.svg'
def main():
 data=urlopen(Request(URL,headers={'User-Agent':'quiet-tizen-qn90b'}),timeout=20).read()
 sprite=ET.fromstring(data);symbol=next(e for e in sprite if e.get('id')=='ps-icon_brand_playstation-family')
 for e in symbol.iter():
  if e.tag.rsplit('}',1)[-1] not in ('symbol','path','g'):raise ValueError('Unexpected external SVG element')
  if any(k.lower().startswith('on') or k.rsplit('}',1)[-1]=='href' for k in e.attrib):raise ValueError('Unexpected external SVG attribute')
 logo=''.join(ET.tostring(e,encoding='unicode') for e in symbol)
 original=(ROOT/'launcher/assets/free-dock-ps5.svg').read_text();i=original.index('<g fill="#fff">');wordmark=original[i:original.rindex('</svg>')]
 svg=original[:i]+'<g fill="#fff" transform="translate(62 -18) scale(2)">'+logo+'</g><g transform="translate(57 62) scale(.55)">'+wordmark+'</g></svg>'
 ET.fromstring(svg);destination=ROOT/'launcher/assets/custom-art/dock-ps5-official.svg';destination.parent.mkdir(exist_ok=True)
 if destination.exists():raise FileExistsError('Existing local logo preserved: '+str(destination))
 destination.write_text(svg);(ROOT/'.local').mkdir(exist_ok=True)
 (ROOT/'.local/ps-logo-provenance.json').write_text(json.dumps({'source':URL,'sha256':hashlib.sha256(data).hexdigest(),'symbol':symbol.get('id'),'changes':'Uniform scaling, white fill, placement above PS5 text; original symbol geometry'},indent=2))
 print('Saved optional local asset:',destination)
if __name__=='__main__':main()
