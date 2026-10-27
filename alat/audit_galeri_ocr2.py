#!/usr/bin/env python3
"""Audit OCR selari (8 pekerja) untuk mengesan data peribadi dalam gambar galeri."""
import json
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
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
    'kata_kunci': re.compile(r'(no\.?\s*k/?p|kad pengenalan|nombor telefon|no\.?\s*telefon|alamat|senarai nama|senarai peserta|pesakit)', re.I),
    'nama_doktor': re.compile(r'\b(DR|DRS)\.?\s+[A-Z][A-Za-z]+', re.I),
}


def ocr(fail: Path) -> dict:
    try:
        with Image.open(fail) as im:
            im = im.convert('L')
            if im.width < 1000:
                im = im.resize((1000, int(im.height * 1000 / im.width)), Image.LANCZOS)
            im = ImageOps.autocontrast(im)
            with tempfile.NamedTemporaryFile(suffix='.png', delete=True) as tmp:
                im.save(tmp.name)
                r = subprocess.run(['tesseract', tmp.name, 'stdout', '-l', 'eng', '--psm', '3'],
                                   capture_output=True, text=True, timeout=120)
            teks = r.stdout or ''
    except Exception as e:
        return {'fail': str(fail.relative_to(AKAR)), 'ralat': str(e)[:80], 'jumpa': {}}
    jumpa = {}
    for nama, pola in POLA.items():
        cari = sorted(set(pola.findall(teks)))
        if cari:
            jumpa[nama] = cari[:6]
    return {'fail': str(fail.relative_to(AKAR)), 'jumpa': jumpa, 'teks': teks.strip()[:400]}


def utama():
    fail = sorted(p for p in GALERI.rglob('*.webp') if not p.stem.endswith('-kecil'))
    print('gambar:', len(fail), flush=True)
    hasil = []
    with ThreadPoolExecutor(max_workers=2) as ex:
        for i, h in enumerate(ex.map(ocr, fail), 1):
            hasil.append(h)
            if h['jumpa']:
                print(f"⚠ {h['fail']} -> {h['jumpa']}", flush=True)
            if i % 50 == 0:
                print(f'  {i}/{len(fail)}', flush=True)
    KELUAR.write_text(json.dumps(hasil, ensure_ascii=False, indent=1), encoding='utf-8')
    bersalah = [h for h in hasil if h['jumpa']]
    print(f'SELESAI: {len(bersalah)} gambar mempunyai penanda.')
    for h in bersalah:
        print('  -', h['fail'], list(h['jumpa']))


if __name__ == '__main__':
    utama()
