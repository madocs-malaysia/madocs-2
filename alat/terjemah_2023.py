#!/usr/bin/env python3
"""Tambah terjemahan Inggeris untuk kandungan 2023 + dua pautan Pusat Sumber.

Bacaan: data/aktiviti.json (entri 2023), data/galeri.json (album program-2023),
data/sumber.json (MMC, MeRITS). Tulis ke data/terjemahan.json.
"""
import json
from pathlib import Path

AKAR = Path('/home/ubuntu/madocs-site')

RINGKAS = {
    '2023-02-18-ccc1': 'MADOCS\' first comprehensive course, featuring four circumcision methods with 5 lecturers and 12 hands-on trainers. 59 participants attended the course and 93 patients from the asnaf, poor and B40 groups benefited through the CSR programme sponsored by PPZ Wilayah Persekutuan.',
    '2023-02-26-micc-putrajaya': 'MADOCS took part in the Malaysian International Circumcision Conference 2023 in Putrajaya. The President delivered a lecture titled "Roles of MADOCS in Malaysia" and MADOCS also held a session with the media.',
    '2023-03-31-agm-pertama': 'The first Annual General Meeting was held at Hotel Tamu, Kampung Baru. At this meeting, the first batch of 85 members was approved, marking the start of formal membership of the society.',
    '2023-08-27-ccc2': 'The second comprehensive course featured five circumcision methods, 6 lecturers and 12 hands-on trainers. 57 participants joined the course and 76 patients received treatment through the CSR programme sponsored by PPZ Wilayah Persekutuan.',
    '2023-09-17-perak-circumcision-update': 'The President of MADOCS was invited to deliver the lecture "Introduction to MADOCS" at Perak Circumcision Update 2023, raising the society\'s profile at state level.',
    '2023-11-01-garis-panduan-khatan-kkm': 'MADOCS represented the private sector at the review meeting of the Ministry of Health Circumcision Guidelines. The meeting agreed to establish a National Circumcision Committee and MADOCS was given two seats.',
    '2023-12-31-mesyuarat-ajk-2023': 'In its first year, three committee meetings were recorded: 18 February at Hotel Maluri Cheras, 31 March at Hotel Tamu Kampung Baru and 2 July at Yahala Restaurant, Kuala Lumpur. Day-to-day matters were handled through the committee WhatsApp group.',
}

TEMPAT = {
    'Hotel Maluri Cheras, Hotel Tamu Kampung Baru dan Yahala Restaurant, Kuala Lumpur':
        'Hotel Maluri Cheras, Hotel Tamu Kampung Baru and Yahala Restaurant, Kuala Lumpur',
}

TAJUK = {
    'Mesyuarat Agung Tahunan Pertama MADOCS': 'MADOCS First Annual General Meeting',
    'Mesyuarat Semakan Garis Panduan Khatan KKM': 'Ministry of Health Circumcision Guidelines Review Meeting',
    'Perak Circumcision Update 2023': 'Perak Circumcision Update 2023',
    'Mesyuarat Ahli Jawatankuasa MADOCS Sesi 2023': 'MADOCS Committee Meetings, 2023 Session',
}

