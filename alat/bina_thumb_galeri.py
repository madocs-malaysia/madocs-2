#!/usr/bin/env python3
"""Jana versi responsif gambar galeri.

  <nama>-kecil.webp      520 px  — grid galeri (slot ~45vw pada telefon 1x)
  <nama>-sederhana.webp  780 px  — hanya untuk gambar asal >= 1100 px, supaya telefon
                                  2x/3x tidak memuat turun fail penuh (lightbox kekal guna asal)

Guna: python3 alat/bina_thumb_galeri.py [--paksa]
"""
import sys
from pathlib import Path

from PIL import Image

AKAR = Path('/home/ubuntu/madocs-site')
GALERI = AKAR / 'assets' / 'galeri'
LEBAR = 520
LEBAR_SEDERHANA = 780
MIN_UNTUK_SEDERHANA = 900
KUALITI = 82
KUALITI_SEDERHANA = 78


def jana(im, fail, lebar, akhiran, paksa):
    keluar = fail.with_name(fail.stem + akhiran + '.webp')
    if keluar.exists() and not paksa and keluar.stat().st_mtime >= fail.stat().st_mtime:
        return False
    if im.width <= lebar:
        im.save(keluar, format='WEBP', quality=(KUALITI_SEDERHANA if akhiran == '-sederhana' else KUALITI), method=6)
    else:
        tinggi = round(im.height * lebar / im.width)
        im.resize((lebar, tinggi), Image.LANCZOS).save(
        keluar, format='WEBP', quality=(KUALITI_SEDERHANA if akhiran == '-sederhana' else KUALITI), method=6)
    return True


def utama():
    paksa = '--paksa' in sys.argv
    bil_kecil = bil_sederhana = 0
    jimat = 0
    for fail in sorted(GALERI.rglob('*.webp')):
        if fail.stem.endswith(('-kecil', '-sederhana')):
            continue
        with Image.open(fail) as im:
            asal = fail.stat().st_size
            if jana(im, fail, LEBAR, '-kecil', paksa):
                bil_kecil += 1
            kecil = fail.with_name(fail.stem + '-kecil.webp')
            if kecil.exists():
                jimat += asal - kecil.stat().st_size
            if im.width >= MIN_UNTUK_SEDERHANA and jana(im, fail, LEBAR_SEDERHANA, '-sederhana', paksa):
                bil_sederhana += 1
    print(f'{bil_kecil} -kecil + {bil_sederhana} -sederhana dijana | jimat {jimat/1048576:.1f} MB')


if __name__ == '__main__':
    utama()
