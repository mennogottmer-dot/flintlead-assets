from pathlib import Path
import tempfile
import unittest
from PIL import Image
from check_assets import validate

class AssetChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
    def test_real_image_and_svg_are_accepted(self):
        Image.new('RGB', (3, 2)).save(self.root / 'image.png')
        (self.root / 'mark.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"/>')
        self.assertEqual(validate(self.root, ['image.png', 'mark.svg']), 2)
    def test_missing_or_empty_inputs_fail(self):
        with self.assertRaises(ValueError): validate(self.root, ['absent.png'])
        (self.root / 'empty.md').touch()
        with self.assertRaises(ValueError): validate(self.root, ['empty.md'])
        with self.assertRaises(ValueError): validate(self.root, [])
    def test_corrupt_image_or_non_svg_fail(self):
        (self.root / 'bad.png').write_text('broken')
        with self.assertRaises(Exception): validate(self.root, ['bad.png'])
        (self.root / 'bad.svg').write_text('<html/>')
        with self.assertRaises(ValueError): validate(self.root, ['bad.svg'])
    def test_escaped_path_fails(self):
        with self.assertRaises(ValueError): validate(self.root, ['../outside.md'])

if __name__ == '__main__': unittest.main()
