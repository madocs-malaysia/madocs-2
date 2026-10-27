"""Masukkan gambar pelancaran Garis Panduan Berkhatan 2026 (buku/stand) ke galeri + hero depan."""
import json
from pathlib import Path

from PIL import Image

SUMBER = Path('/home/ubuntu/.hermes/profiles/madocs/cache/documents/native-inputs/13fd5e3f8103761ee693126699c60f0aca6bc749a47825d6b993fa63be293de2/img_ed7ace4d7d1b.jpg')
AKAR = Path('/home/ubuntu/madocs-site')
DEST = AKAR / 'assets' / 'galeri' / 'pelancaran-2026' / '06.webp'
ALT = ('Stand pelancaran Buku Garis Panduan Berkhatan (Lelaki) 2026 di majlis pelancaran rasmi '
       'Kementerian Kesihatan Malaysia')

im = Image.open(SUMBER).convert('RGB')
if im.width > 1400:
    im = im.resize((1400, round(im.height * 1400 / im.width)), Image.LANCZOS)
im.save(DEST, format='WEBP', quality=85, method=6)
print('imej:', im.size, DEST.stat().st_size, 'bait')

# 1) galeri
g = AKAR / 'data' / 'galeri.json'
d = json.loads(g.read_text(encoding='utf-8'))
for a in d['album']:
    if a['slug'] == 'pelancaran-2026':
        a['gambar'] = [x for x in a['gambar'] if not x['src'].endswith('06.webp')]
        a['gambar'].append({'src': 'assets/galeri/pelancaran-2026/06.webp', 'alt': ALT})
g.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print('galeri: pelancaran-2026 kini', len([x for a in d['album'] if a['slug'] == 'pelancaran-2026' for x in a['gambar']]), 'gambar')

# 2) hero: letak sebagai slaid pertama
h = AKAR / 'alat' / 'bina_hero.py'
s = h.read_text(encoding='utf-8')
baris = ("    ('assets/galeri/pelancaran-2026/06.webp', 'garis-panduan', 0.42,\n"
         "     'Stand pelancaran Buku Garis Panduan Berkhatan (Lelaki) 2026 di majlis pelancaran rasmi Kementerian Kesihatan Malaysia'),\n")
if 'garis-panduan' not in s:
    s = s.replace('GAMBAR = [\n', 'GAMBAR = [\n' + baris, 1)
    h.write_text(s, encoding='utf-8')
    print('bina_hero.py: slaid pertama ditambah')
else:
    print('bina_hero.py: sudah ada')

# 3) terjemahan alt
t = AKAR / 'data' / 'terjemahan.json'
kamus = json.loads(t.read_text(encoding='utf-8'))
kamus[ALT] = ('Stand for the launch of the 2026 Circumcision Guidelines (Male) book at the official '
              'launch by the Ministry of Health Malaysia')
t.write_text(json.dumps(kamus, ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8')
print('terjemahan alt ditambah')
