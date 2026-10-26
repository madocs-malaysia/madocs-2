#!/usr/bin/env python3
"""Ganti kandungan Prakata Presiden dengan teks rasmi daripada fail .docx.

Sumber: dokumen Presiden (25/10/2026). Skrip ini mengambil perenggan Bahasa Melayu dan
menambah terjemahan Inggeris rasmi (yang juga ada dalam dokumen yang sama) ke dalam kamus
data/terjemahan.json, supaya versi /en/ memaparkan tulisan Presiden sendiri — bukan
terjemahan mesin.
"""
import json
import re
import sys
from pathlib import Path

import docx

AKAR = Path('/home/ubuntu/madocs-site')
DOCX = Path(sys.argv[1]) if len(sys.argv) > 1 else None


def bersih(teks: str, bm: bool = True) -> str:
    teks = teks.replace('\u201c', '"').replace('\u201d', '"')
    teks = re.sub(r'\s+', ' ', teks).strip()
    if bm:
        teks = teks.replace('didalam', 'di dalam').replace('professional', 'profesional')
    teks = teks.replace('bermatlamat  ', 'bermatlamat ')
    return teks


def utama():
    d = docx.Document(str(DOCX))
    teks = [bersih(p.text, bm=(i < 30)) for i, p in enumerate(d.paragraphs) if p.text.strip()]

    # Pisahkan versi Melayu dan Inggeris pada penanda tajuk bahasa Inggeris.
    potong = next((i for i, t in enumerate(teks) if t.startswith('*PRESIDENT')), len(teks))
    bm, en = teks[:potong], teks[potong:]

    def ambil(blok, penanda_salam, penanda_tandatangan):
        salam = next(t for t in blok if t.startswith(penanda_salam))
        i_salam = blok.index(salam)
        i_tanda = next(i for i, t in enumerate(blok) if t.startswith(penanda_tandatangan))
        badan = blok[i_salam + 1:i_tanda]
        return salam, badan, blok[i_tanda:]

    salam_bm, badan_bm, ekor_bm = ambil(bm, 'Assalamualaikum', 'Dr Abdol Rashid')
    salam_en, badan_en, ekor_en = ambil(en, 'Assalamualaikum', 'Dr Abdol Rashid')

    # penutup = dua baris cogan kata sebelum tandatangan
    penutup_bm = [t for t in badan_bm if t.startswith('"') or t.lower().startswith('"')]
    badan_bm = [t for t in badan_bm if not (t.startswith('"'))]
    penutup_en = [t for t in badan_en if t.startswith('"')]
    badan_en = [t for t in badan_en if not (t.startswith('"'))]

    print('perenggan BM:', len(badan_bm), '| perenggan EN:', len(badan_en))
    if len(badan_bm) != len(badan_en):
        sys.exit('Bilangan perenggan BM dan EN tidak sepadan — semak dokumen.')

    p = AKAR / 'data' / 'prakata.json'
    asal = json.loads(p.read_text(encoding='utf-8'))
    asal.update({
        'tajuk': 'Dari Meja Presiden',
        'nama': 'Dr. Abdol Rashid bin Masrom',
        'label': 'Presiden Pertama',
        'jawatan': 'Presiden · Sesi 2026-2028',
        'salam': salam_bm.rstrip(','),
        'perenggan': badan_bm,
        'penutup': ' '.join(penutup_bm),
        'tarikh': '25 Oktober 2026',
        'tunjang': ['Peraturan dan garis panduan', 'Ilmu pengetahuan', 'Kemahiran klinikal'],
    })
    p.write_text(json.dumps(asal, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('prakata.json dikemas kini')

    k = AKAR / 'data' / 'terjemahan.json'
    kamus = json.loads(k.read_text(encoding='utf-8'))
    kamus[asal['salam']] = salam_en.rstrip(',')
    for bm_t, en_t in zip(badan_bm, badan_en):
        kamus[bm_t] = en_t
    if penutup_bm and penutup_en:
        kamus[' '.join(penutup_bm)] = ' '.join(penutup_en)
    kamus['25 Oktober 2026'] = '25 October 2026'
    kamus['Presiden · Sesi 2026-2028'] = 'President · 2026-2028 Term'
    kamus['Peraturan dan garis panduan'] = 'Regulation and guidelines'
    kamus['Ilmu pengetahuan'] = 'Knowledge'
    kamus['Kemahiran klinikal'] = 'Clinical skills'
    k.write_text(json.dumps(kamus, ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    print('terjemahan rasmi ditambah:', len(badan_bm) + 4, 'entri')


if __name__ == '__main__':
    utama()
