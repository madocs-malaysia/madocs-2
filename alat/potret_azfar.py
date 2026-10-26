#!/usr/bin/env python3
"""Sediakan potret AJK: latar putih + crop piawai laman.

Piawai: muka 0.50-0.56 daripada tinggi bingkai, garis mata ~0.40 dari atas, 480 px webp.

PENTING: pada build OpenCV VPS ini, `FaceDetectorYN` memberi kotak muka yang SALAH bila
imej > ~600 px (nisbah tersasar ~1.6x; amaran "graph engine"). Jadi semua ukuran dibuat
pada imej kecil 480 px, dan crop dikira dalam ruang PECAHAN (0-1) supaya boleh digunakan
pada imej kerja 2400 px.
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
UKUR = 480               # saiz ukuran yang boleh dipercayai
MUKA_SASARAN = 0.53
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


def ukur_muka(im: Image.Image):
    """Ukur muka pada saiz UKUR; pulangkan (x0f, y0f, wf, hf, mata_yf) dalam pecahan 0-1."""
    kecil = im.resize((UKUR, UKUR), Image.LANCZOS)
    bgr = cv2.cvtColor(np.array(kecil), cv2.COLOR_RGB2BGR)
    det = cv2.FaceDetectorYN.create(pastikan_yunet(), "", (UKUR, UKUR), 0.6, 0.3, 5000)
    _, muka = det.detect(bgr)
    if muka is None or len(muka) == 0:
        return None
    m = max(muka, key=lambda r: r[2] * r[3])
    x, y, w, h = (float(v) / UKUR for v in m[:4])
    mata_y = (float(m[5]) + float(m[7])) / 2.0 / UKUR
    return x, y, w, h, mata_y


def potong_pecahan(im: Image.Image, sisi: float, pusat_x: float, mata_y: float) -> Image.Image:
    W, H = im.size
    x0 = min(max(pusat_x - sisi / 2.0, 0.0), 1.0 - sisi)
    y0 = min(max(mata_y - sisi * MATA_SASARAN, 0.0), 1.0 - sisi)
    return im.crop((int(x0 * W), int(y0 * H), int((x0 + sisi) * W), int((y0 + sisi) * H)))


def crop_piawai(im: Image.Image) -> Image.Image:
    ukuran = ukur_muka(im)
    if not ukuran:
        raise SystemExit("Muka tidak dikesan")
    x, y, w, h, mata_y = ukuran
    sisi = h / MUKA_SASARAN
    pusat_x = x + w / 2.0
    print("ukur asal: muka w=%.3f h=%.3f mata=%.3f" % (w, h, mata_y))

    calon = None
    for i in range(8):
        calon = potong_pecahan(im, sisi, pusat_x, mata_y)
        semak = ukur_muka(calon)
        if not semak:
            raise SystemExit("Muka hilang selepas crop (pusingan %d)" % i)
        nisbah = semak[3]
        print("  pusingan %d: sisi=%.3f -> muka=%.3f mata=%.3f" % (i + 1, sisi, nisbah, semak[4]))
        if abs(nisbah - MUKA_SASARAN) <= 0.015:
            break
        sisi *= nisbah / MUKA_SASARAN

    return calon.resize((SAIZ, SAIZ), Image.LANCZOS)


def main():
    # Latar asal dikekalkan (Doc: "use original background, not white").
    asal = Image.open(SUMBER).convert("RGB")
    akhir = crop_piawai(asal)
    akhir.save(DEST, "WEBP", quality=86, method=6)
    semak = ukur_muka(akhir)
    print("fail: %s (%d px, %.0f KB)" % (DEST.name, akhir.width, DEST.stat().st_size / 1024))
    print("semakan akhir: muka %.2f bingkai, garis mata %.2f" % (semak[3], semak[4]))


if __name__ == "__main__":
    main()
