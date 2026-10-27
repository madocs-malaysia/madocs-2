#!/usr/bin/env python3
"""Import Laporan Aktiviti MADOCS 2024 (DOCX) → entri aktiviti + album galeri + terjemahan.

Sumber: Laporan Aktiviti MADOCS Tahun 2024 (67 imej dalam fail).
Prinsip sama seperti 2023: gambar pesakit/prosedur, sijil, logo dan tangkapan dokumen
tidak diterbitkan.
"""
import json
from pathlib import Path

from PIL import Image

SUMBER = Path('/home/ubuntu/.hermes/profiles/madocs/cache/scratch/laporan2024')
AKAR = Path('/home/ubuntu/madocs-site')
TUJUAN = AKAR / 'assets' / 'galeri' / 'program-2024'
TUJUAN.mkdir(parents=True, exist_ok=True)

# (imej sumber, nama baharu, alt BM, alt EN)
PILIHAN = [
    ('image2.jpeg', '2024-01.webp', 'Penyampaian cenderamata semasa program MADOCS 2024', 'Presentation of a memento at a MADOCS 2024 programme'),
    ('image5.jpeg', '2024-02.webp', 'Penyampaian cek sumbangan pada program bersama rakan kerjasama', 'Cheque presentation at a programme with partner organisations'),
    ('image3.jpeg', '2024-03.webp', 'Peserta program komuniti MADOCS berkumpul di lokasi program', 'Participants of a MADOCS community programme gathering at the venue'),
    ('image8.jpeg', '2024-04.webp', 'Ahli MADOCS bergambar bersama peserta program luar', 'MADOCS members with participants of an outdoor programme'),
    ('image9.jpeg', '2024-05.webp', 'Pasukan MADOCS di ruang pameran program', 'The MADOCS team at a programme exhibition area'),
    ('image10.jpeg', '2024-06.webp', 'Peserta berkunjung ke booth MADOCS semasa program', 'Participants visiting the MADOCS booth during a programme'),
    ('image16.jpeg', '2024-07.webp', 'Mesyuarat semakan garis panduan berkhatan bersama wakil Kementerian Kesihatan', 'Circumcision guidelines review meeting with Ministry of Health representatives'),
    ('image17.jpeg', '2024-08.webp', 'Perbincangan meja bulat semasa mesyuarat garis panduan', 'Round-table discussion at a guidelines meeting'),
    ('image18.jpeg', '2024-09.webp', 'Ahli mesyuarat meneliti dokumen semakan garis panduan', 'Meeting members reviewing guideline documents'),
    ('image21.jpeg', '2024-10.webp', 'Wakil MADOCS dalam perbincangan mesyuarat peringkat kementerian', 'MADOCS representative in a ministry-level meeting discussion'),
    ('image24.jpeg', '2024-11.webp', 'Dewan kursus MADOCS dipenuhi peserta', 'MADOCS course hall filled with participants'),
    ('image27.jpeg', '2024-12.webp', 'Gambar berkumpulan peserta program MADOCS 2024', 'Group photograph of MADOCS 2024 programme participants'),
    ('image28.jpeg', '2024-13.webp', 'Sesi kuliah dalam kursus berkhatan MADOCS', 'Lecture session at a MADOCS circumcision course'),
    ('image29.jpeg', '2024-14.webp', 'Tiga wakil MADOCS di hadapan latar program', 'Three MADOCS representatives in front of a programme backdrop'),
    ('image30.jpeg', '2024-15.webp', 'Pembentangan slaid semasa sesi mesyuarat', 'Slide presentation during a meeting session'),
    ('image34.jpeg', '2024-16.webp', 'Ahli jawatankuasa dalam mesyuarat perancangan program', 'Committee members at a programme planning meeting'),
    ('image37.jpeg', '2024-17.webp', 'Mesyuarat Technical Working Group berkaitan panduan berkhatan', 'Technical Working Group meeting on circumcision guidelines'),
    ('image38.jpeg', '2024-18.webp', 'Peserta mesyuarat kementerian mendengar pembentangan', 'Ministry meeting participants listening to a presentation'),
    ('image42.jpeg', '2024-19.webp', 'Jurulatih berkhatan dalam sesi latihan amali', 'Circumcision trainers during a hands-on training session'),
    ('image44.jpeg', '2024-20.webp', 'Dewan besar semasa program latihan MADOCS', 'The main hall during a MADOCS training programme'),
    ('image50.jpeg', '2024-21.webp', 'Ceramah khatan di hadapan sepanduk program jelajah khatan', 'Circumcision talk in front of a circumcision outreach programme banner'),
    ('image51.jpeg', '2024-22.webp', 'Peserta program jelajah khatan bergambar bersama', 'Participants of a circumcision outreach programme in a group photograph'),
    ('image57.jpeg', '2024-23.webp', 'Slaid kursus Privileging for Circumcision (Dorsal Slit) 23 Oktober 2024', 'Slide for the Privileging Course for Circumcision (Dorsal Slit), 23 October 2024'),
    ('image60.jpeg', '2024-24.webp', 'Gambar berkumpulan peserta National Circumcision Symposium 2024', 'Group photograph of National Circumcision Symposium 2024 participants'),
    ('image62.jpeg', '2024-25.webp', 'Penceramah menyampaikan ucapan di National Circumcision Symposium 2024', 'Speaker addressing the National Circumcision Symposium 2024'),
    ('image64.jpeg', '2024-26.webp', 'Peserta melawat pameran semasa simposium', 'Participants visiting the exhibition during the symposium'),
    ('image65.jpeg', '2024-27.webp', 'Peserta simposium berkumpul di dewan utama', 'Symposium participants gathered in the main hall'),
    ('image31.jpeg', '2024-28.webp', 'Poster Mesyuarat Agung Tahunan ke-2 MADOCS 2024', 'Poster for the MADOCS 2nd Annual General Meeting 2024'),
]

