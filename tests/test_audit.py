import json
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO
from vin_validation_claim_audit.audit import audit, claims, evidence, main
from vin_validation_claim_audit.phrases import VINVALIDATION, NOVINVALIDATION, GENERIC_NAMES


class AuditTests(unittest.TestCase):
    def test_phrases(self):
        for phrase in VINVALIDATION:
            with self.subTest(phrase=phrase):
                self.assertTrue(claims(phrase)[0])
        for phrase in NOVINVALIDATION:
            with self.subTest(phrase=phrase):
                self.assertEqual(claims(phrase)[0], set())
                self.assertTrue(claims(phrase)[1])
        self.assertEqual(claims('```\nvalidate vin\n```'), (set(), set()))

    def test_routes(self):
        routes = ['from vininfo import Vin\nVin.validate(x)', 'import vininfo as vi\nvi.Vin(x)', 'from vininfo import Vin\nv=Vin(x)\nv.validate(x)', 'from vininfo import Vin\nv=Vin(x)\nv.verify_checksum()', 'from vininfo import Vin\nVin.verify_checksum(x)', 'from vin import VIN\nVIN(x)', 'import vin\nvin.VIN(x, decode=False)', 'from vin import VIN\nVIN.calculate_check_digit(x)', 'from vin import VIN\nv=VIN(x, fix_check_digit=True)\nv.calculate_check_digit(x)', 'from pyvin.utils import clean_vins as clean\nclean(x)', 'import pyvin as p\np.utils.clean_vins(x)', 'from pyvin import utils\nutils.clean_vins(x)']
        routes += ['obj.'+name+'(x)' for name in GENERIC_NAMES]
        routes += ['from lib import '+name+' as f\nf(x)' for name in GENERIC_NAMES]
        for source in routes:
            with self.subTest(source=source): self.assertTrue(evidence(source))

    def test_not_evidence(self):
        cases = ['import vininfo', 'import vin', 'import pyvin', 'VIN(x)', 'Vin(x)', 'validate(x)', 'verify_checksum(x)', 'calculate_check_digit(x)', 'clean_vins(x)', 'validate_vin(x)', 'x.validate(y)', 'x.verify_checksum()', 'x.calculate_check_digit(y)', 'x.clean_vins(y)', 'from vin import VIN\nVIN(x, fix_check_digit=True)', 'import pyvin\npyvin.VIN(x)', 'DecodedVIN(x)', 'VehicleDB.decode_vin(x)', 'wmi[x]', 'get_wmis_for_cars_and_light_trucks()', 'extract_vin(x)', 'history.lookup(x)', 'import re\nre.match(pattern, x)', 'import re\nre.search(pattern, x)', 'import re\nre.fullmatch(pattern, x)', 'str(x)', 'repr(x)', '"validate vin"', 'def validate_vin(x): pass\nobj.validate_vin(x)', 'from lib import validate_vin\nwith x as validate_vin: pass\nvalidate_vin(x)', 'def broken(:', 'subprocess.run(["vin"])']
        cases += ['validators.'+n+'(x)' for n in ('vin','card_number','email','url','ipv4','ipv6','domain','uuid','mac_address')]
        cases += ['x.'+n for n in ('manufacturer','make','model','model_year','wmi','vds','vis','brand','details','region','country','years','body_class','trim','series','vehicle_type','electrification_level','description','descriptor','vpic_version')]
        cases += ['x._decode_vin()', 'x._decode_model_year()', 'pay(x)']
        for source in cases:
            with self.subTest(source=source): self.assertFalse(evidence(source))

    def test_findings(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); (p/'README.md').write_text('validate vin')
            self.assertEqual(audit(p)[0]['severity'], 'HIGH')
            (p/'tests').mkdir(); (p/'tests/test_x.py').write_text('x.validate_vin(y)')
            self.assertEqual(audit(p)[0]['severity'], 'MEDIUM')
            (p/'app.py').write_text('x.validate_vin(y)')
            self.assertFalse(audit(p))
            (p/'README.md').write_text('no vin validation')
            self.assertEqual(audit(p)[0]['id'], 'documented-no-vin-validation-claim-false')

    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/'README.md').write_text('validate vin')
            with redirect_stdout(StringIO()) as out:
                self.assertEqual(main(['audit', d, '--json']), 2)
            self.assertEqual(json.loads(out.getvalue())['findings'][0]['id'], 'documented-vin-validation-claim-false')
            with redirect_stdout(StringIO()): self.assertEqual(main(['audit', d, '--ignore', 'README.md']), 0)

    def test_self_audit(self):
        self.assertFalse(audit(Path(__file__).resolve().parents[1]))

if __name__ == '__main__': unittest.main()
