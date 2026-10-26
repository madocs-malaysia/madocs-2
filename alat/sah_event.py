"""Sahkan semua blok Event dalam HTML terbina: medan wajib dan tarikh yang betul."""
import json
import re
from pathlib import Path

AKAR = Path('/home/ubuntu/madocs-site')
wajib = ('name', 'startDate', 'location', 'organizer')
masalah = []
jumlah = 0
for f in AKAR.rglob('*.html'):
    if '.git' in f.parts:
        continue
    teks = f.read_text(encoding='utf-8')
    for blok in re.findall(r'<script type="application/ld\+json">(\{.*?\})</script>', teks, re.S):
        try:
            d = json.loads(blok)
        except Exception:
            masalah.append((str(f.relative_to(AKAR)), 'JSON tidak sah'))
            continue
        if d.get('@type') != 'Event':
            continue
        jumlah += 1
        hilang = [k for k in wajib if not d.get(k)]
        if hilang:
            masalah.append((str(f.relative_to(AKAR)), 'hilang: ' + ', '.join(hilang)))
        tarikh = d.get('startDate', '')
        if not re.match(r'^\d{4}-\d{2}-\d{2}', tarikh):
            masalah.append((str(f.relative_to(AKAR)), 'startDate bukan ISO: %r' % tarikh))
        if d.get('endDate') and d['endDate'] < tarikh:
            masalah.append((str(f.relative_to(AKAR)), 'endDate sebelum startDate'))
        alamat = (d.get('location') or {}).get('address') or {}
        if not alamat.get('addressCountry'):
            masalah.append((str(f.relative_to(AKAR)), 'location.address tiada addressCountry'))
print('Blok Event diperiksa: %d | masalah: %d' % (jumlah, len(masalah)))
for m in masalah:
    print('  -', m[0], '|', m[1])
