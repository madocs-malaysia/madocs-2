#!/usr/bin/env python3
"""Kesan gambar galeri yang terbalik (putar 90°) dan betulkan.

Kaedah: jalankan pengesan muka YuNet pada imej asal dan pada 3 putaran lain.
Jika satu putaran menghasilkan muka yang jauh lebih banyak (atau lebih besar),
imej itu berkemungkinan besar disimpan dalam orientasi salah.

Guna: python3 alat/betulkan_putaran.py [--tulis]
Tanpa --tulis, ia hanya melaporkan.
"""
import sys
from pathlib import Path

import cv2
import numpy as np

AKAR = Path('/home/ubuntu/madocs-site')
MODEL = Path('/home/ubuntu/.hermes/profiles/madocs/cache/scratch/yunet.onnx')
GALERI = AKAR / 'assets' / 'galeri'


def muka(imej, pengesan):
    h, w = imej.shape[:2]
    pengesan.setInputSize((w, h))
    _, muka = pengesan.detect(imej)
    if muka is None:
        return 0, 0.0
    luas = sum((m[2] * m[3]) for m in muka)
    return len(muka), luas / float(w * h)


def putaran(imej, kod):
    if kod == 0:
        return imej
    if kode := kode_putaran(kod):
        return cv2.rotate(imej, kode)
    return imej


def kode_putaran(kod):
    return {90: cv2.ROTATE_90_CLOCKWISE, 180: cv2.ROTATE_180, 270: cv2.ROTATE_90_COUNTERCLOCKWISE}.get(kod)


def utama():
    tulis = '--tulis' in sys.argv
    pengesan = cv2.FaceDetectorYN.create(str(MODEL), '', (320, 320), 0.6, 0.3, 5000)
    calon = []
    for fail in sorted(GALERI.rglob('*.webp')):
        imej = cv2.imread(str(fail))
        if imej is None:
            continue
        asas_bil, asas_luas = muka(imej, pengesan)
        terbaik = (0, asas_bil, asas_luas)
        for kod in (90, 180, 270):
            bil, luas = muka(putaran(imej, kod), pengesan)
            if bil > terbaik[1] and luas > terbaik[2] * 1.05:
                terbaik = (kod, bil, luas)
        if terbaik[0] and terbaik[1] >= max(asas_bil + 1, 2):
            calon.append((fail, asas_bil, asas_luas, terbaik))

    if not calon:
        print('Tiada gambar yang dikesan terbalik.')
        return

    print(f'{len(calon)} gambar dikesan berkemungkinan terbalik:')
    for fail, asas_bil, asas_luas, (kod, bil, luas) in calon:
        print(f'  {fail.relative_to(AKAR)} | asal: {asas_bil} muka ({asas_luas:.4f}) '
              f'| putar {kod}°: {bil} muka ({luas:.4f})')
        if tulis:
            imej = cv2.imread(str(fail))
            hasil = putaran(imej, kod)
            cv2.imwrite(str(fail), hasil, [cv2.IMWRITE_WEBP_QUALITY, 90])
            print('     -> ditulis semula')


if __name__ == '__main__':
    utama()