AKTIVITI = [
    {
        'slug': '2024-01-30-garis-panduan-khatan-kkm-2024',
        'kategori': 'Dasar',
        'tajuk': 'Siri Mesyuarat Garis Panduan Khatan Kebangsaan 2024',
        'tarikh': '2024-01-30',
        'tempat': 'Cyberjaya, Port Dickson, Genting Highlands dan Putrajaya',
        'gambar': 'assets/galeri/program-2024/2024-07.webp',
        'gambar_alt': 'Mesyuarat semakan garis panduan berkhatan bersama wakil Kementerian Kesihatan',
        'ringkas': ('MADOCS menyertai siri mesyuarat semakan Garis Panduan Berkhatan Kementerian Kesihatan '
                    'Malaysia sepanjang 2024, termasuk mesyuarat Bil. 1/2024 di Cyberjaya, Bil. 2/2024 di '
                    'Port Dickson dan Bil. 3/2024 di Genting Highlands. Technical Working Group turut '
                    'bersidang bagi menyiapkan draf akhir garis panduan kebangsaan.'),
        'ringkas_en': ('MADOCS took part in the 2024 series reviewing the Ministry of Health Circumcision '
                       'Guidelines, including meetings 1/2024 in Cyberjaya, 2/2024 in Port Dickson and '
                       '3/2024 in Genting Highlands. The Technical Working Group also met to complete the '
                       'final draft of the national guidelines.'),
        'laporan': [
            ('Mesyuarat membincangkan semakan dokumen garis panduan khatan KKM untuk tujuan privileging khatan.',
             'The meetings reviewed the ministry guideline documents for circumcision privileging.'),
            ('Mesyuarat Technical Working Group diadakan pada 14 Jun, 19 Julai, 27-28 Ogos dan 4-6 September 2024 bagi semakan akhir garis panduan serta perancangan Kursus Privileging dan simposium kebangsaan.',
             'Technical Working Group meetings were held on 14 June, 19 July, 27-28 August and 4-6 September 2024 for the final review and to plan the Privileging Course and national symposium.'),
            ('Pada 3 Oktober 2024, MADOCS turut serta dalam mesyuarat modul khatan dalam aplikasi MySejahtera di E1 KKM Putrajaya, membincangkan penggunaan aplikasi untuk data dan rekod khatan serta komplikasi.',
             'On 3 October 2024, MADOCS joined the circumcision module meeting for the MySejahtera application at E1, Ministry of Health Putrajaya, discussing use of the app for circumcision and complication records.'),
        ],
    },
    {
        'slug': '2024-02-24-ccc3-pulau-pinang',
        'kategori': 'CCC',
        'tajuk': 'Comprehensive Circumcision Course 3 (CCC 3)',
        'tarikh': '2024-02-24',
        'tempat': 'Bayview Hotel dan H-Medical Centre, Pulau Pinang',
        'gambar': 'assets/galeri/program-2024/2024-11.webp',
        'gambar_alt': 'Dewan kursus MADOCS dipenuhi peserta',
        'ringkas': ('Kursus komprehensif ketiga diadakan di Pulau Pinang dengan latihan teori dan amali '
                    'berkhatan, melibatkan peserta doktor dari seluruh negara.'),
        'ringkas_en': ('The third comprehensive course was held in Penang with theory and hands-on '
                       'circumcision training for doctors from across the country.'),
        'laporan': [
            ('Kursus dijalankan selama dua hari di Bayview Hotel untuk sesi teori dan H-Medical Centre untuk latihan amali.',
             'The course ran over two days: theory at Bayview Hotel and hands-on training at H-Medical Centre.'),
        ],
    },
    {
        'slug': '2024-05-06-ttt-hrdc-sunway',
        'kategori': 'Latihan',
        'tajuk': 'Program Train The Trainer HRDC, Sunway Nexus',
        'tarikh': '2024-05-06',
        'tempat': 'Sunway Nexus, Kota Damansara, Selangor',
        'gambar': 'assets/galeri/program-2024/2024-19.webp',
        'gambar_alt': 'Jurulatih berkhatan dalam sesi latihan amali',
        'ringkas': ('Dua siri Program Train The Trainer di bawah HRDC di Sunway Nexus, Kota Damansara, '
                    'dikendalikan oleh barisan penceramah MADOCS bagi melahirkan jurulatih khatan bertauliah.'),
        'ringkas_en': ('Two series of the HRDC Train The Trainer programme at Sunway Nexus, Kota Damansara, '
                       'delivered by MADOCS lecturers to produce certified circumcision trainers.'),
        'laporan': [
            ('Siri pertama berlangsung 6-10 Mei 2024 dan siri kedua 5-9 Ogos 2024, dengan penyertaan beberapa ahli jawatankuasa sebagai penceramah.',
             'The first series ran 6-10 May 2024 and the second 5-9 August 2024, with several committee members as lecturers.'),
        ],
    },
    {
        'slug': '2024-05-18-agm-ke-2',
        'kategori': 'AGM',
        'tajuk': 'Mesyuarat Agung Tahunan ke-2 dan Persidangan Antarabangsa',
        'tarikh': '2024-05-18',
        'tempat': 'Hotel Maluri, Taman Maluri, Kuala Lumpur',
        'gambar': 'assets/galeri/program-2024/2024-28.webp',
        'gambar_alt': 'Poster Mesyuarat Agung Tahunan ke-2 MADOCS 2024',
        'ringkas': ('Mesyuarat Agung Tahunan kedua diadakan di Hotel Maluri, Kuala Lumpur, dengan '
                    'pembentangan laporan tahunan dan pemilihan ahli jawatankuasa sesi 2025-2026. Pada '
                    'tarikh yang sama, Presiden membentangkan ceramah "Role of MADOCS in Circumcision" '
                    'di persidangan antarabangsa.'),
        'ringkas_en': ('The second Annual General Meeting was held at Hotel Maluri, Kuala Lumpur, with the '
                       'annual report presented and the 2025-2026 committee elected. On the same day the '
                       'President presented "Role of MADOCS in Circumcision" at an international conference.'),
        'laporan': [
            ('Keahlian diluluskan dalam sesi mesyuarat sepanjang 2024 berjumlah 168 ahli, terdiri daripada 36 Life Member dan 132 Ordinary Member sehingga 21 November 2024.',
             'Membership approved through 2024 meetings totalled 168 members, comprising 36 Life Members and 132 Ordinary Members as at 21 November 2024.'),
        ],
    },
    {
        'slug': '2024-08-27-latihan-dorsal-slit-jurulatih',
        'kategori': 'Latihan',
        'tajuk': 'Latihan Teknik Dorsal Slit untuk Jurulatih Khatan',
        'tarikh': '2024-08-27',
        'tempat': '',
        'gambar': 'assets/galeri/program-2024/2024-20.webp',
        'gambar_alt': 'Dewan besar semasa program latihan MADOCS',
        'ringkas': ('Seramai 100 jurulatih khatan menamatkan latihan teknik dorsal slit dengan jayanya, '
                    'sebahagian daripada usaha menyediakan jurulatih bertauliah untuk kursus peringkat kebangsaan.'),
        'ringkas_en': ('One hundred circumcision trainers completed dorsal slit technique training, part of '
                       'the effort to prepare certified trainers for national-level courses.'),
        'laporan': [],
    },
    {
        'slug': '2024-09-14-ccc5-kota-kinabalu',
        'kategori': 'CCC',
        'tajuk': 'Comprehensive Circumcision Course 5 (CCC 5)',
        'tarikh': '2024-09-14',
        'tempat': 'Horizon Hotel, Kota Kinabalu, Sabah',
        'gambar': 'assets/galeri/program-2024/2024-03.webp',
        'gambar_alt': 'Peserta program komuniti MADOCS berkumpul di lokasi program',
        'ringkas': ('Kursus CCC 5 di Kota Kinabalu menumpukan latihan penggunaan peranti ZSR generasi '
                    'kedua dalam prosedur berkhatan, selain sesi teori asas khatan.'),
        'ringkas_en': ('CCC 5 in Kota Kinabalu focused on training with the second-generation ZSR device in '
                       'circumcision procedures, alongside basic theory sessions.'),
        'laporan': [],
    },
    {
        'slug': '2024-09-14-sunathon-madocs-ums',
        'kategori': 'Program',
        'tajuk': 'Sunathon MADOCS–UMS, Kota Kinabalu',
        'tarikh': '2024-09-14',
        'tempat': 'Universiti Malaysia Sabah, Kota Kinabalu, Sabah',
        'gambar': 'assets/galeri/program-2024/2024-21.webp',
        'gambar_alt': 'Ceramah khatan di hadapan sepanduk program jelajah khatan',
        'ringkas': ('Program khatan beramai-ramai bersama Universiti Malaysia Sabah, diteruskan sebagai '
                    'sebahagian daripada tanggungjawab sosial MADOCS bersama rakan kerjasama di Sabah.'),
        'ringkas_en': ('A mass circumcision programme with Universiti Malaysia Sabah, continuing MADOCS\' '
                       'social responsibility work with partners in Sabah.'),
        'laporan': [],
    },
    {
        'slug': '2024-10-23-privileging-course-part-1',
        'kategori': 'PCC',
        'tajuk': 'Privileging Course for Circumcision (Dorsal Slit) Part 1',
        'tarikh': '2024-10-23',
        'tempat': 'Hotel Raia, Kuala Terengganu, Terengganu',
        'gambar': 'assets/galeri/program-2024/2024-23.webp',
        'gambar_alt': 'Slaid kursus Privileging for Circumcision (Dorsal Slit) 23 Oktober 2024',
        'ringkas': ('Kursus privileging khatan dorsal slit yang pertama dianjurkan bersama Kementerian '
                    'Kesihatan untuk doktor swasta. Seramai 95 peserta menduduki kursus dan 92 lulus.'),
        'ringkas_en': ('The first dorsal slit circumcision privileging course organised with the Ministry of '
                       'Health for private doctors. 95 participants sat the course and 92 passed.'),
        'laporan': [],
    },
    {
        'slug': '2024-10-24-national-circumcision-symposium',
        'kategori': 'Persidangan',
        'tajuk': 'National Circumcision Symposium 2024',
        'tarikh': '2024-10-24',
        'tempat': 'Hotel Raia, Kuala Terengganu, Terengganu',
        'gambar': 'assets/galeri/program-2024/2024-24.webp',
        'gambar_alt': 'Gambar berkumpulan peserta National Circumcision Symposium 2024',
        'ringkas': ('Simposium khatan kebangsaan yang julung kali diadakan, anjuran Kementerian Kesihatan '
                    'Malaysia dengan kerjasama MADOCS, PERDIM dan MMA.'),
        'ringkas_en': ('The first national circumcision symposium, organised by the Ministry of Health with '
                       'MADOCS, PERDIM and MMA.'),
        'laporan': [
            ('Simposium menjadi platform pertemuan penggubal dasar, pakar bedah dan pengamal khatan dari seluruh negara.',
             'The symposium became a meeting platform for policymakers, surgeons and circumcision practitioners from across the country.'),
        ],
    },
]

