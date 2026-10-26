#!/usr/bin/env python3
"""Tambah terjemahan Inggeris bagi rentetan baharu (Ahli Kehormat, hak mengundi, yuran perlembagaan, nama rasmi)."""
import json
import pathlib

P = pathlib.Path("/home/ubuntu/madocs-site/data/terjemahan.json")
d = json.loads(P.read_text(encoding="utf-8"))

baharu = {
    "Ahli Kehormat": "Honorary Member",
    "Apakah Ahli Kehormat?": "What is an Honorary Member?",
    "Ahli Kehormat ialah pakar bedah, doktor atau individu yang telah menyumbang dalam bidang berkhatan dan diiktiraf pertubuhan. Mereka dilantik khas oleh Ahli Jawatankuasa dan tidak dikenakan sebarang yuran (Perlembagaan Kl. 4.1 dan 6.1.4).":
        "Honorary Members are surgeons, doctors or individuals who have contributed to the field of circumcision and are recognised by the society. They are appointed specially by the Committee and pay no fees (Constitution Cl. 4.1 and 6.1.4).",
    "Pakar bedah, doktor atau individu yang telah menyumbang dalam bidang berkhatan dan diiktiraf pertubuhan; dilantik khas oleh Ahli Jawatankuasa":
        "Surgeons, doctors or individuals who have contributed to the field of circumcision and are recognised by the society; appointed specially by the Committee",
    "Tiada yuran": "No fee",
    "Tiada yuran masuk atau tahunan; lantikan khas oleh Ahli Jawatankuasa (Perlembagaan Kl. 6.1.4)":
        "No entrance or annual fee; by special appointment of the Committee (Constitution Cl. 6.1.4)",
    "Yuran masuk RM100 + yuran tahunan RM100 (Perlembagaan Kl. 6.1.1)":
        "Entrance fee RM100 + annual fee RM100 (Constitution Cl. 6.1.1)",
    "Yuran masuk RM100 + yuran tahunan RM100 (Perlembagaan Kl. 6.1.2)":
        "Entrance fee RM100 + annual fee RM100 (Constitution Cl. 6.1.2)",
    "Yuran masuk RM25 + yuran tahunan RM25 (Perlembagaan Kl. 6.1.3)":
        "Entrance fee RM25 + annual fee RM25 (Constitution Cl. 6.1.3)",
    "Yuran masuk RM100 + RM900 (promosi 2026). Harga biasa RM1,100 (Perlembagaan Kl. 6.1.5)":
        "Entrance fee RM100 + RM900 (2026 promotion). Regular price RM1,100 (Constitution Cl. 6.1.5)",
    "Biasa &amp; Bersekutu RM100; Pelajar RM25 (Perlembagaan Kl. 6.1)":
        "Ordinary &amp; Associate RM100; Student RM25 (Constitution Cl. 6.1)",
    "Hak mengundi:": "Voting rights:",
    "Hak mengundi dalam Mesyuarat Agung terhad kepada Ahli Biasa. Ahli Bersekutu dan Ahli Pelajar tidak layak mengundi (Perlembagaan Kl. 7.1).":
        "Voting rights at the General Meeting are limited to Ordinary Members. Associate and Student Members are not eligible to vote (Constitution Cl. 7.1).",
    "Siapa yang layak mengundi dalam Mesyuarat Agung?": "Who is eligible to vote at the General Meeting?",
    "Hanya Ahli Biasa. Ahli Bersekutu dan Ahli Pelajar tidak layak mengundi (Perlembagaan Kl. 7.1).":
        "Ordinary Members only. Associate and Student Members are not eligible to vote (Constitution Cl. 7.1).",
    "Pertubuhan Doktor Khatan Malaysia (Malaysian Doctors of Circumcision Society, MADOCS)":
        "Malaysian Doctors of Circumcision Society (Pertubuhan Doktor Khatan Malaysia, MADOCS)",
    "Kategori, kelayakan dan yuran diambil daripada Perlembagaan MADOCS (Klausa 4 dan 6); pertubuhan ini didaftarkan dengan Pendaftar Pertubuhan Malaysia. Promosi Keahlian Seumur Hidup 2026 ialah keputusan Ahli Jawatankuasa. Jawatankuasa boleh mengemas kini pada bila-bila masa.":
        "Categories, eligibility and fees are taken from the MADOCS Constitution (Clauses 4 and 6); the society is registered with the Registrar of Societies Malaysia. The 2026 Life Membership Promotion is a Committee decision. The Committee may update these at any time.",
}

ditambah = 0
for k, v in baharu.items():
    if d.get(k) != v:
        d[k] = v
        ditambah += 1

teks = json.dumps({k: d[k] for k in sorted(d)}, ensure_ascii=False, indent=1)
if not teks.endswith("\n"):
    teks += "\n"
P.write_text(teks, encoding="utf-8")
print("entri ditambah/dikemas kini:", ditambah, "| jumlah:", len(d))