LAPORAN = {
    'Empat kaedah berkhatan diperkenalkan dalam kursus ini, dengan gabungan sesi kuliah dan latihan amali yang dikendalikan 12 jurulatih.':
        'Four circumcision methods were introduced in this course, combining lectures and hands-on training run by 12 trainers.',
    'Program CSR bersama PPZ Wilayah Persekutuan membolehkan 93 pesakit daripada golongan asnaf, fakir dan B40 menerima rawatan berkhatan tanpa bayaran.':
        'The CSR programme with PPZ Wilayah Persekutuan enabled 93 patients from the asnaf, poor and B40 groups to receive circumcision treatment free of charge.',
    'Ceramah "Roles of MADOCS in Malaysia" memperkenalkan peranan pertubuhan kepada peserta antarabangsa dan pengamal tempatan.':
        'The lecture "Roles of MADOCS in Malaysia" introduced the society\'s role to international participants and local practitioners.',
    'Kehadiran MADOCS dalam persidangan ini membuka ruang perbincangan dengan rakan NGO dan pihak berkepentingan industri berkhatan.':
        'MADOCS\' presence at the conference opened discussions with fellow NGOs and stakeholders in the circumcision industry.',
    'Seramai 85 ahli kumpulan pertama diluluskan keahliannya dalam mesyuarat ini.':
        'The first batch of 85 members had their membership approved at this meeting.',
    'Mesyuarat turut membincangkan hala tuju program latihan dan penyeragaman caj berkhatan.':
        'The meeting also discussed the direction of training programmes and standardisation of circumcision charges.',
    'Sebelas ahli baharu turut diluluskan keahliannya pada tarikh yang sama.':
        'Eleven new members were also approved on the same date.',
    'Sambutan peserta dan pesakit melebihi jangkaan, menyamai pencapaian kursus pertama.':
        'Response from participants and patients exceeded expectations, matching the first course.',
    'Ceramah memperkenalkan peranan, program latihan dan pendekatan keselamatan berkhatan yang dibawa MADOCS.':
        'The lecture introduced the role, training programmes and safe circumcision approach championed by MADOCS.',
    'Mesyuarat dihadiri Bahagian Amalan Perubatan, Bahagian Perkembangan Kesihatan Awam, Bahagian Pembangunan Kesihatan Keluarga, pakar bedah KKM serta wakil NGO perubatan.':
        'The meeting was attended by the Medical Practice Division, Public Health Development Division, Family Health Development Division, Ministry of Health surgeons and medical NGO representatives.',
    'Jawatankuasa Khatan Kebangsaan ditubuhkan untuk merangka garis panduan berkhatan, termasuk teknik dorsal slit, khatan di premis KKM dan swasta, khatan beramai-ramai, aspek medico-legal dan mekanisme rujukan komplikasi.':
        'A National Circumcision Committee was formed to draft circumcision guidelines covering the dorsal slit technique, circumcision in ministry and private premises, mass circumcision, medico-legal aspects and referral mechanisms for complications.',
    'Sektor swasta diwakili MADOCS (2 wakil), PERDIM, MMA dan APHM (seorang wakil setiap satu).':
        'The private sector was represented by MADOCS (2 representatives), PERDIM, MMA and APHM (one representative each).',
    'Mesyuarat dijalankan secara fizikal dengan pilihan hadir dalam talian bagi ahli yang berada jauh.':
        'Meetings were held physically, with an online option for members who were far away.',
    'Keputusan harian dibincangkan dalam kumpulan WhatsApp jawatankuasa dan direkodkan secara rasmi dalam mesyuarat.':
        'Day-to-day decisions were discussed in the committee WhatsApp group and recorded officially in meetings.',
}

ALBUM = {
    'Program MADOCS 2023': 'MADOCS Programme 2023',
    'Album tahun pertama MADOCS: kursus komprehensif berkhatan, persidangan antarabangsa, mesyuarat agung pertama dan program bersama Kementerian Kesihatan. Gambar pesakit dan prosedur tidak diterbitkan.':
        'Album of MADOCS\' first year: comprehensive circumcision courses, an international conference, the first annual general meeting and a programme with the Ministry of Health. Patient and procedure photographs are not published.',
}

SUMBER = {
    'Laman rasmi MMC: pendaftaran doktor, kod etika dan peraturan amalan perubatan di Malaysia. Halaman utama MMC agak berat; untuk semakan pantas, guna pautan carian pendaftaran doktor di bawah.':
        'Official Malaysian Medical Council site: doctor registration, code of ethics and medical practice regulations in Malaysia. The MMC home page is fairly heavy; for a quick check, use the doctor registration search link below.',
    'Semak status pendaftaran dan APC seseorang doktor dengan pantas. Halaman ringan, sesuai dibuka pada telefon.':
        'Check a doctor\'s registration and APC status quickly. A light page, suitable for opening on a phone.',
    'Carian pendaftaran doktor (MeRITS, Malaysian Medical Council)': 'Doctor registration search (MeRITS, Malaysian Medical Council)',
}