TAJUK_EN = {
    'Siri Mesyuarat Garis Panduan Khatan Kebangsaan 2024': 'National Circumcision Guidelines Meeting Series 2024',
    'Comprehensive Circumcision Course 3 (CCC 3)': 'Comprehensive Circumcision Course 3 (CCC 3)',
    'Program Train The Trainer HRDC, Sunway Nexus': 'HRDC Train The Trainer Programme, Sunway Nexus',
    'Mesyuarat Agung Tahunan ke-2 dan Persidangan Antarabangsa': 'Second Annual General Meeting and International Conference',
    'Latihan Teknik Dorsal Slit untuk Jurulatih Khatan': 'Dorsal Slit Technique Training for Circumcision Trainers',
    'Comprehensive Circumcision Course 5 (CCC 5)': 'Comprehensive Circumcision Course 5 (CCC 5)',
    'Sunathon MADOCS–UMS, Kota Kinabalu': 'MADOCS–UMS Sunathon, Kota Kinabalu',
    'Privileging Course for Circumcision (Dorsal Slit) Part 1': 'Privileging Course for Circumcision (Dorsal Slit) Part 1',
    'National Circumcision Symposium 2024': 'National Circumcision Symposium 2024',
}

TEMPAT_EN = {
    'Cyberjaya, Port Dickson, Genting Highlands dan Putrajaya': 'Cyberjaya, Port Dickson, Genting Highlands and Putrajaya',
    'Bayview Hotel dan H-Medical Centre, Pulau Pinang': 'Bayview Hotel and H-Medical Centre, Penang',
    'Sunway Nexus, Kota Damansara, Selangor': 'Sunway Nexus, Kota Damansara, Selangor',
    'Hotel Maluri, Taman Maluri, Kuala Lumpur': 'Hotel Maluri, Taman Maluri, Kuala Lumpur',
    'Horizon Hotel, Kota Kinabalu, Sabah': 'Horizon Hotel, Kota Kinabalu, Sabah',
    'Universiti Malaysia Sabah, Kota Kinabalu, Sabah': 'Universiti Malaysia Sabah, Kota Kinabalu, Sabah',
    'Hotel Raia, Kuala Terengganu, Terengganu': 'Hotel Raia, Kuala Terengganu, Terengganu',
}

