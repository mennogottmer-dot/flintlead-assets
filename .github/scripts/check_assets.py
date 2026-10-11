"""Validate committed brand inputs without contacting their published host."""
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image

REQUIRED = ['assets/email/fl-scan-en.jpg', 'assets/email/fl-scan-nl.jpg', 'assets/favicon.svg', 'assets/flintlead-avatar-200.gif', 'assets/flintlead-avatar-400.gif', 'assets/flintlead-mark.svg', 'assets/flintlead-profile-250.png', 'assets/flintlead-profile-512.png', 'assets/flintlead-signature-200.gif', 'assets/flintlead-signature-400.gif', 'assets/flintlead-signature-500.gif', 'assets/flintlead-signature-96.gif', 'assets/flintlead-signature-static-200.png', 'index.html', 'CNAME']

ROOT = Path(__file__).resolve().parents[2]

def validate(root, required):
    root = root.resolve()
    count = 0
    for name in required:
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError('Missing or unsafe asset: ' + name)
        if not path.stat().st_size:
            raise ValueError('Empty asset: ' + name)
        suffix = path.suffix.lower()
        if suffix == '.svg':
            element = ET.parse(path).getroot()
            if element.tag != '{http://www.w3.org/2000/svg}svg':
                raise ValueError('Not an SVG: ' + name)
            if not element.get('viewBox') and not (element.get('width') and element.get('height')):
                raise ValueError('SVG dimensions missing: ' + name)
        elif suffix in ('.png', '.gif', '.jpg', '.jpeg'):
            with Image.open(path) as image:
                if min(image.size) <= 0:
                    raise ValueError('Invalid dimensions: ' + name)
                image.verify()
        elif suffix in ('.md', '.txt', '.html'):
            path.read_text(encoding='utf-8')
        count += 1
    if not count:
        raise ValueError('No required assets')
    return count

if __name__ == '__main__':
    print(f'{validate(ROOT, REQUIRED)} committed inputs checked')
