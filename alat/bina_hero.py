#!/usr/bin/env python3
"""Hasilkan slaid hero (roulette) daripada gambar galeri DAN semua berita.

Keluaran:
  assets/hero/<nama>-besar.webp    (1400x1015)
  assets/hero/<nama>-telefon.webp  (720x480)
  data/hero.json                   (gambar prosedur + SEMUA berita, berselang-seli)

Semua berita dalam data/berita.json masuk roulette secara automatik — jangan edit
hero.json dengan tangan.
"""
import json
import os
from PIL import Image, ImageDraw, ImageFilter

AKAR = '/home/ubuntu/madocs-site'
BESAR = (1400, 1015)
TELEFON = (720, 480)
SELANG = 6

# Gambar prosedur/klinikal (bukan berita). Fokus menegak 0=puncak 1=dasar.
GAMBAR = [
    ('assets/galeri/pelancaran-2026/06.webp', 'garis-panduan', 0.42,
     'Stand pelancaran Buku Garis Panduan Berkhatan (Lelaki) 2026 di majlis pelancaran rasmi Kementerian Kesihatan Malaysia'),
    ('assets/berita-agm-2026-kumpulan.webp', 'ahli-agm', 0.45,
     'Ahli dan Ahli Jawatankuasa MADOCS bergambar bersama sepanduk MALAYSIAN DOCTORS OF CIRCUMCISION SOCIETY pada Mesyuarat Agung Tahunan Ke-4, 2026'),
    ('assets/galeri/batu-pahat-2025/01.webp', 'peserta-kursus', 0.38,
     'Peserta dan fasilitator kursus Privileging Course for Circumcision (Dorsal Slit) Part 2 bergambar bersama sepanduk kursus di The Katerina Hotel, Batu Pahat'),
    ('assets/galeri/batu-pahat-2025/16.webp', 'dewan-peserta', 0.45,
     'Dewan kursus PCC2-1 dan CCC7 di The Katerina Hotel, Batu Pahat penuh dengan peserta, dengan sepanduk kursus dan sepanduk MADOCS di pentas'),
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
POSTER = {'2026-11-24-cme-tissue-adhesive', '2026-10-27-promosi-keahlian-seumur-hidup-2026',
          '2026-11-13-ccc9-pendaftaran-dibuka'}

# Berita yang imej hero-nya direka penuh oleh alat lain (jangan jana semula di sini).
SIAP_BERITA = {'2026-11-13-ccc9-pendaftaran-dibuka'}

# Berita yang kad teksnya tidak dipaparkan: reka bentuk hero sudah mengandungi tajuk + CTA.
TANPA_KAD = {'2026-11-13-ccc9-pendaftaran-dibuka'}

# Slaid berita yang dipin di hadapan roulette (promosi aktif).
PIN = ('2026-11-13-ccc9-pendaftaran-dibuka',)

# Gambar berkumpulan: jangan potong sesiapa. Paparkan penuh di atas latar kabur.
PENUH = {'ahli-agm', 'peserta-kursus', 'garis-panduan'}

# Kad ucapan Deepavali bukan gambar — ia direka penuh pada dua nisbah hero oleh
# alat/bina_kad_deepavali.py. Jangan jana semula daripada gambar sumber (poster
# menegak yang ditampal atas latar kabur nampak kecil + terpotong pada telefon).
SIAP = {'ucapan-deepavali'}


def slaid_penuh(im, saiz):
    """Muatkan SELURUH gambar (contain) di atas latar kabur daripada gambar yang sama.

    Digunakan untuk gambar berkumpulan supaya tiada wajah terpotong di tepi.
    """
    lw, lh = saiz
    latar = potong(im, saiz, 0.45).filter(ImageFilter.GaussianBlur(42))
    latar = Image.blend(latar, Image.new('RGB', saiz, '#1e0206'), 0.62)

    skala = min(lw / im.width, lh / im.height)
    lebar, tinggi = int(im.width * skala), int(im.height * skala)
    depan = im.resize((lebar, tinggi), Image.LANCZOS)
    x, y = (lw - lebar) // 2, (lh - tinggi) // 2
    latar.paste(depan, (x, y))
    return latar


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

    # Telefon: kad teks berita berada di bawah (top ~328px), jadi poster mesti
    # kekal di bahagian atas dan lebih kecil supaya tidak tertutup.
    if saiz == TELEFON:
        tinggi = int(lh * 0.60)
        lebar = int(im.width * tinggi / im.height)
        poster = im.resize((lebar, tinggi), Image.LANCZOS)
        x = (lw - lebar) // 2
        y = int(lh * 0.02)
    else:
        tinggi = int(lh * 0.70)
        lebar = int(im.width * tinggi / im.height)
        poster = im.resize((lebar, tinggi), Image.LANCZOS)
        # Tengah imej: CSS hero memotong tepi kiri/kanan (object-fit:cover).
        x = (lw - lebar) // 2
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
        if nama not in SIAP:
            im = Image.open(laluan).convert('RGB')
            for saiz, akhiran in ((TELEFON, 'telefon'), (BESAR, 'besar')):
                out = slaid_penuh(im, saiz) if nama in PENUH else potong(im, saiz, fokus)
                out.save(os.path.join(hero_dir, '%s-%s.webp' % (nama, akhiran)), 'WEBP', quality=82, method=6)
        slaid_gambar.append({'jenis': 'imej',
                             'besar': 'assets/hero/%s-besar.webp' % nama,
                             'telefon': 'assets/hero/%s-telefon.webp' % nama,
                             'alt': alt})
        print('imej   %-14s %s' % (nama, 'kekal (direka penuh)' if nama in SIAP else 'siap'))

    slaid_berita = []
    berita = json.load(open(os.path.join(AKAR, 'data', 'berita.json'), encoding='utf-8'))['berita']
    for b in berita:
        g = b.get('gambar')
        if not g or not os.path.exists(os.path.join(AKAR, g)):
            print('berita tanpa gambar dilangkau:', b['slug'])
            continue
        nama = 'berita-' + b['slug']
        poster = b['slug'] in POSTER
        if b['slug'] in SIAP_BERITA:
            print('berita %-40s kad direka penuh (kekal)' % b['slug'][:40])
        else:
            im = Image.open(os.path.join(AKAR, g)).convert('RGB')
            for saiz, akhiran in ((TELEFON, 'telefon'), (BESAR, 'besar')):
                out = slaid_poster(im, saiz) if poster else potong(im, saiz, 0.40)
                out.save(os.path.join(hero_dir, '%s-%s.webp' % (nama, akhiran)), 'WEBP', quality=82, method=6)
        if b['slug'] in TANPA_KAD:
            slaid_berita.append({'jenis': 'imej', 'slug': b['slug'],
                                 'besar': 'assets/hero/%s-besar.webp' % nama,
                                 'telefon': 'assets/hero/%s-telefon.webp' % nama,
                                 'alt': b.get('gambar_alt') or b['tajuk']})
            print('berita %-40s imej tanpa kad' % b['slug'][:40])
            continue
        slaid_berita.append({'jenis': 'berita', 'slug': b['slug'],
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

    # Slaid yang dipin naik ke hadapan supaya promosi aktif jadi slaid pertama.
    hadapan = [s for s in susunan if s.get('slug') in PIN]
    susunan = hadapan + [s for s in susunan if s not in hadapan]

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
