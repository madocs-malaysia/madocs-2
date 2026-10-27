"""Ganti gambar hero aktiviti yang tidak berkaitan (bangunan) dengan gambar program sebenar."""
import json
from pathlib import Path

AKAR = Path('/home/ubuntu/madocs-site')

TUKAR = {
    '2026-09-17-pelancaran-garis-panduan': {
        'gambar': 'assets/galeri/pelancaran-2026/06.webp',
        'gambar_alt': ('Stand pelancaran Buku Garis Panduan Berkhatan (Lelaki) 2026 di majlis pelancaran '
                       'rasmi Kementerian Kesihatan Malaysia'),
    },
    '2026-09-16-mesyuarat-ajk-bil2': {
        'gambar': 'assets/galeri/mesyuarat-ajk-2026/01.webp',
        'gambar_alt': 'Ahli jawatankuasa dalam perbincangan mesyuarat',
    },
    '2026-08-10-lawatan-klinik-indonesia': {
        'gambar': 'assets/galeri/teknoklem-depok-2025/01.webp',
        'gambar_alt': 'Peserta bengkel Teknoklem dan Teknosealer di Klinik Tekno Sunat Junior',
    },
    '2023-09-17-perak-circumcision-update': {
        'gambar': '',
        'gambar_alt': '',
    },
}

p = AKAR / 'data' / 'aktiviti.json'
d = json.loads(p.read_text(encoding='utf-8'))
ditukar = []
for a in d['aktiviti']:
    if a['slug'] in TUKAR:
        lama = a.get('gambar', '')
        a.update(TUKAR[a['slug']])
        ditukar.append((a['slug'], lama or '(tiada)', a['gambar'] or '(tiada)'))
p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
for s, l, b in ditukar:
    print(f'{s}\n   {l} -> {b}')

# buang terjemahan alt lama yang tidak lagi digunakan
t = AKAR / 'data' / 'terjemahan.json'
kamus = json.loads(t.read_text(encoding='utf-8'))
for kunci in ('Papan tanda Hospital Shah Alam tempat majlis berlangsung',
              'Bangunan tempat berlangsungnya mesyuarat',
              'Peralatan klinikal disusun di atas meja semasa lawatan'):
    kamus.pop(kunci, None)
kamus['Ahli jawatankuasa dalam perbincangan mesyuarat'] = 'Committee members in meeting discussion'
kamus['Peserta bengkel Teknoklem dan Teknosealer di Klinik Tekno Sunat Junior'] = (
    'Participants of the Teknoklem and Teknosealer workshop at Klinik Tekno Sunat Junior')
t.write_text(json.dumps(kamus, ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8')
print('terjemahan dikemas')
