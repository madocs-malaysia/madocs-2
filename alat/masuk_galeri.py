#!/usr/bin/env python3
"""Masukkan gambar ke album galeri MADOCS.

Guna: python3 alat/masuk_galeri.py <slug-album> <fail1> <fail2> ...

- Menghormati EXIF orientation (gambar telefon sering tersimpan bersudut).
- Menjana <nama>.webp (lebar 1000) dan <nama>-kecil.webp (lebar 520).
- Ganti fail sedia ada dengan nama sama; nombor diteruskan dari album.
"""
from __future__ import annotations

import pathlib
import sys

from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent
GALERI = ROOT / "assets" / "galeri"
LEBAR = 1000
LEBAR_KECIL = 520


def simpan(im: Image.Image, dest: pathlib.Path, lebar: int, kualiti: int = 82) -> None:
    if im.width > lebar:
        tinggi = round(im.height * lebar / im.width)
        im = im.resize((lebar, tinggi), Image.LANCZOS)
    im.convert("RGB").save(dest, "WEBP", quality=kualiti, method=6)
    print("  %-34s %d x %d  %.0f KB" % (dest.name, im.width, im.height,
                                        dest.stat().st_size / 1024))


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    slug = sys.argv[1]
    folder = GALERI / slug
    folder.mkdir(parents=True, exist_ok=True)

    sedia = sorted(int(p.name.split(".")[0]) for p in folder.glob("*.webp")
                   if p.name.split(".")[0].isdigit())
    no = (max(sedia) if sedia else 0) + 1

    for fail in sys.argv[2:]:
        src = pathlib.Path(fail)
        if not src.exists():
            print("TIADA:", src)
            continue
        im = ImageOps.exif_transpose(Image.open(src))
        nama = "%02d" % no
        print(src.name, "->", nama)
        simpan(im, folder / (nama + ".webp"), LEBAR)
        simpan(im, folder / (nama + "-kecil.webp"), LEBAR_KECIL, 80)
        no += 1
    print("Selesai. Album:", folder)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
