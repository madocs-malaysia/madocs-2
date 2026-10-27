#!/usr/bin/env python3
"""Import Laporan Aktiviti MADOCS 2025 → entri aktiviti + album galeri + terjemahan.

Nota percanggahan tarikh (disemak silang dengan laporan 2024):
  - CCC5: laporan 2025 letak 9/2/2025; laporan 2024 letak 14/9/2024 (Horizon Hotel, Kota Kinabalu).
  - PCC2-1 & CCC7: laporan 2025 letak 12/9/2025; rekod urusetia di laman 13/9/2025.
  - "TWG Bil. 7/2024, 4-6 September 2025" ialah entri 2024 yang tersalin ke laporan 2025 — tidak
    dimasukkan sebagai aktiviti 2025.
"""
import json
from pathlib import Path

from PIL import Image

SUMBER = Path('/home/ubuntu/.hermes/profiles/madocs/cache/scratch/laporan2025')
AKAR = Path('/home/ubuntu/madocs-site')
TUJUAN = AKAR / 'assets' / 'galeri' / 'program-2025'
TUJUAN.mkdir(parents=True, exist_ok=True)

PILIHAN = [
    ('image2.jpeg', '2025-01.webp', 'Penyampaian cenderamata semasa program MADOCS 2025', 'Presentation of a memento at a MADOCS 2025 programme'),
    ('image3.jpeg', '2025-02.webp', 'Program komuniti MADOCS bersama penduduk setempat', 'MADOCS community programme with local residents'),
    ('image4.jpeg', '2025-03.webp', 'Peserta beratur di kaunter program komuniti MADOCS', 'Participants queueing at a MADOCS community programme counter'),
    ('image5.jpeg', '2025-04.webp', 'Peserta memenuhi dewan semasa majlis MADOCS', 'Participants filling the hall at a MADOCS ceremony'),
    ('image8.jpeg', '2025-05.webp', 'Pentas Program Sunathon 2025 dengan sepanduk penganjur', 'Sunathon 2025 stage with the organisers\' banner'),
    ('image11.jpeg', '2025-06.webp', 'Gambar berkumpulan peserta Program Sunathon 2025 di atas pentas', 'Group photograph of Sunathon 2025 participants on stage'),
    ('image12.jpeg', '2025-07.webp', 'Ahli MADOCS bergambar di luar bangunan program', 'MADOCS members photographed outside the programme venue'),
    ('image13.jpeg', '2025-08.webp', 'Gambar berkumpulan di pintu masuk lokasi kursus', 'Group photograph at the entrance of the course venue'),
    ('image15.jpeg', '2025-09.webp', 'Dewan persidangan dipenuhi peserta', 'Conference hall filled with participants'),
    ('image16.jpeg', '2025-10.webp', 'Peserta kursus bergambar di hadapan bangunan', 'Course participants photographed in front of the building'),
    ('image18.jpeg', '2025-11.webp', 'Jurulatih berkhatan dalam sesi latihan amali', 'Circumcision trainers during a hands-on training session'),
    ('image19.jpeg', '2025-12.webp', 'Peserta mesyuarat di meja panjang', 'Meeting participants at a long table'),
    ('image20.jpeg', '2025-13.webp', 'Mesyuarat Technical Working Group bersama wakil Kementerian Kesihatan', 'Technical Working Group meeting with Ministry of Health representatives'),
    ('image24.jpeg', '2025-14.webp', 'Kaunter pendaftaran peserta program MADOCS', 'Participant registration counter at a MADOCS programme'),
    ('image29.jpeg', '2025-15.webp', 'Penceramah menyampaikan kuliah di hadapan peserta', 'Speaker delivering a lecture to participants'),
    ('image30.jpeg', '2025-16.webp', 'Peserta melawat booth pameran semasa program', 'Participants visiting exhibition booths during a programme'),
    ('image33.jpeg', '2025-17.webp', 'Penceramah di hadapan latar Privileging Course for Circumcision (Dorsal Slit)', 'Speaker in front of the Privileging Course for Circumcision (Dorsal Slit) backdrop'),
    ('image34.jpeg', '2025-18.webp', 'Dua penceramah di pentas program MADOCS', 'Two speakers on stage at a MADOCS programme'),
    ('image40.jpeg', '2025-19.webp', 'Gambar berkumpulan peserta program di dewan utama', 'Group photograph of programme participants in the main hall'),
    ('image41.jpeg', '2025-20.webp', 'Ahli dan peserta berbual semasa jamuan program', 'Members and participants chatting during a programme dinner'),
    ('image42.jpeg', '2025-21.webp', 'Ahli jawatankuasa MADOCS bergambar bersama', 'MADOCS committee members photographed together'),
    ('image46.jpeg', '2025-22.webp', 'Peserta simposium di dewan utama', 'Symposium participants in the main hall'),
    ('image48.jpeg', '2025-23.webp', 'Pentas program kebangsaan dengan dua wakil penganjur', 'National programme stage with two organisers\' representatives'),
    ('image49.jpeg', '2025-24.webp', 'Dua peserta menerima pengiktirafan di atas pentas', 'Two participants receiving recognition on stage'),
    ('image51.jpeg', '2025-25.webp', 'Barisan penceramah di pentas program kebangsaan', 'Panel of speakers on the national programme stage'),
]

