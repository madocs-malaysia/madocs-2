"""Senarai pendek gambar yang mungkin memaparkan skrin/lembaran dengan teks (calon data peribadi).

Heuristik: kawasan tengah yang terang, saturasi rendah, dan ketumpatan tepi tinggi
(ciri skrin atau kertas bercetak). Bukan pengganti OCR — hanya untuk semakan pantas.
"""
from pathlib import Path

import cv2
import numpy as np

AKAR = Path('/home/ubuntu/madocs-site')
GALERI = AKAR / 'assets' / 'galeri'
hasil = []

for f in sorted(p for p in GALERI.rglob('*.webp') if not p.stem.endswith('-kecil')):
    im = cv2.imread(str(f))
    if im is None:
        continue
    h, w = im.shape[:2]
    tengah = im[int(h * 0.25):int(h * 0.75), int(w * 0.2):int(w * 0.8)]
    hsv = cv2.cvtColor(tengah, cv2.COLOR_BGR2HSV)
    kecerahan = float(np.mean(hsv[:, :, 2])) / 255
    saturasi = float(np.mean(hsv[:, :, 1])) / 255
    kelabu = cv2.cvtColor(tengah, cv2.COLOR_BGR2GRAY)
    tepi = float(np.mean(cv2.Canny(kelabu, 60, 160) > 0))
    skor = kecerahan * (1 - min(saturasi, 1)) * (0.5 + tepi * 6)
    hasil.append((skor, str(f.relative_to(AKAR)), round(kecerahan, 2), round(saturasi, 2), round(tepi, 3)))

hasil.sort(reverse=True)
print('calon teratas (skor, fail, kecerahan, saturasi, tepi):')
for s in hasil[:18]:
    print(f'  {s[0]:.3f}  {s[1]:55s} {s[2]} {s[3]} {s[4]}')
