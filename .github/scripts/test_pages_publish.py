"""gh:flintlead-assets/pages-build-deployment: GitHub's own Pages build that publishes this repo's main branch
at https://assets.flintlead.com/ (the email-signature avatars, logos and scan images mail clients load).

It never failed (last run 11 Oct 2026). Core decision of what that build publishes, checked offline on the
committed files: the custom domain stays assets.flintlead.com; every published asset sits on a path the
legacy (Jekyll) Pages build serves, since there is no .nojekyll and Jekyll drops paths starting with "_" or
"."; no file reaches GitHub's 100 MB limit and the site stays far below Pages' 1 GB; the assets emails
load are all present and valid (check_assets.REQUIRED).
"""
from pathlib import Path
import subprocess
import unittest

from check_assets import REQUIRED, validate

ROOT = Path(__file__).resolve().parents[2]


def committed():
    out = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-z'], capture_output=True, text=True, check=True)
    return [name for name in out.stdout.split('\0') if name]


class PagesPublish(unittest.TestCase):
    def test_custom_domain(self):
        self.assertEqual((ROOT / 'CNAME').read_text().strip(), 'assets.flintlead.com')

    def test_every_asset_is_on_a_path_the_legacy_build_serves(self):
        self.assertFalse((ROOT / '.nojekyll').exists())   # if this changes, the rule below can be relaxed
        published = [n for n in committed() if not n.startswith('.github/') and n not in ('CNAME', 'README.md')]
        self.assertIn('index.html', published)
        hidden = [n for n in published if any(part.startswith(('_', '.')) for part in Path(n).parts)]
        self.assertEqual(hidden, [])

    def test_sizes_stay_within_github_pages_limits(self):
        sizes = {n: (ROOT / n).stat().st_size for n in committed() if (ROOT / n).is_file()}
        self.assertEqual([n for n, size in sizes.items() if size >= 100 * 1024 ** 2], [])
        self.assertLess(sum(sizes.values()), 1024 ** 3)

    def test_assets_that_emails_load_are_present_and_valid(self):
        self.assertEqual(validate(ROOT, REQUIRED), len(REQUIRED))
        self.assertTrue(set(REQUIRED) <= set(committed()))


if __name__ == '__main__':
    unittest.main()