AKTIVITI = [
    {
        'slug': '2025-02-09-ccc5',
        'kategori': 'CCC',
        'tajuk': 'Comprehensive Circumcision Course 5 (CCC 5)',
        'tarikh': '2025-02-09',
        'tempat': '',
        'gambar': 'assets/galeri/program-2025/2025-10.webp',
        'gambar_alt': 'Peserta kursus bergambar di hadapan bangunan',
        'ringkas': ('Kursus komprehensif berkhatan MADOCS diteruskan pada 2025 dengan siri kelima. '
                    'Laporan Aktiviti 2025 merekodkan tarikh 9 Februari 2025.'),
        'ringkas_en': ('MADOCS\' comprehensive circumcision course continued in 2025 with its fifth '
                       'series. The 2025 Activity Report records the date as 9 February 2025.'),
        'laporan': [
            ('Nota: Laporan Aktiviti 2024 merekodkan CCC 5 pada 14 September 2024 di Horizon Hotel, Kota Kinabalu. Tarikh dan lokasi sebenar perlu disahkan oleh urusetia.',
             'Note: the 2024 Activity Report records CCC 5 on 14 September 2024 at Horizon Hotel, Kota Kinabalu. The actual date and venue should be confirmed by the secretariat.'),
        ],
    },
    {
        'slug': '2025-04-13-mesyuarat-ajk-bil-2',
        'kategori': 'Mesyuarat',
        'tajuk': 'Mesyuarat Ahli Jawatankuasa Bil. 2/2025',
        'tarikh': '2025-04-13',
        'tempat': 'YaHala Restaurant, Chulan, Kuala Lumpur',
        'gambar': 'assets/galeri/program-2025/2025-12.webp',
        'gambar_alt': 'Peserta mesyuarat di meja panjang',
        'ringkas': ('Mesyuarat ahli jawatankuasa kedua sesi 2025 diadakan di YaHala Restaurant, Chulan, '
                    'dengan kehadiran 11 daripada 13 ahli jawatankuasa.'),
        'ringkas_en': ('The second committee meeting of the 2025 session was held at YaHala Restaurant, '
                       'Chulan, with 11 of 13 committee members present.'),
        'laporan': [
            ('Sepanjang 2025, empat mesyuarat ahli jawatankuasa direkodkan dengan kadar kehadiran antara 7 hingga 13 daripada 13 ahli.',
             'Four committee meetings were recorded in 2025, with attendance ranging from 7 to 13 out of 13 members.'),
        ],
    },
    {
        'slug': '2025-05-26-mesyuarat-pelaksanaan-ccc6',
        'kategori': 'Mesyuarat',
        'tajuk': 'Mesyuarat Pelaksanaan CCC 6',
        'tarikh': '2025-05-26',
        'tempat': '',
        'gambar': '',
        'gambar_alt': '',
        'ringkas': ('Mesyuarat pelaksanaan bagi kursus CCC 6 yang diadakan di Hotel Maluri, Cheras pada '
                    '1 Jun 2025, meliputi pendaftaran peserta, tenaga pengajar dan persiapan latihan amali.'),
        'ringkas_en': ('The implementation meeting for CCC 6, held at Hotel Maluri, Cheras on 1 June 2025, '
                       'covering participant registration, faculty and hands-on training preparation.'),
        'laporan': [],
    },
    {
        'slug': '2025-07-22-twg-bil-5-melaka',
        'kategori': 'Dasar',
        'tajuk': 'Mesyuarat TWG Panduan Berkhatan KKM Bil. 5/2025',
        'tarikh': '2025-07-22',
        'tempat': 'Melaka',
        'gambar': 'assets/galeri/program-2025/2025-13.webp',
        'gambar_alt': 'Mesyuarat Technical Working Group bersama wakil Kementerian Kesihatan',
        'ringkas': ('Mesyuarat Technical Working Group Garis Panduan Berkhatan Kementerian Kesihatan '
                    'Malaysia Bil. 5/2025 diadakan di Melaka selama tiga hari, menyambung semakan draf '
                    'garis panduan kebangsaan.'),
        'ringkas_en': ('Technical Working Group meeting 5/2025 for the Ministry of Health Circumcision '
                       'Guidelines was held in Melaka over three days, continuing the review of the '
                       'national guideline draft.'),
        'laporan': [],
    },
    {
        'slug': '2025-08-10-lawatan-tapak-pcc2-1',
        'kategori': 'Mesyuarat',
        'tajuk': 'Mesyuarat Pelaksanaan dan Lawatan Tapak PCC 2-1, Batu Pahat',
        'tarikh': '2025-08-10',
        'tempat': 'Klinik Kurnia, Batu Pahat, Johor',
        'gambar': 'assets/galeri/program-2025/2025-16.webp',
        'gambar_alt': 'Peserta melawat booth pameran semasa program',
        'ringkas': ('Mesyuarat pelaksanaan dan lawatan tapak bagi kursus PCC 2-1 di Batu Pahat, '
                    'sekaligus menjadi mesyuarat ahli jawatankuasa Bil. 3/2025 di Klinik Kurnia.'),
        'ringkas_en': ('Implementation meeting and site visit for the PCC 2-1 course in Batu Pahat, which '
                       'also served as committee meeting 3/2025 at Klinik Kurnia.'),
        'laporan': [
            ('Lawatan tapak memastikan dewan kuliah, ruang latihan amali dan peralatan mencukupi sebelum kursus pada September 2025.',
             'The site visit confirmed that the lecture hall, hands-on training space and equipment were adequate ahead of the September 2025 course.'),
        ],
    },
    {
        'slug': '2025-10-01-mesyuarat-pelaksanaan-pcc2-2',
        'kategori': 'Mesyuarat',
        'tajuk': 'Mesyuarat Pelaksanaan PCC 2-2',
        'tarikh': '2025-10-01',
        'tempat': 'Masjid Wilayah Persekutuan, Kuala Lumpur',
        'gambar': '',
        'gambar_alt': '',
        'ringkas': ('Mesyuarat pelaksanaan bagi kursus PCC 2-2 yang diadakan di Masjid Wilayah '
                    'Persekutuan pada 27 Disember 2025.'),
        'ringkas_en': ('Implementation meeting for PCC 2-2, held at Masjid Wilayah Persekutuan on '
                       '27 December 2025.'),
        'laporan': [],
    },
    {
        'slug': '2025-10-21-twg-meeting',
        'kategori': 'Dasar',
        'tajuk': 'Mesyuarat Technical Working Group, Oktober 2025',
        'tarikh': '2025-10-21',
        'tempat': '',
        'gambar': 'assets/galeri/program-2025/2025-13.webp',
        'gambar_alt': 'Mesyuarat Technical Working Group bersama wakil Kementerian Kesihatan',
        'ringkas': ('Mesyuarat Technical Working Group selama tiga hari pada Oktober 2025 bagi '
                    'meneruskan kerja penyiapan garis panduan khatan kebangsaan.'),
        'ringkas_en': ('A three-day Technical Working Group meeting in October 2025 to continue work on '
                       'the national circumcision guidelines.'),
        'laporan': [],
    },
    {
        'slug': '2025-10-24-munas-bogor',
        'kategori': 'Persidangan',
        'tajuk': 'MUNAS Bogor, Indonesia',
        'tarikh': '2025-10-24',
        'tempat': 'Bogor, Jawa Barat, Indonesia',
        'gambar': 'assets/galeri/program-2025/2025-18.webp',
        'gambar_alt': 'Dua penceramah di pentas program MADOCS',
        'ringkas': ('Wakil MADOCS menyertai MUNAS di Bogor, Indonesia, bagi mengeratkan hubungan dengan '
                    'pengamal khatan serantau dan mengikuti perkembangan amalan berkhatan di sana.'),
        'ringkas_en': ('MADOCS representatives attended MUNAS in Bogor, Indonesia, strengthening ties with '
                       'regional circumcision practitioners and following practice developments there.'),
        'laporan': [],
    },
    {
        'slug': '2025-11-22-mesyuarat-ajk-bil-4',
        'kategori': 'Mesyuarat',
        'tajuk': 'Mesyuarat Ahli Jawatankuasa Bil. 4/2025',
        'tarikh': '2025-11-22',
        'tempat': 'Qasar Balqis Restaurant, Ampang, Kuala Lumpur',
        'gambar': 'assets/galeri/program-2025/2025-21.webp',
        'gambar_alt': 'Ahli jawatankuasa MADOCS bergambar bersama',
        'ringkas': ('Mesyuarat ahli jawatankuasa terakhir bagi 2025 diadakan di Qasar Balqis Restaurant, '
                    'Ampang, dengan kehadiran 12 daripada 13 ahli jawatankuasa.'),
        'ringkas_en': ('The final 2025 committee meeting was held at Qasar Balqis Restaurant, Ampang, with '
                       '12 of 13 committee members present.'),
        'laporan': [],
    },
]

