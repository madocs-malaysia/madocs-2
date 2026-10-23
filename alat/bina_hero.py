#!/usr/bin/env python3
"""Hasilkan slaid hero (roulette) daripada gambar galeri DAN semua berita.

Keluaran:
  assets/hero/<nama>-besar.webp    (1400x1015)
  assets/hero/<nama>-telefon.webp  (1100x733)
  data/hero.json                   (gambar prosedur + SEMUA berita, berselang-seli)

Semua berita dalam data/berita.json masuk roulette secara automatik — jangan edit
hero.json dengan tangan.
"""
import json
import os
from PIL import Image, ImageDraw, ImageFilter

AKAR = '/home/ubuntu/madocs-site'
BESAR = (1400, 1015)
TELEFON = (1100, 733)
SELANG = 6

# Gambar prosedur/klinikal (bukan berita). Fokus menegak 0=puncak 1=dasar.
GAMBAR = [
    ('assets/galeri/ccc6-cheras-2025/09.webp', 'sop-briefing', 0.42,
     'Fasilitator MADOCS menerangkan Standard Operating Procedure (SOP) berkhatan pada skrin besar semasa kursus CCC di Hotel Maluri, Cheras'),
    ('assets/galeri/pcc1-2-kota-kinabalu-2026/05.webp', 'dorsal-slit', 0.38,
     'Penceramah menerangkan langkah-langkah prosedur Dorsal Slit pada slaid semasa kursus PCC di Kota Kinabalu'),
    ('assets/galeri/batu-pahat-2025/13.webp', 'instrumen', 0.72,
     'Petugas menyediakan dulang instrumen steril sebelum sesi penilaian PCC2-1 di The Katerina Hotel, Batu Pahat'),
    ('assets/galeri/ccc6-cheras-2025/07.webp', 'peranti', 0.40,
     'Booth pameran peranti berkhatan dengan sepanduk perbandingan kaedah semasa program CME MADOCS'),
    ('assets/galeri/ccc6-cheras-2025/06.webp', 'anatomi', 0.34,
     'Penceramah menerangkan anatomi dan anestesia tempatan kepada peserta kursus CCC6 di Hotel Maluri, Cheras'),
]

# Berita yang gambarnya poster menegak: dipaparkan sebagai kad pada latar gelap.
POSTER = {'2026-11-24-cme-tissue-adhesive'}


def potong(im, saiz, fokus_y=0.4):
    """Crop cover mengikut nisbah sasaran, kemudian resize + sharpen ringan."""
    lw, lh = saiz
    nisbah = lw / lh
    w, h = im.size
    if w / h > nisbah:               # terlalu lebar → potong kiri kanan
        baru_w = int(h * nisbah)
        x = (w - baru_w) // 2
        kotak = (x, 0, x + baru_w, h)
    else:                             # terlalu tinggi → potong atas bawah
        baru_h = int(w / nisbah)
        y = int((h - baru_h) * fokus_y)
        kotak = (0, y, w, y + baru_h)
    keluar = im.crop(kotak).resize(saiz, Image.LANCZOS)
    return keluar.filter(ImageFilter.UnsharpMask(radius=1.6, percent=110, threshold=3))


def slaid_poster(im, saiz):
    """Poster menegak: latar kabur gelap + poster di kiri (kad teks berada di kanan)."""
    lw, lh = saiz
    latar = potong(im, saiz, 0.35).filter(ImageFilter.GaussianBlur(38))
    latar = Image.blend(latar, Image.new('RGB', saiz, '#2c0308'), 0.55)

    tinggi = int(lh * 0.78)
    lebar = int(im.width * tinggi / im.height)
    poster = im.resize((lebar, tinggi), Image.LANCZOS)
    x = int(lw * 0.05)
    y = (lh - tinggi) // 2

    bayang = Image.new('RGBA', saiz, (0, 0, 0, 0))
    ImageDraw.Draw(bayang).rectangle(
        [x + 12, y + 16, x + lebar + 12, y + tinggi + 16], fill=(0, 0, 0, 130))
    latar = Image.alpha_composite(
        latar.convert('RGBA'), bayang.filter(ImageFilter.GaussianBlur(20))).convert('RGB')
    latar.paste(poster, (x, y))
    return latar


def main():
    hero_dir = os.path.join(AKAR, 'assets', 'hero')
    os.makedirs(hero_dir, exist_ok=True)

    slaid_gambar = []
    for src, nama, fokus, alt in GAMBAR:
        laluan = os.path.join(AKAR, src)
        if not os.path.exists(laluan):
            print('TIADA:', src)
            continue
        im = Image.open(laluan).convert('RGB')
        for saiz, akhiran in ((TELEFON, 'telefon'), (BESAR, 'besar')):
            potong(im, saiz, fokus).save(
                os.path.join(hero_dir, '%s-%s.webp' % (nama, akhiran)), 'WEBP', quality=82, method=6)
        slaid_gambar.append({'jenis': 'imej',
                             'besar': 'assets/hero/%s-besar.webp' % nama,
                             'telefon': 'assets/hero/%s-telefon.webp' % nama,
                             'alt': alt})
        print('imej   %-14s siap' % nama)

    slaid_berita = []
    berita = json.load(open(os.path.join(AKAR, 'data', 'berita.json'), encoding='utf-8'))['berita']
    for b in berita:
        g = b.get('gambar')
        if not g or not os.path.exists(os.path.join(AKAR, g)):
            print('berita tanpa gambar dilangkau:', b['slug'])
            continue
        nama = 'berita-' + b['slug']
        im = Image.open(os.path.join(AKAR, g)).convert('RGB')
        poster = b['slug'] in POSTER
        for saiz, akhiran in ((TELEFON, 'telefon'), (BESAR, 'besar')):
            out = slaid_poster(im, saiz) if poster else potong(im, saiz, 0.40)
            out.save(os.path.join(hero_dir, '%s-%s.webp' % (nama, akhiran)), 'WEBP', quality=82, method=6)
        slaid_berita.append({'jenis': 'berita',
                             'besar': 'assets/hero/%s-besar.webp' % nama,
                             'telefon': 'assets/hero/%s-telefon.webp' % nama,
                             'alt': b.get('gambar_alt') or b.get('tajuk'),
                             'tajuk': b['tajuk'],
                             'kicker': b.get('kategori') or 'Berita',
                             'pautan': '/berita/%s/' % b['slug']})
        print('berita %-40s %s' % (b['slug'][:40], 'poster' if poster else 'crop'))

    # Berselang-seli gambar/berita; lebihan diletak di hujung.
    susunan, gi, bi = [], 0, 0
    while gi < len(slaid_gambar) or bi < len(slaid_berita):
        if gi < len(slaid_gambar):
            susunan.append(slaid_gambar[gi]); gi += 1
        if bi < len(slaid_berita):
            susunan.append(slaid_berita[bi]); bi += 1

    data = {
        'cara_edit': ('Dijana oleh alat/bina_hero.py — jangan edit dengan tangan. Gambar prosedur '
                      'dalam GAMBAR; semua berita dalam data/berita.json masuk roulette automatik.'),
        'selang_saat': SELANG,
        'slaid': susunan,
    }
    with open(os.path.join(AKAR, 'data', 'hero.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('hero.json: %d slaid (%d gambar, %d berita)' %
          (len(susunan), len(slaid_gambar), len(slaid_berita)))


if __name__ == '__main__':
    main()
