#!/usr/bin/env python3
"""Audit OCR semua gambar galeri MADOCS untuk mengesan data peribadi.

Dikesan: nombor kad pengenalan (12 digit / format ######-##-####), nombor telefon,
e-mel, dan perkataan berkaitan senarai nama peserta ("nama", "no. k/p", "telefon",
"alamat", "senarai").

Keputusan → /home/ubuntu/.hermes/profiles/madocs/cache/scratch/audit-galeri-ocr.json
"""
import json
import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

AKAR = Path('/home/ubuntu/madocs-site')
GALERI = AKAR / 'assets' / 'galeri'
KELUAR = Path('/home/ubuntu/.hermes/profiles/madocs/cache/scratch/audit-galeri-ocr.json')

POLA = {
    'ic_bertanda': re.compile(r'\b\d{6}-\d{2}-\d{4}\b'),
    'ic_12digit': re.compile(r'\b\d{12}\b'),
    'telefon': re.compile(r'\b01\d[\s-]?\d{3,4}[\s-]?\d{4}\b'),
    'emel': re.compile(r'[\w.+-]+@[\w-]+\.[\w.]{2,}'),
    'kata_kunci': re.compile(r'\b(no\.?\s*k/?p|kad pengenalan|nombor telefon|no\.?\s*telefon|alamat|senarai nama|senarai peserta)\b', re.I),
}


def ocr(fail: Path) -> str:
    try:
        with Image.open(fail) as im:
            im = im.convert('L')
            if im.width < 1200:
                skala = 1200 / im.width
                im = im.resize((1200, int(im.height * skala)), Image.LANCZOS)
            im = ImageOps.autocontrast(im)
            with tempfile.NamedTemporaryFile(suffix='.png', delete=True) as tmp:
                im.save(tmp.name)
                hasil = subprocess.run(
                    ['tesseract', tmp.name, 'stdout', '-l', 'eng+msa', '--psm', '6'],
                    capture_output=True, text=True, timeout=120)
            return hasil.stdout or ''
    except Exception as e:
        return '__RALAT__' + str(e)[:80]


def utama():
    fail = sorted(p for p in GALERI.rglob('*.webp') if not p.stem.endswith('-kecil'))
    print('gambar untuk diaudit:', len(fail), flush=True)
    hasil = {}
    for i, f in enumerate(fail, 1):
        teks = ocr(f)
        jumpa = {nama: sorted(set(pola.findall(teks)))[:5] for nama, pola in POLA.items()
                 if pola.search(teks)}
        hasil[str(f.relative_to(AKAR))] = {'jumpa': jumpa, 'teks': teks.strip()[:600]}
        if jumpa:
            print(f'[{i}/{len(fail)}] ⚠ {f.relative_to(AKAR)} -> {jumpa}', flush=True)
        elif i % 25 == 0:
            print(f'[{i}/{len(fail)}] diproses', flush=True)
    KELUAR.write_text(json.dumps(hasil, ensure_ascii=False, indent=1), encoding='utf-8')
    bersalah = [k for k, v in hasil.items() if v['jumpa']]
    print('SELESAI. Gambar dengan penanda data: %d' % len(bersalah))
    for k in bersalah:
        print('  -', k, hasil[k]['jumpa'])


if __name__ == '__main__':
    utama()