ALT_EN = {bm: en for _s, _n, bm, en in PILIHAN}

ALBUM_BM = ('Album program MADOCS sepanjang 2024: kursus komprehensif berkhatan, latihan jurulatih, '
            'mesyuarat garis panduan kebangsaan, kursus privileging pertama dan simposium khatan '
            'kebangsaan. Gambar pesakit dan prosedur tidak diterbitkan.')
ALBUM_EN = ('Album of MADOCS programmes through 2024: comprehensive circumcision courses, trainer '
            'training, national guideline meetings, the first privileging course and the national '
            'circumcision symposium. Patient and procedure photographs are not published.')


def tukar_imej():
    bil = 0
    for sumber, nama, _bm, _en in PILIHAN:
        asal = SUMBER / sumber
        if not asal.exists():
            print('tiada:', sumber)
            continue
        with Image.open(asal) as im:
            im = im.convert('RGB')
            if im.width > 1400:
                im = im.resize((1400, round(im.height * 1400 / im.width)), Image.LANCZOS)
            im.save(TUJUAN / nama, format='WEBP', quality=82, method=6)
        bil += 1
    print('imej ditukar:', bil)


def tulis_galeri():
    p = AKAR / 'data' / 'galeri.json'
    d = json.loads(p.read_text(encoding='utf-8'))
    d['album'] = [a for a in d['album'] if a['slug'] != 'program-2024']
    gambar = [{'src': 'assets/galeri/program-2024/%s' % nama, 'alt': bm}
              for _s, nama, bm, _en in PILIHAN if (TUJUAN / nama).exists()]
    d['album'].append({
        'slug': 'program-2024',
        'tajuk': 'Program MADOCS 2024',
        'tarikh': '2024-12-31',
        'kategori': 'Program',
        'ringkas': ALBUM_BM,
        'gambar': gambar,
    })
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('album program-2024:', len(gambar), 'gambar')


