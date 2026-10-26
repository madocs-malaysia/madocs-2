#!/usr/bin/env python3
"""Sediakan potret AJK: latar putih + crop piawai laman (dengan gelung auto-fit).

Piawai: muka 0.50-0.56 daripada tinggi bingkai, garis mata ~0.40 dari atas, 480 px webp.
Gelung auto-fit: ukur semula muka pada hasil crop, laraskan sisi sehingga nisbah betul.
"""
import pathlib
import urllib.request

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

SUMBER = pathlib.Path("/home/ubuntu/.hermes/profiles/madocs/cache/documents/native-inputs/"
                      "df22b412b98eefb1109918426ba8d399174dbbb05979737d3effe0cc4cad93ed/img_ad68bb53cc6c.jpg")
DEST = pathlib.Path("/home/ubuntu/madocs-site/assets/jawatankuasa/azfar-hakim.webp")
YUNET = pathlib.Path("/home/ubuntu/.hermes/profiles/madocs/cache/scratch/yunet.onnx")
SAIZ = 480
KERJA = 2400
MUKA_SASARAN = 0.53      # dalam julat 0.50-0.56 yang Doc terima
MATA_SASARAN = 0.40


def pastikan_yunet() -> str:
    if not YUNET.exists() or YUNET.stat().st_size < 100_000:
        YUNET.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(
            "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/"
            "face_detection_yunet_2023mar.onnx", YUNET)
    return str(YUNET)


def latar_putih(im: Image.Image) -> Image.Image:
    kecil = im.resize((KERJA, KERJA), Image.LANCZOS)
    potong = remove(kecil, session=new_session("u2net"), post_process_mask=True,
                    alpha_matting=True, alpha_matting_foreground_threshold=250,
                    alpha_matting_background_threshold=20, alpha_matting_erode_size=12)
    putih = Image.new("RGBA", potong.size, (255, 255, 255, 255))
    putih.alpha_composite(potong)
    return putih.convert("RGB")


def muka_terbesar(im: Image.Image):
    """Pulangkan (x, y, w, h, mata_y, pusat_x) muka terbesar, atau None."""
    bgr = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    h, w = bgr.shape[:2]
    det = cv2.FaceDetectorYN.create(pastikan_yunet(), "", (w, h), 0.6, 0.3, 5000)
    _, muka = det.detect(bgr)
    if muka is None or len(muka) == 0:
        return None
    m = max(muka, key=lambda r: r[2] * r[3])
    x, y, fw, fh = (float(v) for v in m[:4])
    mata_y = (float(m[5]) + float(m[7])) / 2.0     # landmark: mata kanan (4,5), mata kiri (6,7)
    return x, y, fw, fh, mata_y, x + fw / 2.0


def potong(im: Image.Image, sisi: float, pusat_x: float, mata_y: float) -> Image.Image:
    w, h = im.size
    x0 = min(max(pusat_x - sisi / 2.0, 0), w - sisi)
    y0 = min(max(mata_y - sisi * MATA_SASARAN, 0), h - sisi)
    return im.crop((int(round(x0)), int(round(y0)), int(round(x0 + sisi)), int(round(y0 + sisi))))


def crop_piawai(im: Image.Image) -> Image.Image:
    info = muka_terbesar(im)
    if not info:
        raise SystemExit("Muka tidak dikesan pada gambar asal")
    _, _, _, fh, mata_y, pusat_x = info
    sisi = fh / MUKA_SASARAN

    for pusingan in range(8):
        calon = potong(im, sisi, pusat_x, mata_y)
        semak = muka_terbesar(calon)
        if not semak:
            raise SystemExit("Muka hilang selepas crop (pusingan %d)" % pusingan)
        _, _, _, fh2, mata2, _ = semak
        nisbah = fh2 / calon.height
        print("  pusingan %d: sisi=%.0f nisbah muka=%.3f mata=%.3f"
              % (pusingan + 1, sisi, nisbah, mata2 / calon.height))
        if abs(nisbah - MUKA_SASARAN) <= 0.015:
            break
        sisi = sisi * (nisbah / MUKA_SASARAN)

    return calon.resize((SAIZ, SAIZ), Image.LANCZOS)


def main():
    asal = Image.open(SUMBER).convert("RGB")
    putih = latar_putih(asal)
    akhir = crop_piawai(putih)
    akhir.save(DEST, "WEBP", quality=86, method=6)
    info = muka_terbesar(akhir)
    print("fail: %s (%d px, %.0f KB)" % (DEST.name, akhir.width, DEST.stat().st_size / 1024))
    print("semakan akhir: muka %.2f bingkai, garis mata %.2f"
          % (info[3] / akhir.height, info[4] / akhir.height))


if __name__ == "__main__":
    main()
