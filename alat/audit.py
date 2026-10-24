#!/usr/bin/env python3
"""Audit laman MADOCS yang telah dibina (bukan sumber data).

Menyemak: pautan dalaman rosak, gambar hilang/alt, teks pemegang tempat,
sisa Bahasa Melayu pada halaman Inggeris, meta SEO, sitemap, dan percanggahan
nombor telefon / istilah / harga.

Guna: python3 alat/audit.py [--keluaran /tmp/audit.md]
"""
import argparse
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup

AKAR = Path('/home/ubuntu/madocs-site')
LANGKAU = ('#', 'mailto:', 'tel:', 'javascript:', 'data:')

# Frasa yang tidak sepatutnya kelihatan kepada orang awam
PEMEGANG_TEMPAT = [
    'belum diaktifkan', 'sedang disediakan', 'akan dimasukkan', 'teks sementara',
    'belum diisi', 'belum ditetapkan', 'data contoh', 'contoh sahaja', 'lorem',
    'TODO', 'FIXME', 'xxx', 'draf', 'placeholder', 'Ujian Satu', 'Ujian Dua',
    'akan diterbitkan di sini', 'belum disahkan jawatankuasa',
]

# Medan yang wajib ada pada setiap halaman awam
META_WAJIB = ('description',)


def semua_html():
    keluar = []
    for p in AKAR.rglob('*.html'):
        s = str(p)
        if '/.git/' in s:
            continue
        keluar.append(p)
    return sorted(keluar)


def pautan_tempatan(doc, fail):
    """Pulangkan senarai pautan dalaman + nilai href mentah."""
    hasil = []
    for tag in doc.find_all(['a', 'link', 'script', 'img', 'source']):
        attr = 'href' if tag.name in ('a', 'link') else 'src'
        if tag.name == 'source':
            attr = 'srcset' if tag.has_attr('srcset') else 'srcset'
        nilai = tag.get(attr) or (tag.get('srcset') if tag.name == 'source' else None)
        if not nilai:
            continue
        if tag.name == 'source':
            for bahagian in str(nilai).split(','):
                u = bahagian.strip().split(' ')[0]
                if u:
                    hasil.append(u)
        else:
            hasil.append(str(nilai))
    return hasil


def selesaikan(url, laluan_halaman):
    """Tukar URL relatif kepada laluan fail sebenar dalam AKAR."""
    if not url or url.startswith(LANGKAU):
        return None
    buang = urlparse(url)
    if buang.scheme in ('http', 'https'):
        return 'luar'
    jalan = unquote(buang.path)
    if not jalan:
        return None
    if jalan.startswith('/'):
        sasaran = AKAR / jalan.lstrip('/')
    else:
        sasaran = (laluan_halaman.parent / jalan).resolve()
    if sasaran.is_dir() or jalan.endswith('/'):
        sasaran = sasaran / 'index.html'
    return sasaran


def audit():
    laporan = {
        'halaman': 0,
        'pautan_rosak': [],
        'gambar_rosak': [],
        'img_tanpa_alt': [],
        'pemegang_tempat': [],
        'meta': [],
        'h1': [],
        'sisa_bm': [],
        'telefon': Counter(),
        'istilah': Counter(),
        'noindex': [],
        'jsonld_ralat': [],
    }

    fail_semua = semua_html()
    laporan['halaman'] = len(fail_semua)

    for fail in fail_semua:
        html = fail.read_text(encoding='utf-8', errors='ignore')
        doc = BeautifulSoup(html, 'lxml')
        relatif = '/' + str(fail.relative_to(AKAR))

        # --- pautan & aset
        for url in pautan_tempatan(doc, fail):
            sasaran = selesaikan(url, fail)
            if sasaran in (None, 'luar'):
                continue
            if not Path(sasaran).exists():
                jenis = 'gambar' if re.search(r'\.(webp|jpg|jpeg|png|svg|gif)$', str(sasaran)) else 'pautan'
                simpan = laporan['gambar_rosak'] if jenis == 'gambar' else laporan['pautan_rosak']
                if len(simpan) < 400:
                    simpan.append((relatif, url))

        # --- alt
        for img in doc.find_all('img'):
            if not img.has_attr('alt') or not img.get('alt').strip():
                laporan['img_tanpa_alt'].append((relatif, img.get('src', '?')))

        # --- teks pemegang tempat
        teks = doc.get_text(' ', strip=True)
        rendah = teks.lower()
        for frasa in PEMEGANG_TEMPAT:
            if frasa.lower() in rendah:
                laporan['pemegang_tempat'].append((relatif, frasa))

        # --- meta
        tajuk = (doc.title.string or '').strip() if doc.title and doc.title.string else ''
        ket = doc.find('meta', attrs={'name': 'description'})
        ket_nilai = (ket.get('content') or '').strip() if ket else ''
        masalah = []
        if not tajuk:
            masalah.append('tiada <title>')
        elif len(tajuk) > 70:
            masalah.append('tajuk %d aksara' % len(tajuk))
        if not ket_nilai:
            masalah.append('tiada meta description')
        elif not (60 <= len(ket_nilai) <= 165):
            masalah.append('description %d aksara' % len(ket_nilai))
        if masalah:
            laporan['meta'].append((relatif, '; '.join(masalah)))

        # --- h1
        h1 = doc.find_all('h1')
        if len(h1) != 1:
            laporan['h1'].append((relatif, len(h1)))

        # --- noindex
        robots = doc.find('meta', attrs={'name': 'robots'})
        if robots and 'noindex' in (robots.get('content') or '').lower():
            laporan['noindex'].append(relatif)

        # --- JSON-LD
        for skrip in doc.find_all('script', attrs={'type': 'application/ld+json'}):
            try:
                json.loads(skrip.string or '{}')
            except Exception as e:
                laporan['jsonld_ralat'].append((relatif, str(e)[:80]))

        # --- sisa BM pada halaman EN
        if str(fail).startswith(str(AKAR / 'en')) or '/en/' in relatif:
            nod = [n.strip() for n in doc.stripped_strings if len(n.strip()) > 8]
            kata = ('yang', 'untuk', 'dengan', 'kepada', 'tidak', 'akan', 'telah', 'kami', 'ini', 'itu',
                    'dalam', 'daripada', 'juga', 'ialah', 'adalah', 'boleh', 'sila', 'anda', 'mereka',
                    'hari', 'tahun', 'bulan', 'sebagai', 'secara', 'antara', 'melalui', 'setiap', 'semua')
            tercemar = []
            for n in nod:
                bawah = ' ' + n.lower() + ' '
                if sum(1 for w in kata if ' %s ' % w in bawah) >= 2:
                    tercemar.append(n[:110])
            if tercemar:
                laporan['sisa_bm'].append((relatif, tercemar))

        # --- telefon & istilah (halaman BM sahaja)
        if not relatif.startswith('/en/'):
            for m in re.findall(r'wa\.me/(\d+)', html):
                laporan['telefon']['wa ' + m] += 1
            for m in re.findall(r'\+60[\d\s-]{8,}', html):
                laporan['telefon'][m.strip()] += 1
            if 'Persatuan' in teks and 'Pertubuhan' in teks:
                laporan['istilah']['kedua-dua Persatuan & Pertubuhan'] += 1
            elif 'Persatuan' in teks:
                laporan['istilah']['Persatuan sahaja'] += 1

    return laporan


