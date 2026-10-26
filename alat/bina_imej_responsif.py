#!/usr/bin/env python3
"""Jana versi kecil (520 px) untuk imej di assets/ yang dipaparkan kecil pada halaman.

Hero (assets/hero) dan galeri (assets/galeri) ada skrip sendiri. Skrip ini untuk
gambar berita, kad program dan gambar kandungan yang dipaparkan selebar ~400 px.

Guna: python3 alat/bina_imej_responsif.py [--paksa]
"""
import sys
from pathlib import Path

from PIL import Image

AKAR = Path('/home/ubuntu/madocs-site')
ASET = AKAR / 'assets'
KECUALI = ('hero', 'galeri', 'jawatankuasa', 'dokumen')
LEBAR = 520
KUALITI = 82


def utama():
    paksa = '--paksa' in sys.argv
    bil = 0
    jimat = 0
    for fail in sorted(ASET.rglob('*.webp')):
        relatif = fail.relative_to(ASET)
        if relatif.parts[0] in KECUALI or fail.stem.endswith('-kecil'):
            continue
        kecil = fail.with_name(fail.stem + '-kecil.webp')
        if kecil.exists() and not paksa and kecil.stat().st_mtime >= fail.stat().st_mtime:
            continue
        with Image.open(fail) as im:
            if im.width <= LEBAR:
                continue
            tinggi = round(im.height * LEBAR / im.width)
            im.resize((LEBAR, tinggi), Image.LANCZOS).save(
                kecil, format='WEBP', quality=KUALITI, method=6)
        bil += 1
        jimat += fail.stat().st_size - kecil.stat().st_size
    print(f'{bil} imej responsif dijana | jimat {jimat/1048576:.1f} MB')


if __name__ == '__main__':
    utama()