TAJUK_EN = {
    'Comprehensive Circumcision Course 5 (CCC 5)': 'Comprehensive Circumcision Course 5 (CCC 5)',
    'Mesyuarat Ahli Jawatankuasa Bil. 2/2025': 'Committee Meeting No. 2/2025',
    'Mesyuarat Pelaksanaan CCC 6': 'CCC 6 Implementation Meeting',
    'Mesyuarat TWG Panduan Berkhatan KKM Bil. 5/2025': 'Ministry of Health Circumcision Guidelines TWG Meeting No. 5/2025',
    'Mesyuarat Pelaksanaan dan Lawatan Tapak PCC 2-1, Batu Pahat': 'PCC 2-1 Implementation Meeting and Site Visit, Batu Pahat',
    'Mesyuarat Pelaksanaan PCC 2-2': 'PCC 2-2 Implementation Meeting',
    'Mesyuarat Technical Working Group, Oktober 2025': 'Technical Working Group Meeting, October 2025',
    'MUNAS Bogor, Indonesia': 'MUNAS Bogor, Indonesia',
    'Mesyuarat Ahli Jawatankuasa Bil. 4/2025': 'Committee Meeting No. 4/2025',
}

TEMPAT_EN = {
    'YaHala Restaurant, Chulan, Kuala Lumpur': 'YaHala Restaurant, Chulan, Kuala Lumpur',
    'Melaka': 'Melaka',
    'Klinik Kurnia, Batu Pahat, Johor': 'Klinik Kurnia, Batu Pahat, Johor',
    'Masjid Wilayah Persekutuan, Kuala Lumpur': 'Masjid Wilayah Persekutuan, Kuala Lumpur',
    'Bogor, Jawa Barat, Indonesia': 'Bogor, West Java, Indonesia',
    'Qasar Balqis Restaurant, Ampang, Kuala Lumpur': 'Qasar Balqis Restaurant, Ampang, Kuala Lumpur',
}

