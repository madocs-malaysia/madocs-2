#!/usr/bin/env python3
"""Jana kad visual untuk aktiviti yang tiada gambar, supaya kad senarai tidak kosong.

Reka bentuk: latar maroon bergradien, garis emas halus, kod program, tajuk, tarikh dan
tempat, serta lambang MADOCS. Tiada gambar palsu daripada program lain.
"""
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

AKAR = Path('/home/ubuntu/madocs-site')
TUJUAN = AKAR / 'assets' / 'kad-aktiviti'
TUJUAN.mkdir(parents=True, exist_ok=True)
SAIZ = (1200, 630)

FON_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FON = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def gradien(saiz, atas, bawah):
    w, h = saiz
    im = Image.new('RGB', saiz)
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / max(1, h - 1)
        warna = tuple(int(atas[i] + (bawah[i] - atas[i]) * t) for i in range(3))
        d.line([(0, y), (w, y)], fill=warna)
    return im


def bina(kod, tajuk, tarikh, tempat, keluar):
    im = gradien(SAIZ, (81, 7, 22), (122, 13, 32))
    d = ImageDraw.Draw(im)

    # corak halus: lukis pada lapisan lutsinar, kemudian gabungkan (alpha betul)
    corak = Image.new('RGBA', SAIZ, (0, 0, 0, 0))
    dc = ImageDraw.Draw(corak)
    for x in range(-200, SAIZ[0] + 200, 46):
        dc.line([(x, 0), (x + 260, SAIZ[1])], fill=(255, 255, 255, 14), width=2)
    im = Image.alpha_composite(im.convert('RGBA'), corak).convert('RGB')
    d = ImageDraw.Draw(im)

    # garis emas
    d.rectangle([56, 56, SAIZ[0] - 56, SAIZ[1] - 56], outline=(212, 175, 110), width=2)

    f_kod = ImageFont.truetype(FON_BOLD, 26)
    f_tajuk = ImageFont.truetype(FON_BOLD, 56)
    f_meta = ImageFont.truetype(FON, 25)

    d.text((86, 92), kod.upper()[:20], font=f_kod, fill=(240, 205, 150))

    baris = textwrap.wrap(tajuk, width=23)[:2]
    y = 146
    for b in baris:
        d.text((86, y), b, font=f_tajuk, fill=(255, 255, 255))
        y += 66

    # tarikh & tempat di kanan bawah: kiri bawah disimpan untuk badge kategori
    teks = tarikh + (('  ·  ' + tempat[:32]) if tempat else '')
    lebar = d.textlength(teks, font=f_meta)
    d.text((SAIZ[0] - 86 - lebar, SAIZ[1] - 104), teks, font=f_meta, fill=(245, 220, 224))
    im.save(keluar, format='WEBP', quality=88, method=6)
    return keluar


BULAN = ['Januari', 'Februari', 'Mac', 'April', 'Mei', 'Jun', 'Julai', 'Ogos',
         'September', 'Oktober', 'November', 'Disember']


def utama():
    p = AKAR / 'data' / 'aktiviti.json'
    d = json.loads(p.read_text(encoding='utf-8'))
    dibuat = 0
    for a in d['aktiviti']:
        ada = (a.get('gambar') or '').strip()
        if ada and not ada.startswith('assets/kad-aktiviti/'):
            continue
        tahun, bulan, hari = (int(x) for x in a['tarikh'].split('-'))
        tarikh = '%d %s %d' % (hari, BULAN[bulan - 1], tahun)
        nama = '%s.webp' % a['slug']
        bina(a.get('kategori') or 'MADOCS', a['tajuk'], tarikh, a.get('tempat', ''), TUJUAN / nama)
        a['gambar'] = 'assets/kad-aktiviti/%s' % nama
        a['gambar_alt'] = 'Kad program %s, %s' % (a['tajuk'], tarikh)
        dibuat += 1
        print('kad:', a['slug'])
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('kad dijana:', dibuat)


if __name__ == '__main__':
    utama()
