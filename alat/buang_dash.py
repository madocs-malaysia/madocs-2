#!/usr/bin/env python3
"""Ganti tanda sempang panjang (em dash) dengan ayat/tanda baca yang wajar.

Latar: teks laman menggunakan "—" sebagai penghubung, yang memberi rasa tulisan
mesin. Skrip ini menukarnya kepada koma, noktah bertindih atau ayat baharu yang
lebih natural dalam Bahasa Melayu, dan menyelaraskan kamus terjemahan.

Guna: python3 alat/buang_dash.py [--tulis]
"""
import json
import pathlib
import re
import sys

AKAR = pathlib.Path('/home/ubuntu/madocs-site')

# Ayat penuh yang perlu ditulis semula (bukan sekadar tukar tanda baca).
OVERRIDE = {
    "Ditubuhkan pada 2022 — kini berusia empat tahun — Pertubuhan Doktor Khatan Malaysia (MADOCS) ialah":
        "Ditubuhkan pada 2022 dan kini berusia empat tahun, Pertubuhan Doktor Khatan Malaysia (MADOCS) ialah",
    "Established in 2022 — now four years old — the Malaysian Doctor of Circumcision Society (MADOCS) is":
        "Established in 2022 and now four years old, the Malaysian Doctor of Circumcision Society (MADOCS) is",
    "Kepada ahli-ahli dan rakan sekerja yang telah menyumbang tenaga, masa dan kepakaran — terima kasih.":
        "Kepada ahli dan rakan sekerja yang telah menyumbang tenaga, masa dan kepakaran, saya ucapkan terima kasih.",
    "To the members and colleagues who have contributed their energy, time and expertise — thank you.":
        "To the members and colleagues who have contributed their energy, time and expertise, thank you.",
    "Credentialing ialah proses menyemak kelayakan seorang doktor — ijazah perubatan, pendaftaran MMC, latihan berkhatan dan rekod log kes.":
        "Credentialing ialah proses menyemak kelayakan seorang doktor, iaitu ijazah perubatan, pendaftaran MMC, latihan berkhatan dan rekod log kes.",
    "Credentialing is the process of verifying a doctor's qualifications — medical degree, MMC registration, circumcision training and case-log records.":
        "Credentialing is the process of verifying a doctor's qualifications: medical degree, MMC registration, circumcision training and case-log records.",
    "MADOCS mahu maklumat tentang pertubuhan, kursus dan keahlian boleh diakses oleh semua orang —":
        "MADOCS mahu maklumat tentang pertubuhan, kursus dan keahlian boleh diakses oleh semua orang,",
    "MADOCS wants information about the society, its courses and membership to be accessible to everyone —":
        "MADOCS wants information about the society, its courses and membership to be accessible to everyone,",
    "Jika anda menghadapi masalah mengakses mana-mana bahagian laman ini — teks yang tidak boleh dibaca,":
        "Jika anda menghadapi masalah mengakses mana-mana bahagian laman ini, seperti teks yang tidak boleh dibaca,",
    "If you have difficulty accessing any part of this site — text you cannot read,":
        "If you have difficulty accessing any part of this site, such as text you cannot read,",
    "Kosmo! — “150 kanak-kanak dirai dalam program khatan MADOCS”":
        "Kosmo!: “150 kanak-kanak dirai dalam program khatan MADOCS”",
    "Kosmo! — “150 children hosted in the MADOCS circumcision programme”":
        "Kosmo!: “150 children hosted in the MADOCS circumcision programme”",
    "Dari Meja Presiden — perutusan daripada Presiden":
        "Dari Meja Presiden: perutusan daripada Presiden",
    "From the President's Desk — a message from the President":
        "From the President's Desk: a message from the President",
    "From the President's Pen — a message from the President":
        "From the President's Pen: a message from the President",
    "Pena Presiden Pertubuhan Doktor Khatan Malaysia (MADOCS) — perutusan daripada Presiden":
        "Pena Presiden: perutusan daripada Presiden",
    "Kod QR pada poster memerlukan log masuk akaun Google. Guna butang di atas — urusetia boleh bantu pendaftaran melalui WhatsApp.":
        "Kod QR pada poster memerlukan log masuk akaun Google. Guna butang di atas. Urusetia boleh bantu pendaftaran melalui WhatsApp.",
    "The QR code on the poster requires a Google account login. Use the button above — the secretariat can help with registration via WhatsApp.":
        "The QR code on the poster requires a Google account login. Use the button above. The secretariat can help with registration via WhatsApp.",
    "Complete the application form online — the “Fill in the membership form” and “Start application” buttons open the official form.":
        "Complete the application form online. The “Fill in the membership form” and “Start application” buttons open the official form.",
    "Foto lokasi: Muhammad Faqih, Wikimedia Commons (CC BY-SA 4.0) — bukan gambar acara MADOCS":
        "Foto lokasi: Muhammad Faqih, Wikimedia Commons (CC BY-SA 4.0), bukan gambar acara MADOCS",
    "Brosur rasmi MADOCS (2023) — jawatankuasa diminta mengesahkan kategori untuk sesi semasa.":
        "Brosur rasmi MADOCS (2023). Jawatankuasa diminta mengesahkan kategori untuk sesi semasa.",
    "Semak status keahlian MADOCS dengan nombor ahli — tanpa mendedahkan data peribadi.":
        "Semak status keahlian MADOCS dengan nombor ahli tanpa mendedahkan data peribadi.",
    "Check MADOCS membership status with a member number — without exposing personal data.":
        "Check MADOCS membership status with a member number, without exposing personal data.",
    "Beyond the Conventional Clamp — The Role of Tissue Adhesives in Pediatric Circumcision":
        "Beyond the Conventional Clamp: The Role of Tissue Adhesives in Pediatric Circumcision",
    "Poster Ceramah CME — Tissue Adhesives dalam Berkhatan Pediatrik":
        "Poster Ceramah CME Tissue Adhesives dalam Berkhatan Pediatrik",
}