ALBUM_BM = ('Album program MADOCS sepanjang 2025: kursus komprehensif berkhatan, kursus privileging, '
            'mesyuarat garis panduan bersama Kementerian Kesihatan, sunathon dan simposium kebangsaan. '
            'Gambar pesakit dan prosedur tidak diterbitkan.')
ALBUM_EN = ('Album of MADOCS programmes through 2025: comprehensive circumcision courses, the privileging '
            'course, guideline meetings with the Ministry of Health, sunathon and the national symposium. '
            'Patient and procedure photographs are not published.')


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
    d['album'] = [a for a in d['album'] if a['slug'] != 'program-2025']
    gambar = [{'src': 'assets/galeri/program-2025/%s' % nama, 'alt': bm}
              for _s, nama, bm, _en in PILIHAN if (TUJUAN / nama).exists()]
    d['album'].append({
        'slug': 'program-2025',
        'tajuk': 'Program MADOCS 2025',
        'tarikh': '2025-12-31',
        'kategori': 'Program',
        'ringkas': ALBUM_BM,
        'gambar': gambar,
    })
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('album program-2025:', len(gambar), 'gambar')


def tulis_aktiviti():
    p = AKAR / 'data' / 'aktiviti.json'
    d = json.loads(p.read_text(encoding='utf-8'))
    ada = {a['slug'] for a in d['aktiviti']}
    for a in AKTIVITI:
        item = {k: v for k, v in a.items() if k != 'ringkas_en'}
        item['laporan'] = [bm for bm, _en in a.get('laporan', [])]
        if item['slug'] in ada:
            d['aktiviti'] = [item if x['slug'] == item['slug'] else x for x in d['aktiviti']]
        else:
            d['aktiviti'].append(item)
    d['aktiviti'].sort(key=lambda x: x['tarikh'])
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('aktiviti 2025 baharu:', len(AKTIVITI), '| jumlah keseluruhan:', len(d['aktiviti']))


