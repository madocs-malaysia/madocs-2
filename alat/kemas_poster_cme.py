#!/usr/bin/env python3
"""Kemas kini poster CME Presiden (24 Nov 2026): poster baharu menyatakan 1 mata CPD.

Tindakan:
  1. Tukar imej berita/poster kepada poster baharu (WebP 1400 px).
  2. Jana semula PDF poster (A4) untuk Pusat Sumber.
  3. Kemas kini teks berita: mata CPD, gelaran penceramah.
"""
import json
from pathlib import Path

from PIL import Image

SUMBER = Path('/home/ubuntu/.hermes/profiles/madocs/cache/documents/native-inputs/2ce78b0836565ac218c81f27888c3875747d286b246f33bc5cc8058984816a89/img_70be97221524.jpg')
AKAR = Path('/home/ubuntu/madocs-site')
IMEJ = AKAR / 'assets' / 'berita-2026-11-24-cme-tissue-adhesive.webp'
PDF = AKAR / 'assets' / 'dokumen' / 'poster-cme-tissue-adhesive.pdf'

LAMA_CPD = ('Permohonan mata CPD PERDIM sedang diproses. Bilangan mata CPD akan dimaklumkan '
            'di halaman ini sebaik ia disahkan. Penyertaan akan direkodkan oleh penganjur bersama.')
BARU_CPD = ('Sesi ini menyediakan 1 mata CPD. Penyertaan akan direkodkan oleh penganjur bersama '
            'PERDIM dan MADOCS.')

LAMA_PENCERAMAH = ('Presiden MADOCS, Dr Abdol Rashid bin Masrom, dijemput menyampaikan ceramah CME '
                   'bertajuk "Beyond the Conventional Clamp, The Role of Tissue Adhesives in '
                   'Pediatric Circumcision".')
BARU_PENCERAMAH = ('Presiden MADOCS, Dr Abdol Rashid bin Masrom, dijemput menyampaikan ceramah CME '
                   'bertajuk "Beyond the Conventional Clamp, The Role of Tissue Adhesives in '
                   'Pediatric Circumcision". Beliau juga Pengerusi Rangkaian Klinik Sejahtera.')


def imej_dan_pdf():
    im = Image.open(SUMBER).convert('RGB')
    if im.width > 1400:
        im = im.resize((1400, round(im.height * 1400 / im.width)), Image.LANCZOS)
    im.save(IMEJ, format='WEBP', quality=88, method=6)
    print('imej:', im.size, IMEJ.stat().st_size, 'bait')

    # PDF A4 potret, gambar diletak pada seluruh halaman dengan nisbah dikekalkan
    a4 = (1240, 1754)  # 150 dpi
    halaman = Image.new('RGB', a4, 'white')
    nisbah = min(a4[0] / im.width, a4[1] / im.height)
    saiz = (round(im.width * nisbah), round(im.height * nisbah))
    kecil = im.resize(saiz, Image.LANCZOS)
    halaman.paste(kecil, ((a4[0] - saiz[0]) // 2, (a4[1] - saiz[1]) // 2))
    halaman.save(PDF, 'PDF', resolution=150.0)
    print('PDF:', PDF.stat().st_size, 'bait')


def teks():
    p = AKAR / 'data' / 'berita.json'
    d = json.loads(p.read_text(encoding='utf-8'))
    bil = 0
    for b in d['berita']:
        if b['slug'] != '2026-11-24-cme-tissue-adhesive':
            continue
        b['kandungan'] = [
            BARU_PENCERAMAH if par == LAMA_PENCERAMAH else (BARU_CPD if par == LAMA_CPD else par)
            for par in b['kandungan']
        ]
        bil += 1
        # simpan teks baharu untuk terjemahan
        globals()['_pasangan'] = [(LAMA_PENCERAMAH, BARU_PENCERAMAH), (LAMA_CPD, BARU_CPD)]
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('berita dikemas:', bil)


def terjemahan():
    p = AKAR / 'data' / 'terjemahan.json'
    kamus = json.loads(p.read_text(encoding='utf-8'))
    # buang terjemahan ayat lama, tambah yang baharu
    kamus.pop(LAMA_CPD, None)
    kamus.pop(LAMA_PENCERAMAH, None)
    kamus[BARU_CPD] = ('This session provides 1 CPD point. Attendance will be recorded jointly by '
                       'PERDIM and MADOCS.')
    kamus[BARU_PENCERAMAH] = ('The President of MADOCS, Dr Abdol Rashid bin Masrom, has been invited to '
                              'deliver the CME lecture titled "Beyond the Conventional Clamp, The Role '
                              'of Tissue Adhesives in Pediatric Circumcision". He is also Chairman of '
                              'Rangkaian Klinik Sejahtera.')
    p.write_text(json.dumps(kamus, ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    print('terjemahan dikemas kini')


if __name__ == '__main__':
    imej_dan_pdf()
    teks()
    terjemahan()
