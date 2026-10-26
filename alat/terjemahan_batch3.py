#!/usr/bin/env python3
"""Batch terjemahan Inggeris (3): kapsyen/alt gambar, ringkasan berita, dan pemetaan identiti."""
import json
import pathlib

P = pathlib.Path("/home/ubuntu/madocs-site/data/terjemahan.json")
d = json.loads(P.read_text(encoding="utf-8"))

baru = {
    # --- alt / kapsyen gambar ---
    "Ahli dan Ahli Jawatankuasa MADOCS bergambar bersama sepanduk MALAYSIAN DOCTORS OF CIRCUMCISION SOCIETY pada Mesyuarat Agung Tahunan Ke-4, 2026":
        "MADOCS members and committee posing with the MALAYSIAN DOCTORS OF CIRCUMCISION SOCIETY banner at the 4th Annual General Meeting, 2026",
    "Album program di The Katerina Hotel, Batu Pahat: Priviling Course for Circumcision Part 2 (PCC2-1) dan Comprehensive Circumcision Course 7 (CCC7) pada 13 September 2025":
        "Programme album at The Katerina Hotel, Batu Pahat: Privileging Course for Circumcision Part 2 (PCC2-1) and Comprehensive Circumcision Course 7 (CCC7) on 13 September 2025",
    "Booth pameran peranti berkhatan dengan sepanduk perbandingan kaedah semasa program CME MADOCS":
        "Circumcision device exhibition booth with a method comparison banner during a MADOCS CME programme",
    "Dewan kursus PCC2-1 dan CCC7 di The Katerina Hotel, Batu Pahat penuh dengan peserta, dengan sepanduk kursus dan sepanduk MADOCS di pentas":
        "The PCC2-1 and CCC7 course hall at The Katerina Hotel, Batu Pahat filled with participants, with course and MADOCS banners on stage",
    "Dr. Abdol Rashid bin Masrom, Presiden Pertubuhan Doktor Khatan Malaysia (MADOCS)":
        "Dr. Abdol Rashid bin Masrom, President of the Malaysian Doctors of Circumcision Society (MADOCS)",
    "Gambar diambil semasa program MADOCS dan diterbitkan untuk tujuan dokumentasi pertubuhan. Ibu bapa, penjaga atau peserta yang ingin gambar tertentu dibuang boleh menghubungi urusetia MADOCS. Kami akan memadamkannya.":
        "Photographs were taken during MADOCS programmes and published for the society's documentation. Parents, guardians or participants who wish a particular photo to be removed may contact the MADOCS secretariat. We will delete it.",
    "Penceramah menerangkan anatomi dan anestesia tempatan kepada peserta kursus CCC6 di Hotel Maluri, Cheras":
        "A speaker explaining anatomy and local anaesthesia to CCC6 participants at Hotel Maluri, Cheras",
    "Penceramah menerangkan langkah-langkah prosedur Dorsal Slit pada slaid semasa kursus PCC di Kota Kinabalu":
        "A speaker explaining the steps of the Dorsal Slit procedure on a slide during a PCC course in Kota Kinabalu",
    "Peserta dan fasilitator kursus Privileging Course for Circumcision (Dorsal Slit) Part 2 bergambar bersama sepanduk kursus di The Katerina Hotel, Batu Pahat":
        "Participants and facilitators of the Privileging Course for Circumcision (Dorsal Slit) Part 2 with the course banner at The Katerina Hotel, Batu Pahat",
    "Peserta kursus mempelajari prosedur Dorsal Slit dalam sesi amali MADOCS":
        "Course participants learning the Dorsal Slit procedure in a MADOCS practical session",
    "Poster Ceramah CME Tissue Adhesives dalam Berkhatan Pediatrik":
        "Poster for the CME talk on Tissue Adhesives in Paediatric Circumcision",
    "Poster Promosi Keahlian Seumur Hidup MADOCS 2026 dengan kadar yuran, maklumat pembayaran dan kod QR pendaftaran":
        "MADOCS 2026 Life Membership Promotion poster with fee rates, payment details and a registration QR code",
    "Poster webinar CME 24 November 2026, 2.00-3.00 petang (Teams). Anjuran bersama PERDIM dan MADOCS, penaja Asumed Biotech.":
        "CME webinar poster, 24 November 2026, 2.00-3.00 pm (Teams). Co-organised by PERDIM and MADOCS, sponsored by Asumed Biotech.",
    "Poster webinar CME Beyond the Conventional Clamp, The Role of Tissue Adhesives in Pediatric Circumcision, 24 November 2026, Teams Webinar, anjuran PERDIM dan MADOCS":
        "CME webinar poster: Beyond the Conventional Clamp, The Role of Tissue Adhesives in Pediatric Circumcision, 24 November 2026, Teams Webinar, organised by PERDIM and MADOCS",
    "Foto lokasi: Muhammad Faqih, Wikimedia Commons (CC BY-SA 4.0), bukan gambar acara MADOCS":
        "Location photo: Muhammad Faqih, Wikimedia Commons (CC BY-SA 4.0) — not a MADOCS event photo",

    # --- ringkasan berita/aktiviti ---
    "Privileging Course for Circumcision Part 2 (PCC2-1) dan Comprehensive Circumcision Course 7 (CCC7) berlangsung serentak pada 13 September 2025 di The…":
        "Privileging Course for Circumcision Part 2 (PCC2-1) and Comprehensive Circumcision Course 7 (CCC7) ran concurrently on 13 September 2025 at The…",
    "Program MADOCS 2026 (4 mata CPD) di Howard Johnson by Wyndham, Kuala Lumpur menggabungkan sesi CME, Jamuan Aidilfitri yang dihadiri 80 orang, dan AGM Ke-4…":
        "The MADOCS Programme 2026 (4 CPD points) at Howard Johnson by Wyndham, Kuala Lumpur combined a CME session, an Aidilfitri dinner attended by 80 people, and the 4th AGM…",
    "Train The Trainer (TTT) Teknoklem pada Sabtu 31 Mei 2025, sehari sebelum CCC6, di Hotel Maluri, Cheras. Sesi berpusat pada kaedah gam Teknoklem: penerangan…":
        "Teknoklem Train The Trainer (TTT) on Saturday 31 May 2025, a day before CCC6, at Hotel Maluri, Cheras. The session focused on the Teknoklem glue method: explanation…",
    "Comprehensive Circumcision Course 6 (CCC6) pada Ahad 1 Jun 2025 di Hotel Maluri, Cheras. Ceramah anatomi dan anestesia tempatan, kaedah Guillotine, Teknoklem…":
        "Comprehensive Circumcision Course 6 (CCC6) on Sunday 1 June 2025 at Hotel Maluri, Cheras. Lectures on anatomy and local anaesthesia, the Guillotine and Teknoklem methods…",
    "Delegasi MADOCS mengadakan lawatan kerja ke sebuah klinik berkhatan di Indonesia untuk berkongsi pengalaman dalam pengurusan perkhidmatan berkhatan…":
        "A MADOCS delegation made a working visit to a circumcision clinic in Indonesia to share experience in running circumcision services…",
    "Dua hari di Hotel Maluri, Cheras: Train The Trainer (TTT) Teknoklem pada 31 Mei 2025, dan Comprehensive Circumcision Course 6 (CCC6) pada 1 Jun 2025, ceramah anatomi":
        "Two days at Hotel Maluri, Cheras: Teknoklem Train The Trainer (TTT) on 31 May 2025 and Comprehensive Circumcision Course 6 (CCC6) on 1 June 2025, anatomy lectures",
    "Demo Peranti, Booth CME: 2 gambar dokumentasi program MADOCS. Koleksi galeri rasmi Pertubuhan Doktor Khatan Malaysia.":
        "Device Demo, CME Booth: 2 photos documenting a MADOCS programme. The official gallery of the Malaysian Doctors of Circumcision Society.",
    "Kursus PCC1-2 Kota Kinabalu: 6 gambar dokumentasi program MADOCS, 26 Januari 2026 · Kota Kinabalu, Sabah. Koleksi galeri rasmi Pertubuhan Doktor Khatan Malaysia.":
        "PCC1-2 Course, Kota Kinabalu: 6 photos documenting a MADOCS programme, 26 January 2026 · Kota Kinabalu, Sabah. The official gallery of the Malaysian Doctors of Circumcision Society.",
    "Kursus PCC2-3 Putrajaya: 5 gambar dokumentasi program MADOCS, 30 Mei 2026 · Masjid Putra, Putrajaya. Koleksi galeri rasmi Pertubuhan Doktor Khatan Malaysia.":
        "PCC2-3 Course, Putrajaya: 5 photos documenting a MADOCS programme, 30 May 2026 · Masjid Putra, Putrajaya. The official gallery of the Malaysian Doctors of Circumcision Society.",
    "Kursus PCC2-4 Semporna: 4 gambar dokumentasi program MADOCS, 18 Jun 2026 · Semporna, Sabah. Koleksi galeri rasmi Pertubuhan Doktor Khatan Malaysia.":
        "PCC2-4 Course, Semporna: 4 photos documenting a MADOCS programme, 18 June 2026 · Semporna, Sabah. The official gallery of the Malaysian Doctors of Circumcision Society.",
    "Majlis Pelancaran Garis Panduan Berkhatan 2026: 5 gambar dokumentasi program MADOCS, 17 September 2026 · Hospital Shah Alam, Selangor. Koleksi galeri rasmi Pertubuha":
        "Launch of the 2026 Circumcision Guidelines: 5 photos documenting a MADOCS programme, 17 September 2026 · Hospital Shah Alam, Selangor. The official gallery of the Malaysia",
    "Mesyuarat Ahli Jawatankuasa Bil. 2: 3 gambar dokumentasi program MADOCS, 16 September 2026 · Restoran Casar Balqis, Taman Melati, Kuala Lumpur. Koleksi galeri rasmi":
        "Committee Meeting No. 2: 3 photos documenting a MADOCS programme, 16 September 2026 · Restoran Casar Balqis, Taman Melati, Kuala Lumpur. The official gallery",
    "Program MADOCS 2026 (AGM Ke-4, CME &amp; Jamuan Aidilfitri): 14 gambar dokumentasi program MADOCS, 26 April 2026 · Howard Johnson by Wyndham, Kuala Lumpur. Koleksi gal":
        "MADOCS Programme 2026 (4th AGM, CME &amp; Aidilfitri Dinner): 14 photos documenting a MADOCS programme, 26 April 2026 · Howard Johnson by Wyndham, Kuala Lumpur. The official gall",

    # --- pemetaan identiti (sudah Inggeris / nama khas) ---
    "Credentialing &amp; Privileging": "Credentialing &amp; Privileging",
    "Credentialing &amp; Privileging (C&amp;P) | MADOCS": "Credentialing &amp; Privileging (C&amp;P) | MADOCS",
    "PCC2-1, CCC7 &amp; TTT, Batu Pahat": "PCC2-1, CCC7 &amp; TTT, Batu Pahat",
    "CCC6 &amp; TTT Teknoklem, Hotel Maluri, Cheras": "CCC6 &amp; TTT Teknoklem, Hotel Maluri, Cheras",
    "CCC7, PCC2-1 &amp; TTT Touchstone, Batu Pahat, Johor": "CCC7, PCC2-1 &amp; TTT Touchstone, Batu Pahat, Johor",
    "Hotel Maluri, Cheras, Kuala Lumpur": "Hotel Maluri, Cheras, Kuala Lumpur",
    "Masjid Putra, Putrajaya, lokasi kursus CCC 9": "Masjid Putra, Putrajaya, venue of the CCC 9 course",
    "&middot;\n        Telefon:": "&middot; Phone:",
}

ditambah = 0
for k, v in baru.items():
    if d.get(k) != v:
        d[k] = v
        ditambah += 1
teks = json.dumps({k: d[k] for k in sorted(d)}, ensure_ascii=False, indent=1)
P.write_text(teks if teks.endswith("\n") else teks + "\n", encoding="utf-8")
print("batch 3 — entri:", ditambah, "| jumlah:", len(d))
