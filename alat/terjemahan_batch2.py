#!/usr/bin/env python3
"""Batch terjemahan Inggeris — betulkan rentetan BM yang masih muncul di halaman /en/."""
import json
import pathlib

P = pathlib.Path("/home/ubuntu/madocs-site/data/terjemahan.json")
d = json.loads(P.read_text(encoding="utf-8"))

baru = {
    # --- Organisasi ---
    "MADOCS ditadbir urus oleh 13 orang ahli lembaga yang diketuai oleh Presiden, Naib Presiden, Setiausaha, Penolong Setiausaha, Bendahari dan 8 orang Ahli Jawatankuasa. Pertubuhan ini turut dibantu oleh":
        "MADOCS is governed by 13 board members led by a President, Vice President, Secretary, Assistant Secretary, Treasurer and 8 Committee Members. The organisation is also assisted by",
    "orang Penasihat.": "Advisors.",
    "Jawatankuasa Eksekutif: Sesi 2026-2028": "Executive Committee: Session 2026-2028",
    "Organisasi &amp; jawatankuasa": "Organisation &amp; committee",

    # --- Tentang ---
    "MADOCS didaftarkan dengan Pendaftar Pertubuhan Malaysia pada 23 Ogos 2022 di bawah nombor pendaftaran PPM-020-10-23082022 (ROS).":
        "MADOCS is registered with the Registrar of Societies Malaysia on 23 August 2022 under registration number PPM-020-10-23082022 (ROS).",
    "Dasar Privasi Pertubuhan Doktor Khatan Malaysia (MADOCS): persatuan profesional doktor yang terlibat dalam amalan berkhatan di Malaysia.":
        "Privacy Policy of the Malaysian Doctors of Circumcision Society (MADOCS): a professional society of doctors involved in circumcision practice in Malaysia.",
    "Terma Penggunaan Pertubuhan Doktor Khatan Malaysia (MADOCS): persatuan profesional doktor yang terlibat dalam amalan berkhatan di Malaysia.":
        "Terms of Use of the Malaysian Doctors of Circumcision Society (MADOCS): a professional society of doctors involved in circumcision practice in Malaysia.",
    "Pernyataan ini dikemas kini pada Oktober 2026 dan akan disemak semula apabila laman":
        "This statement was updated in October 2026 and will be reviewed when the site",
    "Dari Meja Presiden: perutusan daripada Presiden Pertubuhan Doktor Khatan Malaysia (MADOCS), Dr. Abdol Rashid bin Masrom.":
        "From the President's Desk: a message from the President of the Malaysian Doctors of Circumcision Society (MADOCS), Dr. Abdol Rashid bin Masrom.",

    # --- Pengesahan ahli / sijil ---
    ": aktif, tamat tempoh, atau ditangguh.": ": active, expired or suspended.",
    ": Ahli Biasa, Bersekutu, Pelajar atau Seumur Hidup.": ": Ordinary, Associate, Student or Life Member.",
    "Pengesahan Sijil C&amp;P": "Certificate Verification (C&amp;P)",
    "Pengesahan Sijil C&amp;P | MADOCS": "Certificate Verification (C&amp;P) | MADOCS",
    "Sahkan keaslian sijil Credentialing &amp; Privileging (C&amp;P) MADOCS dengan nombor siri sijil.":
        "Verify the authenticity of a MADOCS Credentialing &amp; Privileging (C&amp;P) certificate using its serial number.",
    "Sahkan sijil": "Verify certificate",
    "Bagaimana pengesahan berfungsi": "How verification works",
    "Nombor siri sijil": "Certificate serial number",
    "Nombor siri tercetak di bahagian bawah sijil, di sebelah kod QR. Contoh:":
        "The serial number is printed at the bottom of the certificate, next to the QR code. Example:",
    "Hospital dan pihak berkuasa boleh mengesahkan sijil Credentialing &amp; Privileging (C&amp;P) MADOCS di sini, tanpa perlu memaklumkan data peribadi pemegang sijil.":
        "Hospitals and authorities can verify a MADOCS Credentialing &amp; Privileging (C&amp;P) certificate here, without disclosing the holder's personal data.",
    "Setiap sijil MADOCS mempunyai": "Every MADOCS certificate has",
    "nombor siri unik": "a unique serial number",
    "kod QR": "QR code",
    "hash SHA-256": "SHA-256 hash",
    "fail sijil.": "certificate file.",
    "Untuk mengesahkan, masukkan nombor siri, sistem memaparkan kursus, tarikh, mata CPD dan":
        "To verify, enter the serial number; the system displays the course, date, CPD points and",
    "tidak menyimpan kad pengenalan atau nombor MMC": "does not store identity card or MMC numbers",
    "Rekod awam ini": "This public record",
    "dan": "and",

    # --- Sumber / C&P ---
    "Borang Permohonan Keahlian (dalam talian)": "Membership Application Form (online)",
    "Borang rasmi permohonan keahlian MADOCS. Permohonan dibentangkan dalam mesyuarat Ahli Jawatankuasa; nombor ahli diberikan selepas diluluskan.":
        "Official MADOCS membership application form. Applications are tabled at the Committee meeting; member numbers are issued once approved.",
    "Buka borang pendaftaran keahlian MADOCS": "Open the MADOCS membership registration form",
    "Buka pautan": "Open link",
    "Muat turun": "Download",
    "Nota": "Note",
    "Objektif pembelajaran": "Learning objectives",
    "Kapasiti peserta": "Participant capacity",
    "Tarikh tentatif": "Tentative date",
    "Tenaga pengajar": "Instructors",
    "Rangka program": "Programme outline",
    "Tutup pendaftaran": "Registration closes",
    "Langkah 5": "Step 5",
    "Aliran C&amp;P MADOCS: penilaian kecekapan doktor untuk prosedur berkhatan, dengan pengurusan melalui portal iHealth.":
        "The MADOCS C&amp;P pathway: competency assessment for doctors performing circumcision, managed through the iHealth portal.",
    "Ada pertanyaan tentang C&amp;P?": "Questions about C&amp;P?",
    "Keputusan Ahli Jawatankuasa C&amp;P": "C&amp;P Committee decision",
    "Malaysian Medical Council: pendaftaran dan garis panduan": "Malaysian Medical Council: registration and guidelines",
    "Laman rasmi MMC: pendaftaran doktor, kod etika dan peraturan amalan perubatan di Malaysia.":
        "The official MMC site: doctor registration, code of ethics and medical practice regulations in Malaysia.",
    "PERDIM: Pertubuhan Doktor-Doktor Islam Malaysia": "PERDIM: Malaysian Islamic Doctors' Organisation",
    "Penilaian klinikal, peperiksaan teori dan penilaian stesen amali":
        "Clinical assessment, theory examination and practical station assessment",
    "Semua aktiviti MADOCS": "All MADOCS activities",
    "Poster Keahlian Seumur Hidup MADOCS 2026": "MADOCS 2026 Life Membership Poster",
    "Poster rasmi yuran keahlian 2026 termasuk kategori, kadar bayaran dan maklumat akaun bank persatuan.":
        "Official 2026 membership fee poster including categories, rates and the society's bank account details.",
    "40 gambar": "40 photos",
    "89 gambar": "89 photos",

    # --- Tajuk/meta kursus, galeri, berita ---
    "Kursus Privileging Berkhatan (Dorsal Slit) PCC 2-5: PCC 2-5 | MADOCS":
        "Circumcision Privileging Course (Dorsal Slit) PCC 2-5: PCC 2-5 | MADOCS",
    "PCC2-1, Batu Pahat, Johor | Aktiviti MADOCS": "PCC2-1, Batu Pahat, Johor | MADOCS Activities",
    "PCC2-1, CCC7 &amp; TTT, Batu Pahat | Galeri MADOCS": "PCC2-1, CCC7 &amp; TTT, Batu Pahat | MADOCS Gallery",
    "CCC6 &amp; TTT Teknoklem, Hotel Maluri, Cheras | Galeri MADOCS":
        "CCC6 &amp; TTT Teknoklem, Hotel Maluri, Cheras | MADOCS Gallery",
    "CCC6, Hotel Maluri, Cheras, Kuala Lumpur | Aktiviti MADOCS":
        "CCC6, Hotel Maluri, Cheras, Kuala Lumpur | MADOCS Activities",
    "CCC7, PCC2-1 &amp; TTT Touchstone, Batu Pahat, Johor | Aktiviti MADOCS":
        "CCC7, PCC2-1 &amp; TTT Touchstone, Batu Pahat, Johor | MADOCS Activities",
    "TTT Teknoklem, Hotel Maluri, Cheras, Kuala Lumpur | Aktiviti MADOCS":
        "TTT Teknoklem, Hotel Maluri, Cheras, Kuala Lumpur | MADOCS Activities",
    "Ceramah CME oleh Presiden | Berita MADOCS": "CME Talk by the President | MADOCS News",
    "Program MADOCS 2026 (AGM Ke-4, CME &amp; Jamuan… | Galeri MADOCS":
        "MADOCS Programme 2026 (4th AGM, CME &amp; Dinner… | MADOCS Gallery",
    "Program MADOCS 2026, CME, Jamuan Aidilfitri &amp; AGM… | Aktiviti MADOCS":
        "MADOCS Programme 2026, CME, Aidilfitri Dinner &amp; AGM… | MADOCS Activities",
    "Program MADOCS 2026: CME, Jamuan Aidilfitri dan AGM… | Berita MADOCS":
        "MADOCS Programme 2026: CME, Aidilfitri Dinner and AGM… | MADOCS News",
    "Lawatan Kerja MADOCS ke Klinik Sunat Kanak-kanak di… | Berita MADOCS":
        "MADOCS Working Visit to a Paediatric Circumcision Clinic in… | MADOCS News",
    "MADOCS dalam Media: 150 Kanak-kanak Dirai dalam… | Berita MADOCS":
        "MADOCS in the Media: 150 Children Hosted at… | MADOCS News",
    "Pertubuhan Doktor Khatan Malaysia (MADOCS): keahlian, kursus PCC/CCC, latihan klinikal dan garis panduan berkhatan untuk doktor di Malaysia.":
        "Malaysian Doctors of Circumcision Society (MADOCS): membership, PCC/CCC courses, clinical training and circumcision guidelines for doctors in Malaysia.",

    # --- Berita/aktiviti ringkas ---
    "Dr Abdol Rashid bin Masrom dijemput membentangkan penggunaan pelekat tisu (tissue adhesive) dalam berkhatan pediatrik pada webinar CME bersama PERDIM, 24 November 2026, 2.00-3.00 petang.":
        "Dr Abdol Rashid bin Masrom has been invited to present on the use of tissue adhesive in paediatric circumcision at a CME webinar with PERDIM, 24 November 2026, 2.00-3.00 pm.",
    "Dr Abdol Rashid bin Masrom dijemput membentangkan penggunaan pelekat tisu (tissue adhesive) dalam berkhatan pediatrik pada webinar CME bersama PERDIM, 24…":
        "Dr Abdol Rashid bin Masrom has been invited to present on the use of tissue adhesive in paediatric circumcision at a CME webinar with PERDIM, 24…",
    "Presiden MADOCS, Dr Abdol Rashid bin Masrom, dijemput menyampaikan ceramah CME bertajuk &quot;Beyond the Conventional Clamp, The Role of Tissue Adhesives in Pediatric Circumcision&quot;. Sesi ini dianjurkan bersama Pertubuhan Doktor-Doktor Islam Malaysia (PERDIM) dan MADOCS.":
        "MADOCS President, Dr Abdol Rashid bin Masrom, has been invited to deliver a CME talk titled &quot;Beyond the Conventional Clamp, The Role of Tissue Adhesives in Pediatric Circumcision&quot;. The session is co-organised with the Malaysian Islamic Doctors' Organisation (PERDIM) and MADOCS.",
    "MADOCS mengucapkan terima kasih kepada Presiden dan Ahli Jawatankuasa PERDIM kerana bersetuju menjemput Presiden MADOCS, dan kepada Asumed Biotech selaku penaja program.":
        "MADOCS thanks the President and Committee of PERDIM for inviting the MADOCS President, and Asumed Biotech as programme sponsor.",
    "Halaman yang anda cari tidak dijumpai. Kembali ke laman utama MADOCS atau gunakan carian untuk mencari maklumat yang anda perlukan.":
        "The page you are looking for was not found. Return to the MADOCS homepage or use search to find what you need.",
}

ditambah = 0
for k, v in baru.items():
    if d.get(k) != v:
        d[k] = v
        ditambah += 1

teks = json.dumps({k: d[k] for k in sorted(d)}, ensure_ascii=False, indent=1)
P.write_text(teks if teks.endswith("\n") else teks + "\n", encoding="utf-8")
print("entri ditambah/dikemas kini:", ditambah, "| jumlah:", len(d))
