#!/usr/bin/env python3
"""Hasilkan slaid hero (roulette) daripada gambar galeri dan berita.

Keluaran: assets/hero/<nama>-besar.webp (1400x1015) dan <nama>-telefon.webp (1100x733).
Kedua-dua saiz menggunakan nisbah 1.379:1 supaya kad hero tidak melompat.
"""
import os
import sys
from PIL import Image, ImageFilter

AKAR = '/home/ubuntu/madocs-site'
BESAR = (1400, 1015)
TELEFON = (1100, 733)

# (fail sumber, nama keluaran, berat menegak 0=atas 1=bawah)
SLAID = [
    ('assets/galeri/ccc6-cheras-2025/09.webp', 'sop-briefing', 0.42),
    ('assets/galeri/pcc1-2-kota-kinabalu-2026/05.webp', 'dorsal-slit', 0.38),
    ('assets/galeri/batu-pahat-2025/13.webp', 'instrumen', 0.72),
    ('assets/galeri/ccc6-cheras-2025/07.webp', 'peranti', 0.40),
    ('assets/galeri/ccc6-cheras-2025/06.webp', 'anatomi', 0.34),
    ('assets/galeri/pelancaran-2026/03.webp', 'berita-pelancaran', 0.40),
    ('assets/berita-2026-08-10-lawatan.webp', 'berita-lawatan', 0.40),
]


def potong(im, saiz, fokus_y=0.4):
    """Crop cover mengikut nisbah sasaran, kemudian resize + sharpen ringan."""
    lw, lh = saiz
    nisbah = lw / lh
    w, h = im.size
    if w / h > nisbah:               # terlalu lebar → potong kiri kanan
        baru_w = int(h * nisbah)
        x = (w - baru_w) // 2
        kotak = (x, 0, x + baru_w, h)
    else:                             # terlalu tinggi → potong atas bawah
        baru_h = int(w / nisbah)
        y = int((h - baru_h) * fokus_y)
        kotak = (0, y, w, y + baru_h)
    keluar = im.crop(kotak).resize(saiz, Image.LANCZOS)
    keluar = keluar.filter(ImageFilter.UnsharpMask(radius=1.6, percent=110, threshold=3))
    return keluar


def main():
    for src, nama, fokus in SLAID:
        laluan = os.path.join(AKAR, src)
        if not os.path.exists(laluan):
            print('TIADA:', src)
            continue
        im = Image.open(laluan).convert('RGB')
        for saiz, akhiran in ((TELEFON, 'telefon'), (BESAR, 'besar')):
            out = potong(im, saiz, fokus)
            matlamat = os.path.join(AKAR, 'assets', 'hero', '%s-%s.webp' % (nama, akhiran))
            out.save(matlamat, 'WEBP', quality=82, method=6)
            print('%-22s %-8s %s  %d KB' % (nama, akhiran, '%dx%d' % saiz,
                                            os.path.getsize(matlamat) // 1024))


if __name__ == '__main__':
    main()
