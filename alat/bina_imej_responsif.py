#!/usr/bin/env python3
"""Jana versi responsif untuk imej di assets/ (bukan hero, bukan galeri).

Dua saiz:
  <nama>-kecil.webp      520 px  — kad berita/aktiviti pada telefon 1x
  <nama>-sederhana.webp  780 px  — hanya untuk imej asal >= 1100 px, supaya telefon
                                  2x/3x tidak perlu memuat turun fail penuh

Imej 800-1000 px tidak diberi versi sederhana: mengekod semula pada 780 px
menghasilkan fail yang hampir sama besar (kadang-kadang lebih besar).

Galeri dan hero ada skrip sendiri (bina_thumb_galeri.py, bina_hero.py).

Guna: python3 alat/bina_imej_responsif.py [--paksa]
"""
import sys
from pathlib import Path

from PIL import Image

AKAR = Path('/home/ubuntu/madocs-site')
ASET = AKAR / 'assets'
KECUALI = ('hero', 'galeri', 'jawatankuasa', 'dokumen')
LEBAR = 520
LEBAR_SEDERHANA = 780
MIN_UNTUK_SEDERHANA = 1100
KUALITI = 82


def jana(im, fail, lebar, akhiran, paksa):
    """Tulis <nama><akhiran>.webp jika perlu. Pulangkan bait yang dijimatkan."""
    keluar = fail.with_name(fail.stem + akhiran + '.webp')
    if keluar.exists() and not paksa and keluar.stat().st_mtime >= fail.stat().st_mtime:
        return 0
    tinggi = round(im.height * lebar / im.width)
    im.resize((lebar, tinggi), Image.LANCZOS).save(keluar, format='WEBP', quality=KUALITI, method=6)
    return fail.stat().st_size - keluar.stat().st_size


def utama():
    paksa = '--paksa' in sys.argv
    bil_kecil = bil_sederhana = 0
    jimat = 0
    for fail in sorted(ASET.rglob('*.webp')):
        relatif = fail.relative_to(ASET)
        if relatif.parts[0] in KECUALI or fail.stem.endswith(('-kecil', '-sederhana')):
            continue
        with Image.open(fail) as im:
            if im.width > LEBAR:
                if jana(im, fail, LEBAR, '-kecil', paksa):
                    bil_kecil += 1
                kecil = fail.with_name(fail.stem + '-kecil.webp')
                if kecil.exists():
                    jimat += fail.stat().st_size - kecil.stat().st_size
            if im.width >= MIN_UNTUK_SEDERHANA:
                if jana(im, fail, LEBAR_SEDERHANA, '-sederhana', paksa):
                    bil_sederhana += 1
    print(f'{bil_kecil} -kecil + {bil_sederhana} -sederhana dijana | jimat berbanding asal '
          f'{jimat/1048576:.1f} MB')


if __name__ == '__main__':
    utama()