ALT_PELBAGAI = {
    'Penceramah menyampaikan kuliah semasa Comprehensive Circumcision Course 1': 'Speaker delivering a lecture at Comprehensive Circumcision Course 1',
    'Penceramah di pentas CCC 1 dengan latar sepanduk MADOCS dan PERDIM': 'Speaker on stage at CCC 1 with MADOCS and PERDIM banners',
    'Peserta kursus mengikuti sesi kuliah CCC 1': 'Course participants attending a CCC 1 lecture',
    'Pembentangan slaid semasa sesi kuliah CCC 1': 'Slide presentation during a CCC 1 lecture',
    'Penyampaian cek tajaan kepada penganjur semasa CCC 1': 'Presentation of a sponsorship cheque to the organisers at CCC 1',
    'Meja pendaftaran peserta di kaunter program CCC 1': 'Participant registration desk at CCC 1',
    'Peserta memenuhi ruang pameran semasa program CCC 1': 'Participants filling the exhibition area during CCC 1',
    'Booth pameran semasa Malaysian International Circumcision Conference 2023': 'Exhibition booth at the Malaysian International Circumcision Conference 2023',
    'Dua peserta berbincang di ruang pameran MICC 2023': 'Two participants in discussion at the MICC 2023 exhibition area',
    'Wakil MADOCS menyampaikan ceramah semasa MICC 2023': 'MADOCS representative delivering a lecture at MICC 2023',
    'Gambar berkumpulan peserta MICC 2023 di The Everly Hotel Putrajaya': 'Group photograph of MICC 2023 participants at The Everly Hotel Putrajaya',
    'Ahli mesyuarat di Mesyuarat Agung Tahunan Pertama MADOCS': 'Members at the MADOCS First Annual General Meeting',
    'Perbincangan di meja mesyuarat semasa AGM pertama MADOCS': 'Discussion at the meeting table during the first MADOCS AGM',
    'Ahli jawatankuasa dalam sesi mesyuarat AGM pertama': 'Committee members during the first AGM session',
    'Gambar berkumpulan ahli selepas Mesyuarat Agung Tahunan Pertama': 'Group photograph of members after the First Annual General Meeting',
    'Penyampaian cenderamata sempena mesyuarat agung MADOCS': 'Presentation of a memento at the MADOCS general meeting',
    'Peserta kursus memenuhi dewan semasa Comprehensive Circumcision Course 2': 'Participants filling the hall at Comprehensive Circumcision Course 2',
    'Peserta mengikuti kuliah CCC 2 dengan tekun': 'Participants following the CCC 2 lecture attentively',
    'Penceramah menyampaikan kuliah di CCC 2': 'Speaker delivering a lecture at CCC 2',
    'Wakil MADOCS berucap di hadapan peserta CCC 2': 'MADOCS representative addressing CCC 2 participants',
    'Penyampaian plak penghargaan semasa CCC 2': 'Presentation of an appreciation plaque at CCC 2',
    'Bangunan Hotel Taiping Perdana, lokasi Perak Circumcision Update 2023': 'Hotel Taiping Perdana, venue of Perak Circumcision Update 2023',
    'Ahli jawatankuasa MADOCS dalam perbincangan meja bulat': 'MADOCS committee members in a round-table discussion',
    'Presiden MADOCS berjabat tangan dengan wakil rakan NGO': 'MADOCS President shaking hands with a partner NGO representative',
    'Gambar berkumpulan ahli MADOCS pada program 2023': 'Group photograph of MADOCS members at a 2023 programme',
    'Ahli dan peserta berbual semasa jamuan program MADOCS 2023': 'Members and participants chatting during the MADOCS 2023 programme dinner',
    'Penyediaan sijil keahlian MADOCS': 'Preparation of MADOCS membership certificates',
}


def utama():
    p = AKAR / 'data' / 'terjemahan.json'
    kamus = json.loads(p.read_text(encoding='utf-8'))

    aktiviti = json.loads((AKAR / 'data' / 'aktiviti.json').read_text(encoding='utf-8'))['aktiviti']
    tambah = 0
    for a in aktiviti:
        if not a['slug'].startswith('2023-'):
            continue
        if a['slug'] in RINGKAS:
            kamus[a['ringkas']] = RINGKAS[a['slug']]
            tambah += 1
        if a['tajuk'] in TAJUK:
            kamus[a['tajuk']] = TAJUK[a['tajuk']]
            tambah += 1
        if a.get('tempat') in TEMPAT:
            kamus[a['tempat']] = TEMPAT[a['tempat']]
            tambah += 1
        if a.get('gambar_alt'):
            kamus[a['gambar_alt']] = ALT_PELBAGAI.get(a['gambar_alt'], a['gambar_alt'])
            tambah += 1
        for par in a.get('laporan', []) or []:
            if par in LAPORAN:
                kamus[par] = LAPORAN[par]
                tambah += 1

    galeri = json.loads((AKAR / 'data' / 'galeri.json').read_text(encoding='utf-8'))['album']
    for al in galeri:
        if al['slug'] != 'program-2023':
            continue
        for kunci, nilai in ALBUM.items():
            if kunci in (al.get('tajuk'), al.get('ringkas')):
                kamus[kunci] = nilai
                tambah += 1
        for g in al.get('gambar', []):
            alt = g.get('alt', '')
            if alt in ALT_PELBAGAI:
                kamus[alt] = ALT_PELBAGAI[alt]
                tambah += 1

    for kunci, nilai in SUMBER.items():
        kamus[kunci] = nilai
        tambah += 1

    p.write_text(json.dumps(kamus, ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    print('entri terjemahan ditambah:', tambah, '| jumlah kamus:', len(kamus))


if __name__ == '__main__':
    utama()