def tulis_aktiviti():
    p = AKAR / 'data' / 'aktiviti.json'
    d = json.loads(p.read_text(encoding='utf-8'))
    ada = {a['slug'] for a in d['aktiviti']}
    for a in AKTIVITI:
        item = {k: v for k, v in a.items() if k not in ('ringkas_en',)}
        item['laporan'] = [bm for bm, _en in a.get('laporan', [])]
        if item['slug'] in ada:
            d['aktiviti'] = [item if x['slug'] == item['slug'] else x for x in d['aktiviti']]
        else:
            d['aktiviti'].append(item)
    d['aktiviti'].sort(key=lambda x: x['tarikh'])
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('aktiviti 2024:', len(AKTIVITI), '| jumlah keseluruhan:', len(d['aktiviti']))


def tulis_terjemahan():
    p = AKAR / 'data' / 'terjemahan.json'
    kamus = json.loads(p.read_text(encoding='utf-8'))
    bil = 0
    for a in AKTIVITI:
        pasangan = [(a['tajuk'], TAJUK_EN.get(a['tajuk'], a['tajuk'])),
                    (a['ringkas'], a['ringkas_en']),
                    (a.get('gambar_alt', ''), ALT_EN.get(a.get('gambar_alt', ''), a.get('gambar_alt', '')))]
        if a.get('tempat'):
            pasangan.append((a['tempat'], TEMPAT_EN.get(a['tempat'], a['tempat'])))
        for bm, en in a.get('laporan', []):
            pasangan.append((bm, en))
        for bm, en in pasangan:
            if bm and en:
                kamus[bm] = en
                bil += 1
    kamus['Program MADOCS 2024'] = 'MADOCS Programme 2024'
    kamus[ALBUM_BM] = ALBUM_EN
    for _s, _n, bm, en in PILIHAN:
        kamus[bm] = en
        bil += 1
    p.write_text(json.dumps(kamus, ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    print('terjemahan ditambah:', bil, '| jumlah kamus:', len(kamus))


if __name__ == '__main__':
    tukar_imej()
    tulis_galeri()
    tulis_aktiviti()
    tulis_terjemahan()
