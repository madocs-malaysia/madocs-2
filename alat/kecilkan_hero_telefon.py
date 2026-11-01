#!/usr/bin/env python3
"""Kecilkan imej hero telefon: 1100x733 -> 720x480 (jimat ~45% berat mudah alih)."""
import glob, os
from PIL import Image

AKAR = "/home/ubuntu/madocs-site"
HERO = os.path.join(AKAR, "assets", "hero")
SAIZ_BARU = (720, 480)

fail = sorted(glob.glob(os.path.join(HERO, "*-telefon.webp")))
jimat = 0
for f in fail:
    im = Image.open(f)
    if im.size != (1100, 733):
        print("SKIP (saiz berbeza %s): %s" % (im.size, os.path.basename(f)))
        continue
    sebelum = os.path.getsize(f)
    im = im.resize(SAIZ_BARU, Image.LANCZOS)
    im.save(f, "WEBP", quality=82, method=6)
    selepas = os.path.getsize(f)
    jimat += (sebelum - selepas)
    print("OK  %6dKB -> %6dKB  %s" % (sebelum//1024, selepas//1024, os.path.basename(f)))

print("\nJumlah jimat: %d KB (%.1f%%)" % (jimat//1024, 0))
