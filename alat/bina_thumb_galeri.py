#!/usr/bin/env python3
"""Jana versi kecil gambar galeri untuk grid (jimat data pada telefon).

Grid galeri memaparkan gambar selebar ~300-400 px sahaja, tetapi fail asal 1000-1600 px.
Skrip ini menulis `<nama>-kecil.webp` (lebar 520 px) di sebelah fail asal. Versi penuh
kekal untuk lightbox.

Guna: python3 alat/bina_thumb_galeri.py [--paksa]
"""
import sys
from pathlib import Path

from PIL import Image

AKAR = Path('/home/ubuntu/madocs-site')
GALERI = AKAR / 'assets' / 'galeri'
LEBAR = 520
KUALITI = 82


def utama():
    paksa = '--paksa' in sys.argv
    baru = 0
    jimat = 0
    for fail in sorted(GALERI.rglob('*.webp')):
        if fail.stem.endswith('-kecil'):
            continue
        kecil = fail.with_name(fail.stem + '-kecil.webp')
        if kecil.exists() and not paksa and kecil.stat().st_mtime >= fail.stat().st_mtime:
            continue
        with Image.open(fail) as im:
            asal_saiz = fail.stat().st_size
            if im.width <= LEBAR:
                im.save(kecil, format='WEBP', quality=KUALITI, method=6)
            else:
                tinggi = round(im.height * LEBAR / im.width)
                im.resize((LEBAR, tinggi), Image.LANCZOS).save(
                    kecil, format='WEBP', quality=KUALITI, method=6)
        baru += 1
        jimat += asal_saiz - kecil.stat().st_size
    print(f'{baru} versi kecil dijana | jimat {jimat/1048576:.1f} MB berbanding fail penuh')


if __name__ == '__main__':
    utama()
