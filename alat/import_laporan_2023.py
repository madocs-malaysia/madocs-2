#!/usr/bin/env python3
"""Import Laporan Aktiviti MADOCS 2023 (PDF) → data aktiviti + album galeri.

Sumber: Laporan Aktiviti MADOCS Tahun 2023 (32 halaman, 62 imej).
Prinsip:
  - Hanya gambar program/upacara yang selamat diterbitkan. Gambar pesakit, prosedur di atas
    meja dan kanak-kanak dikenal pasti TIDAK diambil.
  - Teks ringkas ditulis semula dalam Bahasa Melayu, bukan salinan terus.
"""
import json
import shutil
from pathlib import Path

from PIL import Image

SUMBER = Path('/home/ubuntu/.hermes/profiles/madocs/cache/scratch/laporan2023')
AKAR = Path('/home/ubuntu/madocs-site')
TUJUAN = AKAR / 'assets' / 'galeri' / 'program-2023'
TUJUAN.mkdir(parents=True, exist_ok=True)

# (fail sumber, nama baharu, alt, acara)
PILIHAN = [
    ('hlm14-imej1.png', 'ccc1-01.webp', 'Penceramah menyampaikan kuliah semasa Comprehensive Circumcision Course 1', 'ccc1'),
    ('hlm14-imej2.png', 'ccc1-02.webp', 'Penceramah di pentas CCC 1 dengan latar sepanduk MADOCS dan PERDIM', 'ccc1'),
    ('hlm14-imej3.png', 'ccc1-03.webp', 'Peserta kursus mengikuti sesi kuliah CCC 1', 'ccc1'),
    ('hlm15-imej1.png', 'ccc1-04.webp', 'Pembentangan slaid semasa sesi kuliah CCC 1', 'ccc1'),
    ('hlm15-imej3.png', 'ccc1-05.webp', 'Penyampaian cek tajaan kepada penganjur semasa CCC 1', 'ccc1'),
    ('hlm16-imej2.png', 'ccc1-06.webp', 'Meja pendaftaran peserta di kaunter program CCC 1', 'ccc1'),
    ('hlm15-imej4.png', 'ccc1-07.webp', 'Peserta memenuhi ruang pameran semasa program CCC 1', 'ccc1'),
    ('hlm19-imej1.png', 'micc-01.webp', 'Booth pameran semasa Malaysian International Circumcision Conference 2023', 'micc'),
    ('hlm19-imej2.png', 'micc-02.webp', 'Dua peserta berbincang di ruang pameran MICC 2023', 'micc'),
    ('hlm20-imej1.png', 'micc-04.webp', 'Wakil MADOCS menyampaikan ceramah semasa MICC 2023', 'micc'),
    ('hlm20-imej2.png', 'micc-05.webp', 'Gambar berkumpulan peserta MICC 2023 di The Everly Hotel Putrajaya', 'micc'),
    ('hlm21-imej2.png', 'agm1-01.webp', 'Ahli mesyuarat di Mesyuarat Agung Tahunan Pertama MADOCS', 'agm1'),
    ('hlm22-imej1.png', 'agm1-02.webp', 'Perbincangan di meja mesyuarat semasa AGM pertama MADOCS', 'agm1'),
    ('hlm22-imej2.png', 'agm1-03.webp', 'Ahli jawatankuasa dalam sesi mesyuarat AGM pertama', 'agm1'),
    ('hlm22-imej3.png', 'agm1-04.webp', 'Gambar berkumpulan ahli selepas Mesyuarat Agung Tahunan Pertama', 'agm1'),
    ('hlm23-imej2.png', 'agm1-05.webp', 'Penyampaian cenderamata sempena mesyuarat agung MADOCS', 'agm1'),
    ('hlm25-imej2.png', 'ccc2-01.webp', 'Peserta kursus memenuhi dewan semasa Comprehensive Circumcision Course 2', 'ccc2'),
    ('hlm26-imej1.png', 'ccc2-02.webp', 'Peserta mengikuti kuliah CCC 2 dengan tekun', 'ccc2'),
    ('hlm26-imej2.png', 'ccc2-03.webp', 'Penceramah menyampaikan kuliah di CCC 2', 'ccc2'),
    ('hlm26-imej3.png', 'ccc2-04.webp', 'Wakil MADOCS berucap di hadapan peserta CCC 2', 'ccc2'),
    ('hlm27-imej1.png', 'ccc2-05.webp', 'Penyampaian plak penghargaan semasa CCC 2', 'ccc2'),
    ('hlm29-imej1.png', 'perak-01.webp', 'Bangunan Hotel Taiping Perdana, lokasi Perak Circumcision Update 2023', 'perak'),
    ('hlm17-imej2.png', 'umum-01.webp', 'Ahli jawatankuasa MADOCS dalam perbincangan meja bulat', 'umum'),
    ('hlm05-imej1.png', 'umum-02.webp', 'Presiden MADOCS berjabat tangan dengan wakil rakan NGO', 'umum'),
    ('hlm06-imej1.png', 'umum-03.webp', 'Gambar berkumpulan ahli MADOCS pada program 2023', 'umum'),
    ('hlm18-imej3.png', 'umum-04.webp', 'Ahli dan peserta berbual semasa jamuan program MADOCS 2023', 'umum'),
    ('hlm28-imej3.png', 'umum-05.webp', 'Penyediaan sijil keahlian MADOCS', 'umum'),
]

