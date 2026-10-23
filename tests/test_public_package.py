"""Offline release checks; no TV, credentials or network access."""
import json,sys,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from tv import value
class ReleaseChecks(unittest.TestCase):
 def test_vconf_parser_rejects_wrong_type_and_missing_value(self):
  self.assertEqual(value('db/appfw/home_appid, value = example.App (String)'),'example.App')
  for bad in ('permission denied','value = 1 (Int)',''):
   with self.assertRaises(ValueError):value(bad)
 def test_package_has_public_catalog_icon_and_no_samsung_dlls(self):
  archives=list((ROOT/'.local/package').glob('*.tpk'))
  self.assertTrue(archives,'Build first; this checks the actual produced archive')
  with zipfile.ZipFile(archives[-1]) as z:
   self.assertIn('shared/res/quiet-home.png',z.namelist())
   apps=json.loads(z.read('bin/quiet-home/apps.json'));self.assertEqual(len(apps),3)
   for app in apps:self.assertIn('bin/quiet-home/'+app['Asset'],z.namelist())
   self.assertFalse(any(Path(n).name.startswith('Tizen') and n.endswith('.dll') for n in z.namelist()))
   self.assertNotIn(b'240000',(ROOT/'launcher/src/Home.cs').read_bytes())
if __name__=='__main__':unittest.main()