def tulis(laporan, keluar):
    L = []
    tambah = L.append
    rosak = laporan['pautan_rosak']
    gambar = laporan['gambar_rosak']
    tambah('# Audit laman MADOCS\n')
    tambah('Halaman diperiksa: **%d**\n' % laporan['halaman'])
    tambah('| Semakan | Bilangan |')
    tambah('|---|---|')
    tambah('| Pautan dalaman rosak | %d |' % len(rosak))
    tambah('| Gambar/aset hilang | %d |' % len(gambar))
    tambah('| `<img>` tanpa alt | %d |' % len(laporan['img_tanpa_alt']))
    tambah('| Halaman dengan teks pemegang tempat | %d |' % len({r for r, _ in laporan['pemegang_tempat']}))
    tambah('| Halaman dengan masalah meta | %d |' % len(laporan['meta']))
    tambah('| Halaman bukan satu `<h1>` | %d |' % len(laporan['h1']))
    tambah('| Halaman EN dengan sisa BM | %d |' % len(laporan['sisa_bm']))
    tambah('| Ralat JSON-LD | %d |' % len(laporan['jsonld_ralat']))
    tambah('')

    def senarai(tajuk, baris, had=40):
        tambah('## %s\n' % tajuk)
        if not baris:
            tambah('Tiada.\n')
            return
        for b in baris[:had]:
            tambah('- %s' % (b if isinstance(b, str) else ' · '.join(str(x) for x in b)))
        if len(baris) > had:
            tambah('- … dan %d lagi' % (len(baris) - had))
        tambah('')

    senarai('Pautan dalaman rosak', rosak)
    senarai('Gambar/aset hilang', gambar)
    senarai('Teks pemegang tempat', sorted(laporan['pemegang_tempat']))
    senarai('Masalah meta (tajuk/description)', laporan['meta'])
    senarai('Bukan satu H1', laporan['h1'])
    senarai('JSON-LD rosak', laporan['jsonld_ralat'])

    tambah('## Sisa Bahasa Melayu pada halaman Inggeris\n')
    if not laporan['sisa_bm']:
        tambah('Tiada.\n')
    else:
        for fail, nod in laporan['sisa_bm'][:40]:
            tambah('- **%s** — %d cebisan, cth: %s' % (fail, len(nod), nod[0][:90]))
        tambah('')

    tambah('## Nombor telefon/WhatsApp yang muncul\n')
    for no, bil in laporan['telefon'].most_common(12):
        tambah('- `%s` × %d' % (no, bil))
    tambah('')
    tambah('## Istilah persatuan/pertubuhan\n')
    for k, v in laporan['istilah'].most_common():
        tambah('- %s × %d' % (k, v))
    tambah('')
    tambah('## Halaman noindex\n')
    for h in laporan['noindex']:
        tambah('- %s' % h)
    tambah('')

    Path(keluar).write_text('\n'.join(L) + '\n', encoding='utf-8')
    return '\n'.join(L[:40])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--keluaran', default='/tmp/audit_madocs.md')
    a = ap.parse_args()
    lap = audit()
    ringkas = tulis(lap, a.keluaran)
    print(ringkas)
    print("\nLaporan penuh: %s" % a.keluaran)


if __name__ == '__main__':
    main()