AKTIVITI = [
    {
        'slug': '2023-02-18-ccc1',
        'kategori': 'CCC',
        'tajuk': 'Comprehensive Circumcision Course 1 (CCC 1)',
        'tarikh': '2023-02-18',
        'tempat': '',
        'gambar': 'assets/galeri/program-2023/ccc1-02.webp',
        'gambar_alt': 'Penceramah di pentas CCC 1 dengan latar sepanduk MADOCS dan PERDIM',
        'ringkas': ('Kursus komprehensif pertama MADOCS, menampilkan empat kaedah berkhatan dengan '
                    '5 penceramah dan 12 jurulatih amali. Seramai 59 peserta mengikuti kursus dan '
                    '93 pesakit daripada golongan asnaf, fakir dan B40 menerima manfaat melalui '
                    'program CSR tajaan PPZ Wilayah Persekutuan.'),
        'laporan': [
            'Empat kaedah berkhatan diperkenalkan dalam kursus ini, dengan gabungan sesi kuliah dan latihan amali yang dikendalikan 12 jurulatih.',
            'Program CSR bersama PPZ Wilayah Persekutuan membolehkan 93 pesakit daripada golongan asnaf, fakir dan B40 menerima rawatan berkhatan tanpa bayaran.',
        ],
    },
    {
        'slug': '2023-02-26-micc-putrajaya',
        'kategori': 'Persidangan',
        'tajuk': 'Malaysian International Circumcision Conference 2023',
        'tarikh': '2023-02-26',
        'tempat': 'The Everly Hotel, Putrajaya',
        'gambar': 'assets/galeri/program-2023/micc-05.webp',
        'gambar_alt': 'Gambar berkumpulan peserta MICC 2023 di The Everly Hotel Putrajaya',
        'ringkas': ('MADOCS menyertai Malaysian International Circumcision Conference 2023 di '
                    'Putrajaya. Presiden menyampaikan ceramah bertajuk "Roles of MADOCS in Malaysia" '
                    'dan MADOCS turut mengadakan sesi bersama media.'),
        'laporan': [
            'Ceramah "Roles of MADOCS in Malaysia" memperkenalkan peranan pertubuhan kepada peserta antarabangsa dan pengamal tempatan.',
            'Kehadiran MADOCS dalam persidangan ini membuka ruang perbincangan dengan rakan NGO dan pihak berkepentingan industri berkhatan.',
        ],
    },
    {
        'slug': '2023-03-31-agm-pertama',
        'kategori': 'AGM',
        'tajuk': 'Mesyuarat Agung Tahunan Pertama MADOCS',
        'tarikh': '2023-03-31',
        'tempat': 'Hotel Tamu, Kampung Baru, Kuala Lumpur',
        'gambar': 'assets/galeri/program-2023/agm1-04.webp',
        'gambar_alt': 'Gambar berkumpulan ahli selepas Mesyuarat Agung Tahunan Pertama MADOCS',
        'ringkas': ('Mesyuarat Agung Tahunan pertama diadakan di Hotel Tamu, Kampung Baru. Dalam '
                    'mesyuarat ini, keahlian kumpulan pertama seramai 85 ahli diluluskan, menandakan '
                    'bermulanya keanggotaan rasmi pertubuhan.'),
        'laporan': [
            'Seramai 85 ahli kumpulan pertama diluluskan keahliannya dalam mesyuarat ini.',
            'Mesyuarat turut membincangkan hala tuju program latihan dan penyeragaman caj berkhatan.',
        ],
    },
    {
        'slug': '2023-08-27-ccc2',
        'kategori': 'CCC',
        'tajuk': 'Comprehensive Circumcision Course 2 (CCC 2)',
        'tarikh': '2023-08-27',
        'tempat': '',
        'gambar': 'assets/galeri/program-2023/ccc2-03.webp',
        'gambar_alt': 'Penceramah menyampaikan kuliah di CCC 2',
        'ringkas': ('Kursus komprehensif kedua menampilkan lima kaedah berkhatan, 6 penceramah dan '
                    '12 jurulatih amali. Seramai 57 peserta menyertai kursus dan 76 pesakit menerima '
                    'rawatan melalui program CSR tajaan PPZ Wilayah Persekutuan.'),
        'laporan': [
            'Sebelas ahli baharu turut diluluskan keahliannya pada tarikh yang sama.',
            'Sambutan peserta dan pesakit melebihi jangkaan, menyamai pencapaian kursus pertama.',
        ],
    },
    {
        'slug': '2023-09-17-perak-circumcision-update',
        'kategori': 'Ceramah',
        'tajuk': 'Perak Circumcision Update 2023',
        'tarikh': '2023-09-17',
        'tempat': 'Hotel Taiping Perdana, Perak',
        'gambar': 'assets/galeri/program-2023/perak-01.webp',
        'gambar_alt': 'Bangunan Hotel Taiping Perdana, lokasi Perak Circumcision Update 2023',
        'ringkas': ('Presiden MADOCS dijemput menyampaikan ceramah "Introduction to MADOCS" di '
                    'Perak Circumcision Update 2023, menjadikan pertubuhan ini dikenali di peringkat '
                    'negeri.'),
        'laporan': [
            'Ceramah memperkenalkan peranan, program latihan dan pendekatan keselamatan berkhatan yang dibawa MADOCS.',
        ],
    },
    {
        'slug': '2023-11-01-garis-panduan-khatan-kkm',
        'kategori': 'Dasar',
        'tajuk': 'Mesyuarat Semakan Garis Panduan Khatan KKM',
        'tarikh': '2023-11-01',
        'tempat': 'E1, Kementerian Kesihatan Malaysia, Putrajaya',
        'gambar': '',
        'gambar_alt': '',
        'ringkas': ('MADOCS mewakili sektor swasta dalam mesyuarat semakan Garis Panduan Khatan '
                    'Kementerian Kesihatan Malaysia. Mesyuarat bersetuju menubuhkan Jawatankuasa '
                    'Khatan Kebangsaan dan MADOCS diberi dua kerusi wakil.'),
        'laporan': [
            'Mesyuarat dihadiri Bahagian Amalan Perubatan, Bahagian Perkembangan Kesihatan Awam, Bahagian Pembangunan Kesihatan Keluarga, pakar bedah KKM serta wakil NGO perubatan.',
            'Jawatankuasa Khatan Kebangsaan ditubuhkan untuk merangka garis panduan berkhatan, termasuk teknik dorsal slit, khatan di premis KKM dan swasta, khatan beramai-ramai, aspek medico-legal dan mekanisme rujukan komplikasi.',
            'Sektor swasta diwakili MADOCS (2 wakil), PERDIM, MMA dan APHM (seorang wakil setiap satu).',
        ],
    },
    {
        'slug': '2023-12-31-mesyuarat-ajk-2023',
        'kategori': 'Mesyuarat',
        'tajuk': 'Mesyuarat Ahli Jawatankuasa MADOCS Sesi 2023',
        'tarikh': '2023-07-02',
        'tempat': 'Hotel Maluri Cheras, Hotel Tamu Kampung Baru dan Yahala Restaurant, Kuala Lumpur',
        'gambar': 'assets/galeri/program-2023/umum-01.webp',
        'gambar_alt': 'Ahli jawatankuasa MADOCS dalam perbincangan meja bulat',
        'ringkas': ('Sepanjang tahun pertama, tiga mesyuarat ahli jawatankuasa direkodkan iaitu pada '
                    '18 Februari di Hotel Maluri Cheras, 31 Mac di Hotel Tamu Kampung Baru dan '
                    '2 Julai di Yahala Restaurant, Kuala Lumpur. Urusan harian pula dibuat melalui '
                    'kumpulan WhatsApp jawatankuasa.'),
        'laporan': [
            'Mesyuarat dijalankan secara fizikal dengan pilihan hadir dalam talian bagi ahli yang berada jauh.',
            'Keputusan harian dibincangkan dalam kumpulan WhatsApp jawatankuasa dan direkodkan secara rasmi dalam mesyuarat.',
        ],
    },
]


