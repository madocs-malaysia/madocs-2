"""Jadikan gambar berkumpulan PCC2-3 sebagai gambar muka depan (cover) album galeri."""
import json
from pathlib import Path

from PIL import Image

SUMBER = Path('/home/ubuntu/.hermes/profiles/madocs/cache/documents/native-inputs/7bff500835d25829a15db13237ac59fa6d6618aa1011e0fe774faf5ef970c673/img_8af04d3e4244.jpg')
AKAR = Path('/home/ubuntu/madocs-site')
DEST = AKAR / 'assets' / 'galeri' / 'pcc2-3-putrajaya-2026' / '06.webp'
ALT = 'Gambar berkumpulan peserta dan fasilitator Kursus PCC2-3 di Masjid Putra, Putrajaya'

im = Image.open(SUMBER).convert('RGB')
print('asal:', im.size)
if im.width > 1400:
    im = im.resize((1400, round(im.height * 1400 / im.width)), Image.LANCZOS)
im.save(DEST, format='WEBP', quality=86, method=6)
print('disimpan:', im.size, DEST.stat().st_size, 'bait')

p = AKAR / 'data' / 'galeri.json'
d = json.loads(p.read_text(encoding='utf-8'))
for a in d['album']:
    if a['slug'] != 'pcc2-3-putrajaya-2026':
        continue
    a['gambar'] = [g for g in a['gambar'] if not g['src'].endswith('06.webp')]
    a['gambar'].insert(0, {'src': 'assets/galeri/pcc2-3-putrajaya-2026/06.webp', 'alt': ALT})
    print('gambar dalam album:', len(a['gambar']), '| cover:', a['gambar'][0]['src'])
p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

t = AKAR / 'data' / 'terjemahan.json'
kamus = json.loads(t.read_text(encoding='utf-8'))
kamus[ALT] = 'Group photograph of participants and facilitators of the PCC2-3 course at Putra Mosque, Putrajaya'
t.write_text(json.dumps(kamus, ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8')
print('terjemahan alt ditambah')
