"""OCR pantas untuk satu album: cetak petikan teks supaya dokumen/senarai dapat dikesan."""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageOps

AKAR = Path('/home/ubuntu/madocs-site/assets/galeri')
album = sys.argv[1] if len(sys.argv) > 1 else 'program-2025'

for f in sorted((AKAR / album).glob('*.webp')):
    if f.stem.endswith('-kecil'):
        continue
    with Image.open(f) as im:
        im = im.convert('L')
        im = im.resize((1000, int(im.height * 1000 / im.width)), Image.LANCZOS) if im.width < 1000 else im
        im = ImageOps.autocontrast(im)
        tmp = '/tmp/ocr_satu.png'
        im.save(tmp)
    r = subprocess.run(['tesseract', tmp, 'stdout', '-l', 'eng', '--psm', '3'],
                       capture_output=True, text=True, timeout=90)
    teks = ' '.join((r.stdout or '').split())[:150]
    print(f'{f.name:16s} | {teks}')