# Label pendek yang diikuti senarai → noktah bertindih
LABEL = (
    'Status keahlian', 'Kategori', 'Tarikh sah', 'Nama bertopeng', 'Penilaian klinikal',
    'Membership status', 'Category', 'Valid until', 'Masked name', 'Clinical assessment',
    '404', 'Malaysian Medical Council', 'PERDIM', 'MADOCS',
)


def tukar(teks):
    """Tukar satu rentetan: override dahulu, kemudian peraturan tanda baca."""
    if teks in OVERRIDE:
        return OVERRIDE[teks]

    # julat tahun: 2026–2028 → 2026-2028
    teks = teks.replace('\u2013', '-')

    if '\u2014' not in teks:
        return teks

    # label diikuti senarai
    for label in LABEL:
        if teks.startswith(label + ' \u2014'):
            return teks.replace(label + ' \u2014', label + ':', 1)

    # "…petugas — termasuk 20 jurulatih … — serta" → kurungan
    teks = re.sub(r'\s\u2014\s(termasuk[^\u2014]{0,90})\s\u2014\s', r' (\1), ', teks)

    # "…MADOCS) — perutusan…" → noktah bertindih
    teks = teks.replace(') \u2014 ', '): ')

    # baki: koma
    teks = re.sub(r'\s*\u2014\s*', ', ', teks)
    teks = re.sub(r',\s*,', ',', teks)
    return teks


def proses_json(laluan, tulis):
    d = json.loads(laluan.read_text(encoding='utf-8'))
    berubah = 0

    def jalan(obj):
        nonlocal berubah
        if isinstance(obj, str):
            baru = tukar(obj)
            if baru != obj:
                berubah += 1
            return baru
        if isinstance(obj, list):
            return [jalan(x) for x in obj]
        if isinstance(obj, dict):
            return {jalan(k) if isinstance(k, str) else k: jalan(v) for k, v in obj.items()}
        return obj

    d2 = jalan(d)
    if tulis and berubah:
        laluan.write_text(json.dumps(d2, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return berubah


def proses_py(laluan, tulis):
    asal = laluan.read_text(encoding='utf-8')
    baru = asal
    # hanya ganti rentetan yang mengandungi em dash
    for lama, ganti in OVERRIDE.items():
        if lama in baru:
            baru = baru.replace(lama, ganti)
    # peraturan umum untuk corak "X — Y" dalam rentetan HTML
    baru = re.sub(r'(?<=\w) \u2014 (?=[a-z])', ', ', baru)
    baru = re.sub(r'(?<=\w) \u2014 (?=[A-Z])', ': ', baru)
    baru = baru.replace('\u2013', '-')
    if tulis and baru != asal:
        laluan.write_text(baru, encoding='utf-8')
    return asal.count('\u2014') - baru.count('\u2014')


def main():
    tulis = '--tulis' in sys.argv
    jumlah = 0
    for f in sorted((AKAR / 'data').glob('*.json')):
        n = proses_json(f, tulis)
        if n:
            print('%-28s %3d rentetan' % (f.name, n))
            jumlah += n
    n = proses_py(AKAR / 'build.py', tulis)
    print('%-28s %3d em dash' % ('build.py', n))
    jumlah += n
    print('\njumlah perubahan:', jumlah, '| ditulis:', tulis)


if __name__ == '__main__':
    main()
