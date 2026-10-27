"""Tambah gambar taklimat PCC2-3 Putrajaya ke album galeri."""
import json
from pathlib import Path

from PIL import Image

SUMBER = Path('/home/ubuntu/.hermes/profiles/madocs/cache/documents/native-inputs/9bfbdb817d31c038e0d395cbc7141c9a8f1ff3941c1f4f733392fee0190c60fc/img_c8c976af765b.jpg')
AKAR = Path('/home/ubuntu/madocs-site')
DEST = AKAR / 'assets' / 'galeri' / 'pcc2-3-putrajaya-2026' / '07.webp'
ALT = ('Peserta kursus PCC2-3 mendengar taklimat di dalam dewan Masjid Putra, Putrajaya, '
       'sebelum sesi latihan amali bermula')

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
    a['gambar'] = [g for g in a['gambar'] if not g['src'].endswith('07.webp')]
    a['gambar'].append({'src': 'assets/galeri/pcc2-3-putrajaya-2026/07.webp', 'alt': ALT})
    print('album kini', len(a['gambar']), 'gambar | cover kekal:', a['gambar'][0]['src'])
p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

t = AKAR / 'data' / 'terjemahan.json'
kamus = json.loads(t.read_text(encoding='utf-8'))
kamus[ALT] = ('PCC2-3 participants listening to a briefing in the hall at Putra Mosque, Putrajaya, '
              'before the hands-on session begins')
t.write_text(json.dumps(kamus, ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8')
print('terjemahan alt ditambah')
