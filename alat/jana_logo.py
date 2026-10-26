#!/usr/bin/env python3
"""Jana set logo MADOCS daripada PNG asal (2480 px, latar lutsinar).

Output:
  assets/logo-192.webp       - logo header (retina 2x untuk paparan 55 px)
  assets/logo-128.webp       - logo untuk JSON-LD / meta (nama lama dikekalkan)
  assets/favicon-64.png      - favicon
  assets/apple-touch-180.png - ikon iOS (latar putih, tiada lutsinar)
"""
import pathlib

from PIL import Image

SUMBER = pathlib.Path("/home/ubuntu/.hermes/profiles/madocs/cache/images/img_68e2bd0c442c.png")
ASET = pathlib.Path("/home/ubuntu/madocs-site/assets")

PAD = 0.02  # 2% ruang kosong di keliling


def potong_rapat(im: Image.Image) -> Image.Image:
    bbox = im.getbbox()
    return im.crop(bbox)


def pada_kanvas(im: Image.Image, tinggi: int, latar=None) -> Image.Image:
    """Skala ikut tinggi, letak di tengah kanvas segi empat sama."""
    nisbah = im.width / im.height
    lebar = max(1, round(tinggi * nisbah))
    kecil = im.resize((lebar, tinggi), Image.LANCZOS)
    kanvas = Image.new("RGBA", (tinggi, tinggi), latar if latar else (0, 0, 0, 0))
    kanvas.alpha_composite(kecil, ((tinggi - lebar) // 2, 0))
    return kanvas


def main():
    asal = Image.open(SUMBER).convert("RGBA")
    logo = potong_rapat(asal)
    print("logo dipotong: %dx%d (nisbah %.3f)" % (logo.width, logo.height, logo.width / logo.height))

    # Header: tinggi 192 px (2x daripada 55-96 px paparan)
    h192 = round(192 * (1 - 2 * PAD))
    l192 = pada_kanvas(logo, h192)
    l192.save(ASET / "logo-192.webp", "WEBP", quality=92, method=6)

    l128 = pada_kanvas(logo, round(128 * (1 - 2 * PAD)))
    l128.save(ASET / "logo-128.webp", "WEBP", quality=92, method=6)

    fav = pada_kanvas(logo, 58)          # 58/64 = sedikit margin
    fav.resize((64, 64), Image.LANCZOS).save(ASET / "favicon-64.png", "PNG", optimize=True)

    sentuh = pada_kanvas(logo, 152, latar=(255, 255, 255, 255))
    sentuh.resize((180, 180), Image.LANCZOS).save(ASET / "apple-touch-180.png", "PNG", optimize=True)

    for f in ("logo-192.webp", "logo-128.webp", "favicon-64.png", "apple-touch-180.png"):
        print("%-24s %6.1f KB" % (f, (ASET / f).stat().st_size / 1024))


if __name__ == "__main__":
    main()
