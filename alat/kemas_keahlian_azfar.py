#!/usr/bin/env python3
"""Kemas kini data/keahlian.json + data/site.json mengikut keputusan Dr Azfar (20 Okt 2026).

1. Yuran Ahli Pelajar ikut Perlembagaan: RM25 masuk + RM25 tahunan.
2. Tambah kategori Ahli Kehormat (tiada yuran, lantikan jawatankuasa).
3. Nama rasmi: Pertubuhan Doktor Khatan Malaysia (Malaysian Doctors of Circumcision Society, MADOCS).
4. Hak mengundi: hanya Ahli Biasa.
"""
import json
import pathlib

DATA = pathlib.Path("/home/ubuntu/madocs-site/data")


def muat(nama):
    return json.loads((DATA / nama).read_text(encoding="utf-8"))


def simpan(nama, data):
    teks = json.dumps(data, ensure_ascii=False, indent=1)
    if not teks.endswith("\n"):
        teks += "\n"
    (DATA / nama).write_text(teks, encoding="utf-8")


# ---------------------------------------------------------------- keahlian.json
kh = muat("keahlian.json")

kh["kategori"] = [
    {"nama": "Ahli Biasa",
     "kelayakan": "Doktor perubatan yang berdaftar dengan Majlis Perubatan Malaysia (MMC)"},
    {"nama": "Ahli Bersekutu",
     "kelayakan": "Kakitangan perubatan yang terlibat dalam prosedur berkhatan"},
    {"nama": "Ahli Pelajar",
     "kelayakan": "Pelajar perubatan"},
    {"nama": "Ahli Kehormat",
     "kelayakan": "Pakar bedah, doktor atau individu yang telah menyumbang dalam bidang berkhatan "
                  "dan diiktiraf pertubuhan; dilantik khas oleh Ahli Jawatankuasa"},
    {"nama": "Ahli Seumur Hidup",
     "kelayakan": "Ahli yang memilih keahlian seumur hidup"},
]

kh["yuran"] = [
    {"kategori": "Ahli Biasa", "yuran": "RM200",
     "nota": "Yuran masuk RM100 + yuran tahunan RM100 (Perlembagaan Kl. 6.1.1)"},
    {"kategori": "Ahli Bersekutu", "yuran": "RM200",
     "nota": "Yuran masuk RM100 + yuran tahunan RM100 (Perlembagaan Kl. 6.1.2)"},
    {"kategori": "Ahli Pelajar", "yuran": "RM50",
     "nota": "Yuran masuk RM25 + yuran tahunan RM25 (Perlembagaan Kl. 6.1.3)"},
    {"kategori": "Ahli Kehormat", "yuran": "Tiada yuran",
     "nota": "Tiada yuran masuk atau tahunan; lantikan khas oleh Ahli Jawatankuasa (Perlembagaan Kl. 6.1.4)"},
    {"kategori": "Ahli Seumur Hidup", "yuran": "RM1,000",
     "nota": "Yuran masuk RM100 + RM900 (promosi 2026). Harga biasa RM1,100 (Perlembagaan Kl. 6.1.5)"},
    {"kategori": "Naik taraf Biasa ke Seumur Hidup", "yuran": "RM900",
     "nota": "Bayar yuran seumur hidup sahaja (promosi 2026; biasa RM1,000)"},
    {"kategori": "Pembaharuan tahunan", "yuran": "RM100 / RM25",
     "nota": "Biasa & Bersekutu RM100; Pelajar RM25 (Perlembagaan Kl. 6.1)"},
]

kh["hak_undi"] = ("Hak mengundi dalam Mesyuarat Agung terhad kepada Ahli Biasa. "
                  "Ahli Bersekutu dan Ahli Pelajar tidak layak mengundi (Perlembagaan Kl. 7.1).")

# FAQ: tambah dua soalan baharu (kehormat + hak mengundi) selepas soalan sedia ada.
faq = kh.get("faq", [])
tajuk_wujud = {f["s"] for f in faq}
baharu = [
    {"s": "Apakah Ahli Kehormat?",
     "j": "Ahli Kehormat ialah pakar bedah, doktor atau individu yang telah menyumbang dalam bidang "
          "berkhatan dan diiktiraf pertubuhan. Mereka dilantik khas oleh Ahli Jawatankuasa dan tidak "
          "dikenakan sebarang yuran (Perlembagaan Kl. 4.1 dan 6.1.4)."},
    {"s": "Siapa yang layak mengundi dalam Mesyuarat Agung?",
     "j": "Hanya Ahli Biasa. Ahli Bersekutu dan Ahli Pelajar tidak layak mengundi (Perlembagaan Kl. 7.1)."},
]
for f in baharu:
    if f["s"] not in tajuk_wujud:
        faq.append(f)
kh["faq"] = faq

kh["sumber_nota"] = (
    "Kategori, kelayakan dan yuran diambil daripada Perlembagaan MADOCS (Klausa 4 dan 6); "
    "pertubuhan ini didaftarkan dengan Pendaftar Pertubuhan Malaysia. Promosi Keahlian Seumur "
    "Hidup 2026 ialah keputusan Ahli Jawatankuasa. Jawatankuasa boleh mengemas kini pada bila-bila masa."
)
simpan("keahlian.json", kh)

# ---------------------------------------------------------------- site.json
st = muat("site.json")
st["nama_rasmi"] = ("Pertubuhan Doktor Khatan Malaysia "
                    "(Malaysian Doctors of Circumcision Society, MADOCS)")
simpan("site.json", st)

print("keahlian.json: kategori=%d, yuran=%d, faq=%d" % (len(kh["kategori"]), len(kh["yuran"]), len(kh["faq"])))
print("site.json: nama_rasmi =", st["nama_rasmi"])
