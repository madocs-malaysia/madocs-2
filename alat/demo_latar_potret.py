#!/usr/bin/env python3
"""Demo v2: potret pada saiz laman — latar asal vs latar putih (rembg u2net)."""
import pathlib

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from rembg import new_session, remove

SUMBER = pathlib.Path("/home/ubuntu/.hermes/profiles/madocs/cache/documents/native-inputs/"
                      "df22b412b98eefb1109918426ba8d399174dbbb05979737d3effe0cc4cad93ed/img_ad68bb53cc6c.jpg")
OUT = pathlib.Path("/home/ubuntu/.hermes/profiles/madocs/cache/preview/potret-banding-latar.png")
OUT_PUTIH = pathlib.Path("/home/ubuntu/.hermes/profiles/madocs/cache/preview/potret-latar-putih-penuh.png")

# Sumber 3499 px; kerja pada 1400 px sudah memadai untuk paparan 104 px.
KERJA = 1400


def segi_empat(im: Image.Image) -> Image.Image:
    w, h = im.size
    sisi = min(w, h)
    return im.crop(((w - sisi) // 2, 0, (w + sisi) // 2, sisi))


def atas_putih(im: Image.Image) -> Image.Image:
    kecil = im.resize((KERJA, KERJA), Image.LANCZOS)
    potong = remove(kecil, session=new_session("u2net"), post_process_mask=True,
                    alpha_matting=True, alpha_matting_foreground_threshold=250,
                    alpha_matting_background_threshold=20,
                    alpha_matting_erode_size=12)
    putih = Image.new("RGBA", potong.size, (255, 255, 255, 255))
    putih.alpha_composite(potong)
    return putih.convert("RGB").resize(im.size, Image.LANCZOS)


def bulatan(im: Image.Image, saiz=104, skala=4) -> Image.Image:
    sisi = min(im.size)
    im = im.crop((0, 0, sisi, sisi)).resize((saiz, saiz), Image.LANCZOS)
    mask = Image.new("L", (saiz, saiz), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, saiz - 1, saiz - 1), fill=255)
    keluar = Image.new("RGBA", (saiz, saiz), (0, 0, 0, 0))
    keluar.paste(im, (0, 0), mask)
    return keluar.resize((saiz * skala, saiz * skala), Image.LANCZOS)


def main():
    asal = segi_empat(Image.open(SUMBER).convert("RGB"))
    putih = atas_putih(asal)
    putih.save(OUT_PUTIH, quality=92)

    a, b = bulatan(asal), bulatan(putih)

    W, H = 1000, 660
    kanvas = Image.new("RGB", (W, H), (246, 244, 240))
    d = ImageDraw.Draw(kanvas)
    try:
        fon = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        kecil_f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except OSError:
        fon = kecil_f = ImageFont.load_default()

    d.text((40, 26), "Pada saiz laman (bulatan 104 px) — dibesarkan 4x", fill=(60, 60, 60), font=kecil_f)
    for i, (im, label) in enumerate(((a, "A. Latar asal"), (b, "B. Latar putih"))):
        x = 60 + i * 470
        kanvas.paste(im, (x, 90), im)
        d.text((x + 30, 540), label, fill=(30, 30, 30), font=fon)

    d.text((40, 600), "Saiz sebenar di telefon:", fill=(60, 60, 60), font=kecil_f)
    for i, im in enumerate((a, b)):
        kecil = im.resize((104, 104), Image.LANCZOS)
        kanvas.paste(kecil, (330 + i * 150, 590), kecil)

    kanvas.save(OUT, quality=94)
    print("simpan:", OUT)
    print("penuh:", OUT_PUTIH)


if __name__ == "__main__":
    main()
