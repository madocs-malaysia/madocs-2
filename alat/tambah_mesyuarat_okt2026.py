#!/usr/bin/env python3
"""Masukkan gambar Mesyuarat AJK 27 Oktober 2026 (Qasar Balqis) ke galeri.

Semakan sensitiviti sudah dibuat: OCR tidak menemui teks pada mana-mana gambar, dan
semakan visual pada skrin komputer riba serta kertas di meja tidak menunjukkan senarai
nama, nombor IC atau nombor telefon yang boleh dibaca.
"""
import json
from pathlib import Path

from PIL import Image

SUMBER = Path('/tmp/zip-mtg')
AKAR = Path('/home/ubuntu/madocs-site')
TUJUAN = AKAR / 'assets' / 'galeri' / 'mesyuarat-ajk-okt-2026'
TUJUAN.mkdir(parents=True, exist_ok=True)

PILIHAN = [
    ('Mesyuarat_AJK_MADOCS_27Okt2026_1.jpg', '01.webp',
     'Pengerusi mesyuarat meneliti kertas cadangan semasa mesyuarat AJK MADOCS',
     'The chair reviewing working papers during the MADOCS committee meeting'),
    ('Mesyuarat_AJK_MADOCS_27Okt2026_2.jpg', '02.webp',
     'Ahli jawatankuasa berbincang semasa mesyuarat di Qasar Balqis, Ampang',
     'Committee members in discussion during the meeting at Qasar Balqis, Ampang'),
    ('Mesyuarat_AJK_MADOCS_27Okt2026_3.jpg', '03.webp',
     'Dua ahli jawatankuasa meneliti dokumen mesyuarat',
     'Two committee members reviewing meeting documents'),
    ('Mesyuarat_AJK_MADOCS_27Okt2026_4.jpg', '04.webp',
     'Ahli jawatankuasa dalam perbincangan di meja mesyuarat',
     'Committee members in discussion at the meeting table'),
    ('Mesyuarat_AJK_MADOCS_27Okt2026_5.jpg', '05.webp',
     'Ahli jawatankuasa bergambar bersama sebelum mesyuarat bermula',
     'Committee members photographed together before the meeting began'),
    ('Mesyuarat_AJK_MADOCS_27Okt2026_6.jpg', '06.webp',
     'Gambar berkumpulan ahli jawatankuasa MADOCS selepas mesyuarat',
     'Group photograph of MADOCS committee members after the meeting'),
]

ALBUM = {
    'slug': 'mesyuarat-ajk-okt-2026',
    'tajuk': 'Mesyuarat Ahli Jawatankuasa, 27 Oktober 2026',
    'tarikh': '2026-10-27',
    'kategori': 'Mesyuarat',
    'ringkas': ('Mesyuarat ahli jawatankuasa MADOCS di Qasar Balqis Restaurant, Ampang, '
                'Kuala Lumpur. Perbincangan meliputi kertas kerja program, kursus dan '
                'persiapan mesyuarat agung tahunan.'),
}
ALBUM_EN = ('MADOCS committee meeting at Qasar Balqis Restaurant, Ampang, Kuala Lumpur. '
            'Discussion covered programme papers, courses and preparations for the annual '
            'general meeting.')


def utama():
    gambar = []
    for sumber, nama, alt, _alt_en in PILIHAN:
        asal = SUMBER / sumber
        if not asal.exists():
            print('tiada:', sumber)
            continue
        with Image.open(asal) as im:
            im = im.convert('RGB')
            if im.width > 1400:
                im = im.resize((1400, round(im.height * 1400 / im.width)), Image.LANCZOS)
            im.save(TUJUAN / nama, format='WEBP', quality=85, method=6)
        gambar.append({'src': 'assets/galeri/mesyuarat-ajk-okt-2026/%s' % nama, 'alt': alt})
    print('gambar diproses:', len(gambar))

    p = AKAR / 'data' / 'galeri.json'
    d = json.loads(p.read_text(encoding='utf-8'))
    d['album'] = [a for a in d['album'] if a['slug'] != ALBUM['slug']]
    d['album'].append({**ALBUM, 'gambar': gambar})
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('album ditambah:', ALBUM['slug'], len(gambar), 'gambar')

    t = AKAR / 'data' / 'terjemahan.json'
    kamus = json.loads(t.read_text(encoding='utf-8'))
    kamus[ALBUM['tajuk']] = 'Committee Meeting, 27 October 2026'
    kamus[ALBUM['ringkas']] = ALBUM_EN
    for _s, _n, alt, alt_en in PILIHAN:
        kamus[alt] = alt_en
    t.write_text(json.dumps(kamus, ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    print('terjemahan ditambah')


if __name__ == '__main__':
    utama()