def tulis_terjemahan():
    p = AKAR / 'data' / 'terjemahan.json'
    kamus = json.loads(p.read_text(encoding='utf-8'))
    bil = 0
    for a in AKTIVITI:
        pasangan = [(a['tajuk'], TAJUK_EN.get(a['tajuk'], a['tajuk'])),
                    (a['ringkas'], a['ringkas_en'])]
        if a.get('gambar_alt'):
            pasangan.append((a['gambar_alt'], ALT_EN.get(a['gambar_alt'], a['gambar_alt'])))
        if a.get('tempat'):
            pasangan.append((a['tempat'], TEMPAT_EN.get(a['tempat'], a['tempat'])))
        pasangan += [(bm, en) for bm, en in a.get('laporan', [])]
        for bm, en in pasangan:
            if bm and en:
                kamus[bm] = en
                bil += 1
    kamus['Program MADOCS 2025'] = 'MADOCS Programme 2025'
    kamus[ALBUM_BM] = ALBUM_EN
    for _s, _n, bm, en in PILIHAN:
        kamus[bm] = en
        bil += 1
    p.write_text(json.dumps(kamus, ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    print('terjemahan ditambah:', bil)


ALT_EN = {bm: en for _s, _n, bm, en in PILIHAN}

if __name__ == '__main__':
    tukar_imej()
    tulis_galeri()
    tulis_aktiviti()
    tulis_terjemahan()