def tukar_imej():
    dibuat = 0
    for sumber, nama, _alt, _acara in PILIHAN:
        asal = SUMBER / sumber
        if not asal.exists():
            print('tiada:', sumber)
            continue
        with Image.open(asal) as im:
            im = im.convert('RGB')
            if im.width > 1400:
                tinggi = round(im.height * 1400 / im.width)
                im = im.resize((1400, tinggi), Image.LANCZOS)
            im.save(TUJUAN / nama, format='WEBP', quality=82, method=6)
        dibuat += 1
    print('imej ditukar:', dibuat)


def tulis_galeri():
    p = AKAR / 'data' / 'galeri.json'
    d = json.loads(p.read_text(encoding='utf-8'))
    d['album'] = [a for a in d['album'] if a['slug'] != 'program-2023']
    gambar = [{'src': 'assets/galeri/program-2023/%s' % nama, 'alt': alt}
              for _s, nama, alt, _a in PILIHAN if (TUJUAN / nama).exists()]
    d['album'].append({
        'slug': 'program-2023',
        'tajuk': 'Program MADOCS 2023',
        'tarikh': '2023-12-31',
        'kategori': 'Program',
        'ringkas': ('Album tahun pertama MADOCS: kursus komprehensif berkhatan, persidangan '
                    'antarabangsa, mesyuarat agung pertama dan program bersama Kementerian Kesihatan. '
                    'Gambar pesakit dan prosedur tidak diterbitkan.'),
        'gambar': gambar,
    })
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('album program-2023:', len(gambar), 'gambar')


def tulis_aktiviti():
    p = AKAR / 'data' / 'aktiviti.json'
    d = json.loads(p.read_text(encoding='utf-8'))
    slug_lama = {a['slug'] for a in d['aktiviti']}
    for a in AKTIVITI:
        item = dic = dict(a)
        if dic['slug'] in slug_lama:
            d['aktiviti'] = [dic if x['slug'] == dic['slug'] else x for x in d['aktiviti']]
        else:
            d['aktiviti'].append(dic)
    d['aktiviti'].sort(key=lambda x: x['tarikh'])
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('aktiviti 2023 ditambah:', len(AKTIVITI), '| jumlah keseluruhan:', len(d['aktiviti']))


if __name__ == '__main__':
    tukar_imej()
    tulis_galeri()
    tulis_aktiviti()
