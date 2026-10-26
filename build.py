#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Penjana laman statik MADOCS 2.0 (madocs.my)

Cara guna:
    python3 build.py            # bina semua halaman ke folder ini
    python3 build.py --report   # tunjuk kandungan yang masih belum disediakan

Kandungan yang boleh diubah terletak dalam folder data/*.json.
Jangan sunting fail .html terus, ia ditulis semula oleh skrip ini.
"""

import json
import html
import re
import shutil
import sys
import urllib.parse
from pathlib import Path
from datetime import date, datetime

import terjemah

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
ICON_DIR = ROOT / "_icons"

HARI = ["Isnin", "Selasa", "Rabu", "Khamis", "Jumaat", "Sabtu", "Ahad"]
BULAN = ["Januari", "Februari", "Mac", "April", "Mei", "Jun", "Julai",
         "Ogos", "September", "Oktober", "November", "Disember"]
BULAN_SING = ["JAN", "FEB", "MAC", "APR", "MEI", "JUN", "JUL", "OGO", "SEP", "OKT", "NOV", "DIS"]

# Jalur kredensial disembunyikan sementara (Dr Azfar, Okt 2026). Tukar kepada True untuk papar semula.
TUNJUK_KREDENSIAL = False


def _blok_kredensial(isi: str) -> str:
    if not TUNJUK_KREDENSIAL:
        return ""
    return '<section class="credential-band">\n  <div class="shell credential-grid">%s</div>\n</section>' % isi


# Kad kongsi sosial (og:image). Fail: assets/og-madocs.png, 1200x630 (nisbah 1.91:1).
GAMBAR_OG_LALAI = "/assets/og-madocs.png"
OG_SAIZ = (1200, 630)

STATUS_LABEL = {
    "tentatif": ("Tarikh tentatif", "tentatif"),
    "open": ("Pendaftaran dibuka", "open"),
    "limited": ("Kerusi terhad", "limited"),
    "closed": ("Pendaftaran ditutup", "closed"),
    "done": ("Selesai", "done"),
}


# ----------------------------------------------------------------- utiliti
def esc(s):
    return html.escape(str(s), quote=True)


def wa_nombor():
    """Nombor WhatsApp urusetia dalam format antarabangsa tanpa tanda (untuk wa.me).

    Guna site.json → whatsapp (boleh berbeza daripada nombor telefon am), jika tidak ada
    jatuh balik kepada telefon.
    """
    return re.sub(r"\D", "", str(SITE.get("whatsapp") or SITE.get("telefon", "")))


# Konteks WhatsApp semasa membina halaman:
#   "ahli" = urusan keahlian → setiausaha keahlian (Madihah)
#   None   = nombor am persatuan (footer, topbar halaman umum)
_WA_KONTEKS = None
LALUAN_AHLI = ("semak-ahli", "member-verification", "sahkan", "keahlian", "membership", "certificate")


def wa_pautan(teks="", nombor=None):
    """Pautan WhatsApp ke urusetia, dengan mesej sedia taip.

    Di halaman urusan ahli (keahlian, semakan ahli, pengesahan sijil) pautan ini
    menghala kepada setiausaha keahlian (Madihah); di halaman lain, nombor am.
    """
    no = nombor or (wa_keahlian_nombor() if _WA_KONTEKS == "ahli" else wa_nombor())
    asas = "https://wa.me/%s" % no
    return asas + ("?text=" + urllib.parse.quote(teks) if teks else "")


def wa_keahlian_nombor():
    """Nombor WhatsApp urusetia keahlian (Madihah) — untuk semua urusan ahli.

    Semua urusan keahlian, semakan status ahli dan pengesahan sijil halakan kepada
    urusetia keahlian, bukan nombor am persatuan. Sumber: data/keahlian.json → urusan.
    """
    k = load("keahlian.json")
    urus = (k.get("urusan") or (k.get("promosi") or {}).get("urusan") or {})
    no = re.sub(r"\D", "", str(urus.get("whatsapp") or ""))
    return no or wa_nombor()


MESEJ_WA_UMUM = "Salam, saya ingin bertanya tentang MADOCS."


def kotak_bantuan(tajuk, teks, mesej=None, nombor=None):
    """Kotak bantuan kontekstual: WhatsApp + e-mel urusetia (corak RCOG/RCGP)."""
    return f"""<div class="card kotak-bantuan">
  <h3>{esc(tajuk)}</h3>
  <p>{esc(teks)}</p>
  <a class="btn-blok wa" href="{wa_pautan(mesej or MESEJ_WA_UMUM, nombor)}" target="_blank" rel="noopener">{icon('message-circle')} WhatsApp urusetia</a>
  <a class="btn-blok ghost" href="mailto:{esc(SITE['email'])}" style="margin-top:9px">{icon('mail')} E-mel urusetia</a>
</div>"""


def blok_promosi_keahlian(kh):
    """Kad promosi keahlian (poster + yuran + bayaran + WhatsApp urusetia).

    Sumber: poster rasmi jawatankuasa MADOCS 2026 (data/keahlian.json → promosi).
    """
    pr = kh.get("promosi") or {}
    if not pr.get("aktif"):
        return ""
    kad = "".join(
        '<div class="kad-yuran"><small>%s</small>%s<strong>%s</strong></div>'
        % (esc(y["nama"]),
           ("<s>%s</s>" % esc(y["harga_asas"])) if y.get("harga_asas") else "",
           esc(y["harga"]))
        for y in pr.get("yuran", []))
    bay = pr.get("bayaran") or {}
    urus = pr.get("urusan") or {}
    # Pautan borang dalam talian: hanya jika jawatankuasa beri pautan yang benar-benar
    # terbuka kepada awam. Kod QR pada poster memerlukan log masuk Google (HTTP 401),
    # jadi pautan itu tidak boleh dipakai sebagai ganti.
    borang_url = (pr.get("borang_url") or "").strip()
    butang_borang = ('<a class="btn-blok borang" href="%s" target="_blank" rel="noopener">%s Isi borang keahlian dalam talian</a>'
                     % (esc(borang_url), icon("file-text"))) if borang_url else ""
    pautan_wa = "https://wa.me/%s?text=%s" % (
        re.sub(r"\D", "", str(urus.get("whatsapp", ""))),
        urllib.parse.quote("Salam, saya ingin mendaftar / naik taraf keahlian seumur hidup MADOCS."))
    pautan_form = borang_url or pautan_wa
    baris_bayar = "".join(
        "<p><span>%s</span><b>%s</b></p>" % (esc(label), esc(bay.get(kunci, "")))
        for kunci, label in (("bank", "Bank"), ("akaun", "Nombor akaun"), ("nama_akaun", "Nama akaun")))
    return ("""<section class="content-wrap seksyen-rose" style="padding-top:0">
  <div class="shell">
    <div class="promosi">
      <div class="promosi-poster">
        <a class="poster-pautan" href="%s" target="_blank" rel="noopener"
           aria-label="Buka borang pendaftaran keahlian MADOCS">
          <img src="/%s" alt="%s" width="820" height="1025" loading="lazy" decoding="async">
        </a>
      </div>
      <div class="promosi-isi">
        <span class="chip promosi-chip">%s</span>
        <h2>%s</h2>
        <p>%s</p>
        <div class="promosi-yuran">%s</div>
        <div class="promosi-bayaran">
          <h3>Bayaran</h3>
          %s
        </div>
        <p class="amaran-bayaran">%s</p>
        <div class="promosi-aksi">
          %s
          <a class="btn-blok wa" href="%s" target="_blank" rel="noopener">%s WhatsApp %s (%s)</a>
        </div>
        <p class="nota-qr">Kod QR pada poster memerlukan log masuk akaun Google. Guna butang di atas. Urusetia boleh bantu pendaftaran melalui WhatsApp.</p>
        <p class="nota-isi">%s Sumber: %s.</p>
      </div>
    </div>
  </div>
</section>""" % (pautan_form, esc(pr.get("gambar", "")), esc(pr.get("gambar_alt", "")), esc(pr.get("chip", "Promosi")),
                 esc(pr.get("tajuk", "")), esc(pr.get("pengenalan", "")), kad, baris_bayar,
                 esc(pr.get("amaran_bayaran", "")), butang_borang,
                 pautan_wa, icon("message-circle"), esc(urus.get("telefon", "")), esc(urus.get("nama", "")),
                 esc(pr.get("nota", "")), esc(pr.get("sumber", ""))))


def blok_struktur_organisasi(jk_data):
    """Carta organisasi (bilangan dan jawatan) daripada brosur rasmi MADOCS.

    Nama individu diisi kemudian melalui data/jawatankuasa.json → jawatankuasa[].
    Sumber: brosur rasmi "MADOCS Brochure 18012023".
    """
    st = jk_data.get("struktur") or {}
    if not st:
        return ""
    penasihat = jk_data.get("penasihat") or []
    ringkas = esc(st.get("ringkas", "")).rstrip(".")
    # Satu perenggan: ringkasan tadbir urus + bilangan penasihat.
    if penasihat:
        ringkas = ("%s. Pertubuhan ini turut dibantu oleh <b>%d</b> orang Penasihat." % (ringkas, len(penasihat)))

    # Kad bilangan dalam 7 lajur: Penasihat, Presiden, Naib Presiden, Setiausaha,
    # Penolong Setiausaha, Bendahari, Ahli Jawatankuasa.
    kad = []
    if penasihat:
        kad.append(("Penasihat", len(penasihat)))
    kad.extend((j["nama"], j.get("bilangan") or 1) for j in st.get("jawatan", []))
    kad_html = "".join(
        '<div class="struktur-kad"><b>%d</b><span>%s</span></div>' % (bil, esc(nama)) for nama, bil in kad)

    return ("""<div class="struktur">
  <p class="struktur-ringkas">%s</p>
  <div class="struktur-kad-grid">%s</div>
  <p class="struktur-tugas">%s</p>
</div>""" % (ringkas, kad_html, esc(st.get("tugas", "")).rstrip()))

def blok_sumber_berita(b):
    """Nota sumber untuk berita yang memetik liputan media luar."""
    if not b.get("sumber_teks"):
        return ""
    teks = esc(b["sumber_teks"])
    if b.get("sumber_pautan"):
        teks = '<a href="%s" target="_blank" rel="noopener">%s</a>' % (esc(b["sumber_pautan"]), teks)
    return '<p class="sumber-berita">Sumber: %s</p>' % teks


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def parse_date(s):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def tarikh_pjg(d):
    if not d:
        return ""
    return "%s, %d %s %d" % (HARI[d.weekday()], d.day, BULAN[d.month - 1], d.year)


def tarikh_pdk(d):
    if not d:
        return ""
    return "%d %s %d" % (d.day, BULAN[d.month - 1], d.year)


def muat_ikon():
    cache = {}

    def get(name):
        if name in cache:
            return cache[name]
        p = ICON_DIR / (name + ".svg")
        if not p.exists():
            cache[name] = '<span class="ikon-ganti" aria-hidden="true"></span>'
            return cache[name]
        raw = p.read_text(encoding="utf-8")
        raw = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
        inner = re.search(r"(?s)<svg[^>]*>(.*?)</svg>", raw)
        body = inner.group(1).strip() if inner else ""
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" '
               'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
               'stroke-linejoin="round" class="lucide lucide-%s" aria-hidden="true">%s</svg>' % (name, body))
        cache[name] = svg
        return svg

    return get


icon = muat_ikon()

SITE = load("site.json")
BASE = SITE.get("base_url", "").rstrip("/")
PAGES = []          # untuk sitemap
HALAMAN_BM = []     # (laluan, html) — sumber tunggal untuk penjanaan versi Inggeris
KURANG = []         # kandungan yang belum disediakan (untuk --report)


def kurang(item):
    KURANG.append(item)


# ----------------------------------------------------------------- cangkerang
NAV = [
    ("Utama", "/", "utama"),
    ("Mengenai", "/tentang/", "tentang"),
    ("Organisasi", "/organisasi/", "organisasi"),
    ("Pendidikan & Latihan", "/pendidikan/", "pendidikan"),
    ("Keahlian", "/keahlian/", "keahlian"),
    ("Aktiviti", "/aktiviti/", "aktiviti"),
    ("Sumber", "/sumber/", "sumber"),
    ("Berita", "/berita/", "berita"),
    ("Galeri", "/galeri/", "galeri"),
    ("Hubungi", "/hubungi/", "hubungi"),
]


def head(tajuk, deskripsi, laluan, og_jenis="website", jsonld=None, noindex=False, gambar_og=None):
    # Kad kongsi sosial lalai: kad jenama 1200x630 (logo + logotaip). Halaman item (berita,
    # aktiviti, kursus, galeri) menghantar gambar sendiri supaya pratonton pautan kekal relevan.
    og_imej = ("/" + gambar_og.lstrip("/")) if gambar_og else GAMBAR_OG_LALAI
    kanon = BASE + laluan
    sekatan = []
    sekatan.append('<meta charset="utf-8">')
    sekatan.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    sekatan.append("<title>%s</title>" % esc(tajuk))
    sekatan.append('<meta name="description" content="%s">' % esc(deskripsi))
    sekatan.append('<link rel="canonical" href="%s">' % esc(kanon))
    sekatan.append("<!--HREFLANG-->")
    sekatan.append('<meta name="theme-color" content="#510716">')
    if noindex:
        sekatan.append('<meta name="robots" content="noindex, follow">')
    sekatan.append('<link rel="icon" href="/assets/favicon-64.png" sizes="64x64">')
    sekatan.append('<link rel="apple-touch-icon" href="/assets/apple-touch-180.png">')
    sekatan.append('<link rel="stylesheet" href="/styles.css">')
    sekatan.append('<meta property="og:type" content="%s">' % og_jenis)
    sekatan.append('<meta property="og:site_name" content="MADOCS">')
    sekatan.append('<meta property="og:locale" content="ms_MY">')
    sekatan.append('<meta property="og:title" content="%s">' % esc(tajuk))
    sekatan.append('<meta property="og:description" content="%s">' % esc(deskripsi))
    sekatan.append('<meta property="og:url" content="%s">' % esc(kanon))
    sekatan.append('<meta property="og:image" content="%s%s">' % (esc(BASE), esc(og_imej)))
    # Saiz/jenis hanya diisytiharkan untuk kad jenama; gambar item ada saiznya sendiri dan
    # pengikis (WhatsApp/Telegram) akan membaca fail sebenar.
    if gambar_og:
        jenis = "image/webp" if og_imej.lower().endswith(".webp") else (
            "image/jpeg" if og_imej.lower().endswith((".jpg", ".jpeg")) else "image/png")
        sekatan.append('<meta property="og:image:type" content="%s">' % jenis)
    else:
        sekatan.append('<meta property="og:image:width" content="%d">' % OG_SAIZ[0])
        sekatan.append('<meta property="og:image:height" content="%d">' % OG_SAIZ[1])
        sekatan.append('<meta property="og:image:type" content="image/png">')
    sekatan.append('<meta property="og:image:alt" content="%s">' % esc("MADOCS — Pertubuhan Doktor Khatan Malaysia"))
    sekatan.append('<meta name="twitter:card" content="summary_large_image">')
    sekatan.append('<meta name="twitter:image" content="%s%s">' % (esc(BASE), esc(og_imej)))
    data = [organisasi_ld()]
    if jsonld:
        data.extend(jsonld if isinstance(jsonld, list) else [jsonld])
    for d in data:
        sekatan.append('<script type="application/ld+json">%s</script>'
                       % json.dumps(d, ensure_ascii=False, separators=(",", ":")))
    return "\n".join(sekatan)


def organisasi_ld():
    o = {
        "@context": "https://schema.org",
        "@type": "NGO",
        "name": SITE["nama"],
        "alternateName": SITE["singkatan"],
        "url": BASE + "/",
        "email": SITE["email"],
        "telephone": SITE["telefon"],
        "foundingDate": SITE["ditubuhkan"],
        "identifier": SITE["pendaftaran"],
        "areaServed": "MY",
        "logo": BASE + "/assets/logo-128.webp",
        "address": {"@type": "PostalAddress", "addressCountry": "MY"},
    }
    return o


def topbar():
    sos = SITE.get("sosial") or {}
    sosial = "".join('<a href="%s" rel="noopener" aria-label="%s">%s</a>'
                     % (esc(v), esc(k.capitalize()), esc(k[0].upper()))
                     for k, v in sos.items() if v)
    if not sosial:
        sosial = '<a href="mailto:%s" aria-label="E-mel MADOCS">%s</a>' % (esc(SITE["email"]), icon("mail"))
    return f"""<div class="topbar">
  <div class="shell topbar-inner">
    <span>{icon('shield-check')} {esc(SITE['pendaftaran'])}</span>
    <div>
      <a href="{wa_pautan(MESEJ_WA_UMUM)}" target="_blank" rel="noopener">{icon('message-circle')} WhatsApp</a>
      <i></i>
      <a href="mailto:{esc(SITE['email'])}">{icon('mail')} {esc(SITE['email'])}</a>
      <i></i>
      <a href="tel:{esc(SITE['telefon'])}">{icon('phone')} {esc(SITE['telefon_papar'])}</a>
    </div>
  </div>
</div>"""


# Navigasi berkumpulan (5 kumpulan): (label, href, kunci, [(label, href, kunci), ...])
NAV_KUMPULAN = [
    ("Mengenai", "/tentang/", "tentang", [
        ("Mengenai MADOCS", "/tentang/", "tentang"),
        ("Organisasi & Jawatankuasa", "/organisasi/", "organisasi"),
        ("Perutusan Presiden", "/dari-meja-presiden/", "presiden"),
    ]),
    ("Pendidikan", "/pendidikan/", "pendidikan", [
        ("Kursus & Latihan", "/pendidikan/", "pendidikan"),
        ("Credentialing & Privileging (C&P)", "/cp/", "cp"),
        ("Pusat Sumber", "/sumber/", "sumber"),
    ]),
    ("Keahlian", "/keahlian/", "keahlian", [
        ("Keahlian & Yuran", "/keahlian/", "keahlian"),
        ("Semak Status Ahli", "/semak-ahli/", "ahli"),
        ("Sahkan Sijil", "/sahkan/", "sahkan"),
    ]),
    ("Media", "/berita/", "berita", [
        ("Berita", "/berita/", "berita"),
        ("Aktiviti", "/aktiviti/", "aktiviti"),
        ("Galeri", "/galeri/", "galeri"),
    ]),
    ("Hubungi", "/hubungi/", "hubungi", []),
]


def header(aktif):
    """Navigasi desktop: 4 kumpulan berdropdown + 2 pautan terus."""
    blok = []
    for label, href, kunci, anak in NAV_KUMPULAN:
        aktif_kumpulan = kunci == aktif or any(a[2] == aktif for a in anak)
        if not anak:
            blok.append('<a class="%s" href="%s"%s>%s</a>'
                        % ("active" if aktif_kumpulan else "", href,
                           ' aria-current="page"' if aktif_kumpulan else "", esc(label)))
            continue
        sub = "".join('<a href="%s"%s>%s</a>'
                      % (h, ' aria-current="page"' if k == aktif else "", esc(l))
                      for l, h, k in anak)
        blok.append(
            '<div class="nav-kumpulan%s">'
            '<a class="nav-induk" href="%s" aria-haspopup="true">%s%s</a>'
            '<div class="sub-nav"><div class="sub-nav-dalaman">%s</div></div>'
            '</div>'
            % (" aktif" if aktif_kumpulan else "", href, esc(label), icon("chevron-down"), sub))
    pautan = "".join(blok)

    blok_mudah = []
    for label, href, kunci, anak in NAV_KUMPULAN:
        if not anak:
            blok_mudah.append('<a href="%s">%s</a>' % (href, esc(label)))
            continue
        sub = "".join('<a href="%s">%s</a>' % (h, esc(l)) for l, h, k in anak)
        blok_mudah.append('<details class="mudah-kumpulan"><summary>%s%s</summary>'
                          '<div class="mudah-sub">%s</div></details>'
                          % (esc(label), icon("chevron-down"), sub))
    mudah = "".join(blok_mudah)
    return f"""<header class="header">
  <div class="shell nav-row">
    <a href="/" class="logo" aria-label="Laman utama MADOCS">
      <img src="/assets/logo-192.webp" alt="Lambang MADOCS" width="110" height="110">
      <span>
        <strong>MADOCS</strong>
        <small>Pertubuhan Doktor Khatan Malaysia</small>
      </span>
    </a>
    <nav class="desktop-nav" aria-label="Navigasi utama">{pautan}</nav>
    <a class="join-nav" href="/keahlian/sertai/" style="text-decoration:none">Sertai MADOCS</a>
    <!--TUKAR-BAHASA-->
    <button class="menu-toggle" aria-label="Buka atau tutup menu" aria-expanded="false">{icon('menu')}</button>
  </div>
  <nav class="mobile-nav" id="menu-mudah" aria-label="Navigasi mudah alih" hidden>
    {mudah}
    <a class="btn btn-primary" href="/keahlian/sertai/" style="justify-content:center">Sertai MADOCS</a>
  </nav>
</header>"""


def footer():
    pintasan = "".join('<a href="%s">%s</a>' % (href, esc(label)) for label, href, kunci in NAV[:6])
    return f"""<footer>
  <div class="shell footer-grid">
    <div>
      <h3>Mengenai MADOCS</h3>
      <p>{esc(SITE['nama'])} ({esc(SITE['singkatan'])}) ialah pertubuhan profesional yang meningkatkan standard amalan berkhatan selamat melalui pendidikan, latihan, advokasi dan kerjasama profesional.</p>
      <div class="socials">
        <a href="mailto:{esc(SITE['email'])}" aria-label="E-mel">{icon('mail')}</a>
        <a href="tel:{esc(SITE['telefon'])}" aria-label="Telefon">{icon('phone')}</a>
        <a href="{wa_pautan(MESEJ_WA_UMUM)}" target="_blank" rel="noopener" aria-label="WhatsApp urusetia">{icon('message-circle')}</a>
        <a href="/hubungi/" aria-label="Hubungi kami">{icon('globe')}</a>
      </div>
    </div>
    <div>
      <h3>Pintasan</h3>
      {pintasan}
    </div>
    <div>
      <h3>Hubungi kami</h3>
      <p>{esc(SITE['nama'])}<br>No. Pendaftaran : {esc(SITE['pendaftaran'])}</p>
      <a href="mailto:{esc(SITE['email'])}">{icon('mail')} {esc(SITE['email'])}</a>
      <a href="tel:{esc(SITE['telefon'])}">{icon('phone')} {esc(SITE['telefon_papar'])}</a>
      <span>{icon('map-pin')} {esc(SITE['alamat'])}</span>
    </div>
    <div>
      <h3>Langgan berita</h3>
      <p>Hantar e-mel kepada urusetia untuk menerima kemas kini kursus, aktiviti dan berita MADOCS.</p>
      <form action="mailto:{esc(SITE['email'])}" method="get" enctype="text/plain">
        <label>{icon('mail')}<input type="email" name="email" placeholder="Alamat e-mel anda" aria-label="Alamat e-mel" required></label>
        <button type="submit">Langgan</button>
      </form>
    </div>
  </div>
  <div class="shell footer-bottom">
    <span>© {date.today().year} {esc(SITE['nama'])}. Hak cipta terpelihara.</span>
    <span><a href="/semak-ahli/">Pengesahan Ahli</a><i></i><a href="/dasar-privasi/">Dasar Privasi</a><i></i><a href="/terma/">Terma Penggunaan</a><i></i><a href="/kebolehaksesan/">Aksesibiliti</a></span>
  </div>
</footer>"""


def halaman(aktif, tajuk, deskripsi, laluan, isi, og_jenis="website", jsonld=None, masuk_sitemap=True,
            noindex=False, gambar_og=None):
    # Halaman urusan ahli: semua pautan WhatsApp (termasuk topbar dan butang terapung)
    # menghala kepada setiausaha keahlian (Madihah), bukan nombor am persatuan.
    global _WA_KONTEKS
    _WA_KONTEKS = "ahli" if any(k in (laluan or "") for k in LALUAN_AHLI) else None
    dokumen = f"""<!DOCTYPE html>
<html lang="ms">
<head>
{head(tajuk, deskripsi, laluan, og_jenis, jsonld, noindex, gambar_og)}
</head>
<body class="hlm-{esc(aktif or 'umum')}">
<a class="skip-link" href="#kandungan">Lompat ke kandungan utama</a>
{topbar()}
{header(aktif)}
<main id="kandungan">
{isi}
</main>
{footer()}
<script src="/app.js" defer></script>
</body>
</html>
"""
    tulis(laluan, dokumen, masuk_sitemap)


def tulis(laluan, kandungan, masuk_sitemap=True):
    """laluan contohnya '/tentang/' atau '/404.html'."""
    _tulis_fail(laluan, kandungan)
    HALAMAN_BM.append((laluan, kandungan))
    if masuk_sitemap:
        PAGES.append(laluan)


DIJANA = set()      # laluan fail HTML yang dijana dalam larian ini (untuk bersihkan halaman sisa)


def _tulis_fail(laluan, kandungan):
    if laluan.endswith("/"):
        fail = ROOT / (laluan.strip("/") or "") / "index.html" if laluan != "/" else ROOT / "index.html"
    else:
        fail = ROOT / laluan.strip("/")
    fail.parent.mkdir(parents=True, exist_ok=True)
    fail.write_text(kandungan, encoding="utf-8")
    DIJANA.add(fail.resolve())


# ----------------------------------------------------------------- dwi-bahasa
def _potong_kata(teks: str, had: int) -> str:
    """Potong pada sempadan perkataan supaya tidak terpotong di tengah perkataan."""
    if len(teks) <= had:
        return teks
    potong = teks[:had].rsplit(" ", 1)[0].rstrip(" ,;:·-")
    return potong or teks[:had]


def ketat_meta(html: str, had_tajuk: int = 70, had_desc: int = 160) -> str:
    """Hadkan <title> dan meta description versi Inggeris.

    Terjemahan menjadikan ayat lebih panjang daripada Bahasa Melayu, jadi tajuk yang sah
    dalam BM boleh melebihi 70 aksara dalam EN. Fungsi ini memendekkan pada sempadan
    perkataan dan mengekalkan akhiran jenama ("| MADOCS Gallery" dan seumpamanya).
    """
    def _tajuk(m):
        t = m.group(1)
        if len(t) <= had_tajuk:
            return m.group(0)
        if " | " in t:
            asas, akhiran = t.split(" | ", 1)
            ruang = had_tajuk - len(akhiran) - 6  # " | " + "…"
            if ruang >= 18:
                return "<title>%s… | %s</title>" % (_potong_kata(asas, ruang), akhiran)
        return "<title>%s…</title>" % _potong_kata(t, had_tajuk - 1)

    def _desc(m):
        d = m.group(2)
        if len(d) <= had_desc:
            return m.group(0)
        return '%s%s"' % (m.group(1), _potong_kata(d, had_desc - 1) + "…")

    html = re.sub(r"<title>(.*?)</title>", _tajuk, html, count=1)
    html = re.sub(r'(<meta name="description" content=")(.*?)"', _desc, html, count=1)
    return html


def bina_bahasa_inggeris():
    """Suntik pautan tukar bahasa + hreflang pada halaman BM, dan jana versi Inggeris di /en/.

    Sumber kandungan tunggal = Bahasa Melayu. Versi EN ialah terjemahan HTML yang sama,
    menggunakan kamus data/terjemahan.json (lihat terjemah.py).
    """
    peta = terjemah.peta_slug([l for l, _ in HALAMAN_BM])
    kamus = terjemah.muat_kamus()
    belum = 0
    for laluan, html in HALAMAN_BM:
        if laluan == "/404.html":
            _tulis_fail(laluan, html.replace(terjemah.PENANDA_BAHASA, "")
                         .replace(terjemah.PENANDA_HREFLANG, ""))
            continue
        # halaman BM: tambah pautan EN + hreflang
        _tulis_fail(laluan, terjemah.suntik_navigasi_bahasa(html, peta, laluan, BASE))
        # halaman EN
        en = peta.get(laluan)
        if not en:
            continue
        html_en = terjemah.terjemah_html(html, kamus, peta, laluan, en, BASE)
        html_en = terjemah.suntik_navigasi_bahasa(html_en, peta, en, BASE)
        html_en = ketat_meta(html_en)
        _tulis_fail(en, html_en)
        PAGES.append(en)
        for t in terjemah.teks_dalam_html(html):
            if t not in kamus:
                belum += 1

    # indeks carian versi Inggeris (pautan + teks diterjemah)
    indeks_bm = ROOT / "carian" / "index.json"
    if indeks_bm.exists():
        try:
            data = json.loads(indeks_bm.read_text(encoding="utf-8"))
        except Exception:
            data = []
        en_data = []
        for it in data:
            baharu = dict(it)
            baharu["t"] = kamus.get(it.get("t", ""), it.get("t", ""))
            baharu["r"] = kamus.get(it.get("r", ""), it.get("r", ""))
            baharu["j"] = kamus.get(it.get("j", ""), it.get("j", ""))
            if it.get("u") in peta:
                baharu["u"] = peta[it["u"]]
            en_data.append(baharu)
        (ROOT / "en" / "search").mkdir(parents=True, exist_ok=True)
        (ROOT / "en" / "search" / "index.json").write_text(
            json.dumps(en_data, ensure_ascii=False, indent=0), encoding="utf-8")

    if belum:
        print("Nota: %d cebisan teks belum diterjemah (kekal BM) — lihat terjemah.py --laporan." % belum)
    print("Bahasa Inggeris: %d halaman dijana di /en/." % (len(PAGES) - len(HALAMAN_BM)))


# ----------------------------------------------------------------- komponen
def crumbs(items):
    bahagian = []
    for i, (label, href) in enumerate(items):
        if i:
            bahagian.append(icon("chevron-right"))
        bahagian.append('<a href="%s">%s</a>' % (href, esc(label)) if href else "<span>%s</span>" % esc(label))
    return '<nav class="crumbs" aria-label="Jejak navigasi">%s</nav>' % "".join(bahagian)


def page_hero(jejak, tajuk, huraian="", butang="", kicker=""):
    k = '<p class="hero-kicker">%s</p>' % esc(kicker) if kicker else ""
    return f"""<section class="page-hero">
  <div class="shell">
    {crumbs(jejak)}
    {k}
    <h1>{esc(tajuk)}</h1>
    {f'<p>{esc(huraian)}</p>' if huraian else ''}
    {butang}
  </div>
</section>"""


def badge_status(status):
    label, kelas = STATUS_LABEL.get(status, (status, ""))
    return '<span class="badge %s">%s</span>' % (kelas, esc(label))


def kad_kursus(k, keutamaan=False):
    d = parse_date(k.get("tarikh"))
    badge = ""
    if d:
        badge = ('<span class="date-badge"><b>%d</b> %s<small>%d</small></span>'
                 % (d.day, BULAN_SING[d.month - 1], d.year))
    fakta = []
    if d:
        fakta.append(f"<li>{icon('calendar-days')}{esc(tarikh_pjg(d))}</li>")
    if k.get("tempat"):
        fakta.append(f"<li>{icon('map-pin')}{esc(k['tempat'])}</li>")
    if k.get("sasaran"):
        fakta.append(f"<li>{icon('users')}{esc(k['sasaran'])}</li>")
    if k.get("kapasiti"):
        fakta.append(f"<li>{icon('list-checks')}Kapasiti {esc(k['kapasiti'])}"
                     + (f" · {esc(k['baki'])} tempat berbaki" if k.get("baki") else "") + "</li>")
    if k.get("masa_mula"):
        fakta.append(f"<li>{icon('clock')}{esc(k['masa_mula'])}-{esc(k.get('masa_tamat',''))}</li>")
    tag = "".join("<span>%s</span>" % esc(t) for t in (k.get("tag") or []))
    img = k.get("gambar") or gambar_hero_utama()
    alt = k.get("gambar_alt") or k.get("tajuk", "")
    chip = chip_ilustrasi(alt)
    return f"""<article class="course-feature">
  <div class="course-photo">
    <img src="/{esc(img)}" alt="{esc(alt)}" loading="{'eager' if keutamaan else 'lazy'}" decoding="async">
    {badge}
    {chip}
    {f'<span class="chip-kredit">{esc(k["gambar_kredit"])}</span>' if k.get("gambar_kredit") else ''}
  </div>
  <div class="course-info">
    <span class="course-code">{esc(k.get('kod',''))}</span>
    <h3>{esc(k['tajuk'])}</h3>
    <ul>{''.join(fakta)}</ul>
    {f'<div class="tags">{tag}</div>' if tag else ''}
    <div class="course-actions">
      <a class="small-btn filled" href="/pendidikan/{esc(k['slug'])}/" style="display:inline-flex;align-items:center;text-decoration:none">Lihat kursus</a>
      {'<a class="small-btn" href="%s" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;text-decoration:none">Daftar</a>' % esc(k['daftar_url']) if k.get('daftar_url') else '<a class="small-btn" href="/hubungi/" style="display:inline-flex;align-items:center;text-decoration:none">Daftar</a>'}
    </div>
  </div>
</article>"""


def chip_ilustrasi(alt=""):
    """Label 'Imej ilustrasi' — hanya apabila teks alt menyatakan imej itu ilustrasi.

    Gambar sebenar MADOCS (alt menerangkan peristiwa) tidak dilabel; imej ilustrasi lama
    (alt bermula 'Imej ilustrasi') dilabel. Kawalan induk: data/site.json → gambar_ilustrasi.
    """
    if not SITE.get("gambar_ilustrasi"):
        return ""
    if str(alt or "").strip().lower().startswith("imej ilustrasi"):
        return '<span class="chip-illustrasi">Imej ilustrasi</span>'
    return ""


def kad_aktiviti(a):
    d = parse_date(a.get("tarikh"))
    kelas = "teal" if (a.get("kategori") or "").upper() in ("TTT", "PCC") else ""
    # Aktiviti tanpa gambar sebenar: jangan pinjam gambar peristiwa lain, paparkan blok
    # kategori yang bersih supaya kad kekal sekata dan tidak mengelirukan.
    if a.get("gambar"):
        gambar_html = ('<img src="/%s" alt="%s" loading="lazy" decoding="async">'
                       % (esc(a["gambar"]), esc(a.get("gambar_alt") or a["tajuk"])))
    else:
        gambar_html = '<span class="ikon-tiada">%s</span>' % icon("calendar-days")
    return f"""<article class="activity-card">
  <div class="activity-image{" tiada-gambar" if not a.get("gambar") else ""}">
    {gambar_html}
    <span class="{kelas}">{esc(a.get('kategori',''))}</span>
    {chip_ilustrasi(a.get('gambar_alt'))}
  </div>
  <div class="activity-info">
    <h3>{esc(a['tajuk'])}</h3>
    <p>{icon('calendar-days')}{esc(tarikh_pdk(d))}</p>
    <p>{icon('map-pin')}{esc(a.get('tempat',''))}</p>
    <a href="/aktiviti/{esc(a['slug'])}/">Baca lanjut {icon('arrow-right')}</a>
  </div>
</article>"""


def tajuk_meta(teks, akhiran=" | MADOCS", had=70):
    """Tajuk <title> yang tidak melebihi `had` aksara (Google memotong selepas ~60-70)."""
    t = re.sub(r"\s+", " ", str(teks or "")).strip()
    ruang = had - len(akhiran)
    if len(t) <= ruang:
        return t + akhiran
    potong = t[:ruang].rsplit(" ", 1)[0].rstrip(" ,.;:—-")
    return potong + "…" + akhiran


def ringkas_meta(teks, had=158):
    """Potong teks pada sempadan perkataan untuk meta description (<= `had` aksara)."""
    t = re.sub(r"\s+", " ", str(teks or "")).strip()
    if len(t) <= had:
        return t
    potong = t[:had].rsplit(" ", 1)[0]
    return potong.rstrip(" ,.;:") + "…"


def item_kandungan(tajuk, url, ringkas, tarikh=None, kategori="", gambar=None, alt="", meta_ikon="calendar-days", kredit=None, tarikh_papar=None, label="Baca lanjut"):
    """Kad senarai untuk berita / aktiviti / sumber."""
    foto = ('<div class="item-photo"><img src="/%s" alt="%s" loading="lazy" decoding="async">%s%s</div>'
            % (esc(gambar), esc(alt or tajuk), chip_ilustrasi(alt),
               '<span class="chip-kredit">%s</span>' % esc(kredit) if kredit else "")) if gambar else ""
    kelas = "" if gambar else " no-photo"
    badge = '<span class="badge">%s</span>' % esc(kategori) if kategori else ""
    masa = ('<p class="item-meta">%s %s</p>' % (icon(meta_ikon), esc(tarikh_papar))) if tarikh_papar else (
        ('<time datetime="%s">%s %s</time>' % (esc(tarikh), icon(meta_ikon), esc(tarikh_pdk(parse_date(tarikh))))) if tarikh else "")
    return f"""<article class="item{kelas}">
  {foto}
  <div class="item-body">
    {badge}
    <h3><a href="{esc(url)}">{esc(tajuk)}</a></h3>
    <div class="item-meta">{masa}</div>
    {f'<p>{esc(ringkas)}</p>' if ringkas else ''}
    <a class="lebih" href="{esc(url)}">{esc(label)} {icon('arrow-right')}</a>
  </div>
</article>"""


def kosong(ikon_nama, tajuk, mesej, butang=""):
    return f"""<div class="kosong">
  <span class="ikon">{icon(ikon_nama)}</span>
  <h3>{esc(tajuk)}</h3>
  <p>{esc(mesej)}</p>
  {butang}
</div>"""


def cta_komuniti(tajuk="Sertai komuniti profesional MADOCS",
                 mesej="Bersama-sama kita memartabatkan amalan khatan yang selamat, profesional dan beretika di Malaysia.",
                 label="Sertai MADOCS sekarang", href="/keahlian/sertai/"):
    return f"""<section class="community-cta">
  <div class="shell cta-grid">
    <span class="cta-icon">{icon('users')}</span>
    <div>
      <h2>{esc(tajuk)}</h2>
      <p>{esc(mesej)}</p>
    </div>
    <a class="cta-btn" href="{href}">{esc(label)} {icon('arrow-right')}</a>
  </div>
</section>"""


def bina_sahkan():
    """Halaman pengesahan sijil C&P, rekod awam TANPA data peribadi.

    Rekod (data/sijil.json, dijana oleh madocs-admin/jana-sijil.py) hanya mengandungi
    nombor siri, kursus, tarikh, mata CPD dan hash PDF. Nama dan nombor MMC pemegang
    TIDAK disimpan di sini, jadi hospital boleh mengesahkan keaslian sijil tanpa
    mendedahkan maklumat peribadi kepada awam (PRD §47).
    """
    data = load("sijil.json") if (DATA / "sijil.json").exists() else {"sijil": []}
    indeks_json = json.dumps({"sijil": data.get("sijil", [])}, ensure_ascii=False).replace("</", "<\\/")
    # Pengesahan sijil juga urusan ahli → urusetia keahlian (Madihah).
    wa = "https://wa.me/%s" % wa_keahlian_nombor()
    isi = f"""<section class="page-hero">
  <div class="shell">{crumbs([("Utama", "/"), ("Pengesahan Sijil", None)])}
    <h1>Pengesahan Sijil C&amp;P</h1>
    <p>Hospital dan pihak berkuasa boleh mengesahkan sijil Credentialing &amp; Privileging (C&amp;P) MADOCS di sini, tanpa perlu memaklumkan data peribadi pemegang sijil.</p>
  </div>
</section>
<section class="content-wrap"><div class="shell"><div class="card prose">
  <p class="banner-draf">{icon('info')} <b>Rekod sijil sedang diselaraskan dengan urusetia.</b> Untuk pengesahan rasmi bertulis, sila hubungi urusetia MADOCS.</p>
  <form id="borang-sahkan" class="borang-sahkan" autocomplete="off" novalidate>
    <label for="siri">Nombor siri sijil</label>
    <p class="nota-isi">Nombor siri tercetak di bahagian bawah sijil, di sebelah kod QR. Contoh: <b>MADOCS-CP-2026-0001</b>.</p>
    <div class="baris-sahkan">
      <input id="siri" name="siri" type="text" placeholder="MADOCS-CP-2026-0001" required>
      <button class="btn btn-primary" type="submit">{icon('search')} Sahkan sijil</button>
    </div>
  </form>
  <div id="hasil-sahkan" class="hasil-sahkan" role="status" aria-live="polite"></div>

  <h2>Bagaimana pengesahan berfungsi</h2>
  <ul>
    <li>Setiap sijil MADOCS mempunyai <b>nombor siri unik</b> dan <b>kod QR</b> yang membuka halaman ini dengan nombor itu.</li>
    <li>Untuk mengesahkan, masukkan nombor siri, sistem memaparkan kursus, tarikh, mata CPD dan <b>hash SHA-256</b> fail sijil.</li>
    <li>Sijil hanya sah jika nombor siri wujud dalam rekod, dan hash yang dipaparkan sepadan dengan fail sijil asal.</li>
  </ul>

  <h2>Privasi</h2>
  <p>Rekod awam ini <b>tidak menyimpan nama atau nombor MMC</b> pemegang sijil. Nama pada sijil adalah pada dokumen pemegang sendiri, dan pengesahan di sini tidak mendedahkan maklumat peribadi kepada pihak ketiga. Pertanyaan tentang pengesahan boleh diajukan kepada urusetia.</p>

  <h2>Jika sijil tidak dijumpai</h2>
  <p>Sila semak semula nombor siri pada sijil. Jika masih tidak dijumpai, hubungi urusetia MADOCS: <a href="mailto:{esc(load('site.json').get('email',''))}">{esc(load('site.json').get('email',''))}</a> atau <a href="{esc(wa)}" target="_blank" rel="noopener">WhatsApp urusetia</a>.</p>

  <script type="application/json" id="indeks-sijil">{indeks_json}</script>
</div></div></section>"""
    halaman("", "Pengesahan Sijil C&P | MADOCS",
            "Sahkan keaslian sijil Credentialing & Privileging (C&P) MADOCS dengan nombor siri sijil.",
            "/sahkan/", isi, masuk_sitemap=False, noindex=True)


def bina_semak_ahli():
    """Halaman pengesahan status keahlian, rekod awam tanpa data peribadi.

    Rekod (data/ahli.json) hanya menyimpan nombor ahli, nama bertopeng, kategori,
    status dan tarikh sah. Tiada kad pengenalan, tiada nombor MMC.
    """
    data = load("ahli.json") if (DATA / "ahli.json").exists() else {"ahli": []}
    ahli = data.get("ahli", [])
    indeks_json = json.dumps({"ahli": ahli}, ensure_ascii=False).replace("</", "<\\/")
    # Semua urusan ahli → urusetia keahlian (Madihah), bukan nombor am persatuan.
    wa = "https://wa.me/%s" % wa_keahlian_nombor()
    contoh = bool(data.get("contoh"))
    banner = ('<p class="banner-draf">%s <b>Data contoh untuk semakan jawatankuasa.</b> Rekod sebenar belum '
              'dimasukkan; status di bawah tidak boleh dijadikan bukti keahlian.</p>' % icon("info")) if contoh else ""
    isi = f"""<section class="page-hero">
  <div class="shell">{crumbs([("Utama", "/"), ("Pengesahan Ahli", None)])}
    <h1>Pengesahan Status Ahli</h1>
    <p>Klinik, hospital dan pihak berkuasa boleh menyemak sama ada seorang doktor ialah ahli MADOCS yang aktif.</p>
  </div>
</section>
<section class="content-wrap"><div class="shell"><div class="card prose">
  {banner}
  <form id="borang-ahli" class="borang-sahkan" autocomplete="off" novalidate>
    <label for="no-ahli">Nombor ahli</label>
    <p class="nota-isi">Nombor ahli tercetak pada sijil keahlian dan e-mel pengesahan pendaftaran. Nombor bermula dengan kod negeri, contohnya <b>JDT1</b> (Johor), <b>SDE53</b> (Selangor), <b>WKL12</b> (Kuala Lumpur).</p>
    <div class="baris-sahkan">
      <input id="no-ahli" name="no-ahli" type="text" placeholder="cth. SDE53" autocomplete="off" spellcheck="false" required>
      <button class="btn btn-primary" type="submit">{icon('search')} Semak status</button>
    </div>
  </form>
  <div id="hasil-ahli" class="hasil-sahkan" role="status" aria-live="polite"></div>

  <h2>Apa yang dipaparkan</h2>
  <ul>
    <li><b>Status keahlian</b>: aktif, tamat tempoh, atau ditangguh.</li>
    <li><b>Kategori</b>: Ahli Biasa, Bersekutu, Pelajar atau Seumur Hidup.</li>
    <li><b>Tarikh sah</b>: untuk keahlian tahunan; keahlian seumur hidup tiada tarikh luput.</li>
    <li><b>Nama bertopeng</b>: cukup untuk memadankan dengan nama pada kad pengenalan doktor, tanpa mendedahkan nama penuh.</li>
  </ul>

  <h2>Privasi</h2>
  <p>Rekod awam ini <b>tidak menyimpan kad pengenalan atau nombor MMC</b>. Pertanyaan lanjut boleh diajukan kepada urusetia MADOCS.</p>

  <h2>Jika nombor tidak dijumpai</h2>
  <p>Sila semak semula nombor pada sijil keahlian. Jika masih tidak dijumpai, hubungi urusetia: <a href="mailto:{esc(load('site.json').get('email',''))}">{esc(load('site.json').get('email',''))}</a> atau <a href="{esc(wa)}" target="_blank" rel="noopener">WhatsApp urusetia</a>.</p>

  <script type="application/json" id="indeks-ahli">{indeks_json}</script>
</div></div></section>"""
    halaman("", "Pengesahan Ahli | MADOCS",
            "Semak status keahlian MADOCS dengan nombor ahli tanpa mendedahkan data peribadi.",
            "/semak-ahli/", isi, masuk_sitemap=False, noindex=True)


def laman_ringkas(slug, tajuk, isi_html, deskripsi=None):
    """Halaman teks ringkas (dasar privasi, terma)."""
    dalam = f"""<section class="page-hero">
  <div class="shell">{crumbs([("Utama", "/")])}<h1>{esc(tajuk)}</h1></div>
</section>
<section class="content-wrap"><div class="shell"><div class="card prose">{isi_html}</div></div></section>"""
    ket = deskripsi or ("%s Pertubuhan Doktor Khatan Malaysia (MADOCS): persatuan profesional doktor "
                        "yang terlibat dalam amalan berkhatan di Malaysia." % tajuk)
    halaman("", tajuk + " | MADOCS", ringkas_meta(ket, 160), "/%s/" % slug, dalam)


# ----------------------------------------------------------------- halaman: utama
def gambar_hero_utama():
    """Laluan imej hero pertama (untuk og:image dan gambar lalai kad kursus)."""
    sl = (load("hero.json").get("slaid") or [])
    return ("/" + sl[0]["besar"]) if sl else "/assets/logo.png"


def blok_hero_slaid():
    """Slaid hero (roulette) daripada data/hero.json.

    Dua jenis slaid:
      - "imej"   : gambar penuh (slaid biasa)
      - "berita" : gambar + teks di bawah + pautan ke halaman berita; seluruh slaid
                   boleh ditekan supaya pembaca terus sampai ke berita.

    Slaid pertama dimuatkan segera (LCP); slaid lain memakai data-src + data-srcset
    supaya app.js memuatkannya selepas halaman sedia. Tanpa JS, hanya slaid pertama
    kelihatan (ada kelas 'aktif' dalam HTML) — kandungan kekal boleh dilihat.
    """
    h = load("hero.json")
    slaid = h.get("slaid") or []
    keluar = []
    for i, sl in enumerate(slaid):
        aktif = " aktif" if i == 0 else ""
        if i == 0:
            sumber = '<source media="(max-width: 640px)" srcset="/%s">' % esc(sl["telefon"])
            imej = ('<img src="/%s" alt="%s" width="1400" height="1015" class="hero-image" '
                    'fetchpriority="high" decoding="async">' % (esc(sl["besar"]), esc(sl["alt"])))
        else:
            sumber = '<source media="(max-width: 640px)" data-srcset="/%s">' % esc(sl["telefon"])
            imej = ('<img alt="%s" width="1400" height="1015" class="hero-image" decoding="async" '
                    'data-src="/%s">' % (esc(sl["alt"]), esc(sl["besar"])))

        gambar = "<picture>%s%s</picture>" % (sumber, imej)

        if sl.get("jenis") == "berita" and sl.get("pautan"):
            teks = ('<span class="hero-berita-teks">'
                    '<small>%s</small><b>%s</b>'
                    '<i>Baca berita %s</i></span>'
                    % (esc(sl.get("kicker") or "Berita"), esc(sl.get("tajuk") or ""), icon("arrow-right")))
            keluar.append('<a class="hero-slaid hero-slaid-berita%s" href="%s" '
                          'aria-label="%s">%s%s</a>'
                          % (aktif, esc(sl["pautan"]), esc(sl.get("tajuk") or "Berita MADOCS"),
                             gambar, teks))
        else:
            keluar.append('<picture class="hero-slaid%s">%s%s</picture>' % (aktif, sumber, imej))
    return "\n  ".join(keluar)



def bina_utama():
    stats = load("stats.json")
    kursus = load("kursus.json")["kursus"]
    aktiviti = load("aktiviti.json")["aktiviti"]
    sumber = load("sumber.json")["sumber"]
    berita = load("berita.json")["berita"]
    keahlian = load("keahlian.json")
    hari_ini = date.today()

    akan_datang = sorted([k for k in kursus
                          if k.get("status") in ("open", "limited", "tentatif")
                          and (parse_date(k.get("tarikh")) or hari_ini) >= hari_ini],
                         key=lambda k: k.get("tarikh") or "")
    lepas = sorted([k for k in kursus if k not in akan_datang],
                   key=lambda k: k.get("tarikh") or "", reverse=True)

    # --- sepanduk kredensial
    kred = [("shield-check", "Pertubuhan Profesional<br>Berdaftar", SITE["pendaftaran"]),
            ("graduation-cap", "Pendidikan Klinikal<br>&amp; Latihan", "CCC · PCC · TTT"),
            ("stethoscope", "Pembangunan Profesional", "CPD &amp; Pembelajaran Berterusan"),
            ("users", "Komuniti<br>Seluruh Negara", "Seluruh Malaysia")]
    kred_html = "".join(
        '<div><span>%s</span><p><strong>%s</strong><small>%s</small></p></div>' % (icon(i), t, s)
        for i, t, s in kred)

    # --- statistik (PRD §11: hanya jika disahkan)
    nota_stats = stats.get("setakat") or ""
    if stats.get("disahkan"):
        stat_items = "".join(
            '<div class="stat"><span>%s</span><p><strong>%s</strong><b>%s</b><small>%s</small></p></div>'
            % (icon(it.get("ikon", "target")), esc(it["nilai"]), esc(it["label"]), esc(it.get("sub", "")))
            for it in stats["items"])
    else:
        kurang("Angka statistik (PRD §11) belum disahkan, data/stats.json masih 'disahkan': false.")
        stat_items = "".join(
            '<div class="stat"><span>%s</span><p><strong>…</strong><b>%s</b><small>Menunggu pengesahan</small></p></div>'
            % (icon(it.get("ikon", "target")), esc(it["label"]))
            for it in stats["items"])

    # --- kursus akan datang
    if akan_datang:
        kursus_html = kad_kursus(akan_datang[0], keutamaan=True)
        baki = "".join(
            '<article class="item no-photo"><div class="item-body">%s<h3><a href="/pendidikan/%s/">%s</a></h3>'
            '<div class="item-meta"><time datetime="%s">%s %s</time><span>%s %s</span></div>'
            '<a class="lebih" href="/pendidikan/%s/">Lihat butiran %s</a></div></article>'
            % (badge_status(k.get("status")), esc(k["slug"]), esc(k["tajuk"]), esc(k.get("tarikh", "")),
               icon("calendar-days"), esc(tarikh_pjg(parse_date(k.get("tarikh")))), icon("map-pin"),
               esc(k.get("tempat", "")), esc(k["slug"]), icon("arrow-right"))
            for k in akan_datang[1:4])
        kursus_html += ('<div class="listing" style="margin-top:18px">%s</div>' % baki) if baki else ""
    else:
        kurang("Tiada kursus akan datang dalam data/kursus.json: PRD §58 memerlukan sekurang-kurangnya satu program latihan yang boleh diterbitkan.")
        kursus_html = kosong(
            "calendar-days", "Tiada kursus akan datang buat masa ini",
            "Jadual latihan sedang disusun. Hubungi urusetia MADOCS untuk maklumat program seterusnya, atau lihat program yang telah dijalankan.",
            '<div style="margin-top:20px"><a class="btn btn-primary" href="/pendidikan/">Lihat program lepas</a></div>')
        if lepas:
            kursus_html += '<div style="margin-top:22px">%s</div>' % kad_kursus(lepas[0])

    # --- perkhidmatan
    servis = [("graduation-cap", "Pendidikan &amp; Latihan", "Program latihan klinikal berstruktur untuk meningkatkan kemahiran dan kompetensi pengamal."),
              ("shield-check", "Standard Klinikal", "Menyokong amalan berkhatan yang selamat melalui garis panduan dan standard terbaik."),
              ("target", "Pembangunan Profesional", "Menyediakan platform CPD, sokongan profesional dan perkongsian ilmu berterusan."),
              ("heart-handshake", "Advokasi &amp; Komuniti", "Mewakili kepentingan ahli dan menyokong program CSR serta kesihatan masyarakat.")]
    servis_html = "".join('<article><span>%s</span><div><h3>%s</h3><p>%s</p></div></article>'
                          % (icon(i), t, p) for i, t, p in servis)

    # --- mengapa sertai
    manfaat = "".join('<div class="tile tile-manfaat"><span class="ikon">%s</span><h3>%s</h3></div>'
                      % (icon("check"), esc(m)) for m in keahlian.get("manfaat", []))

    # --- aktiviti
    aktiviti_html = "".join(kad_aktiviti(a) for a in aktiviti[:4]) or kosong(
        "users", "Belum ada aktiviti diterbitkan", "Gambar dan laporan aktiviti MADOCS akan dimuat naik oleh urusetia.")

    # --- sumber
    if sumber:
        sumber_html = "".join(
            item_kandungan(s["tajuk"], (s.get("fail") if str(s.get("fail", "")).startswith("http") else "/" + str(s.get("fail", "")).lstrip("/")) or "/sumber/", s.get("ringkas", ""),
                           kategori=s.get("kategori", ""), alt=s.get("gambar_alt", ""), gambar=s.get("gambar"))
            for s in sumber[:3])
        sumber_html = '<div class="listing">%s</div>' % sumber_html
    else:
        kurang("Tiada sumber klinikal dalam data/sumber.json (PRD §19, §49).")
        sumber_html = kosong("book-open", "Pusat Sumber sedang disediakan",
                             "Bahan rujukan klinikal, garis panduan dan bahan pendidikan akan diterbitkan di sini selepas semakan klinikal (PRD §21).")

    # --- berita
    if berita:
        berita_html = "".join(
            item_kandungan(b["tajuk"], "/berita/%s/" % b["slug"], b.get("ringkas", ""),
                           tarikh=b.get("tarikh"), kategori=b.get("kategori", ""), alt=b.get("gambar_alt", ""), gambar=b.get("gambar"))
            for b in berita[:3])
        berita_html = '<div class="listing">%s</div>' % berita_html
    else:
        kurang("Tiada berita dalam data/berita.json (PRD §49).")
        berita_html = kosong("file-text", "Belum ada berita diterbitkan",
                             "Pengumuman dan berita MADOCS akan diterbitkan di sini.")

    hero_slaid_html = blok_hero_slaid()
    selang_slaid = load("hero.json").get("selang_saat") or 7
    isi = f"""<section class="hero" data-selang="{selang_slaid}">
  {hero_slaid_html}
  <div class="hero-wash"></div>
  {chip_ilustrasi("Dewan majlis pelancaran Garis Panduan Berkhatan 2026 di Hospital Shah Alam")}
  <div class="shell hero-content">
    <div class="hero-copy">
      <p class="hero-kicker">Ditubuhkan {esc(SITE['ditubuhkan'])} · Malaysia</p>
      <h1>{esc(SITE['nama'])} ({esc(SITE['singkatan'])})</h1>
      <h2>Memajukan Amalan Berkhatan Selamat di Malaysia</h2>
      <p>Memperkasa pengamal perubatan melalui pendidikan, latihan klinikal berstruktur, pembangunan profesional dan amalan khatan yang selamat.</p>
      <div class="hero-buttons">
        <a href="/pendidikan/" class="btn btn-primary">{icon('book-open')} Lihat kursus</a>
        <a href="/keahlian/sertai/" class="btn btn-outline">Sertai MADOCS</a>
      </div>
    </div>
  </div>
</section>

{_blok_kredensial(kred_html)}

<section class="section-pad seksyen-b" id="tentang">
  <div class="shell overview-grid">
    <div class="upcoming">
      <div class="section-title-row"><h2>Mengenai MADOCS</h2></div>
      <div class="prose">
        <p>{esc(SITE['nama'])} ({esc(SITE['singkatan'])}) ialah pertubuhan profesional yang menghimpunkan doktor yang terlibat dalam amalan, pendidikan dan latihan berkhatan di Malaysia.</p>
        <p>Kami menyediakan platform latihan klinikal berstruktur, pembangunan profesional berterusan dan perkongsian ilmu bagi meningkatkan kualiti serta keselamatan perkhidmatan berkhatan untuk masyarakat.</p>
      </div>
      <div style="margin-top:18px"><a class="btn btn-primary" href="/tentang/">Kenali MADOCS {icon('arrow-right')}</a></div>
    </div>
    <div class="what-we-do">
      <div class="section-title-row"><h2>Apa yang kami lakukan</h2></div>
      <div class="service-grid">{servis_html}</div>
    </div>
  </div>
</section>

<section class="stats-band seksyen-a">
  <div class="shell stats-grid">
    <h2>MADOCS dalam<br>Angka</h2>
    {stat_items}
  </div>
</section>

<section class="activities section-pad seksyen-b" id="aktiviti">
  <div class="shell">
    <div class="section-title-row activities-head">
      <h2>Aktiviti terkini</h2>
      <a href="/aktiviti/">Lihat semua aktiviti {icon('arrow-right')}</a>
    </div>
    <div class="activity-stage">
      <button class="carousel-arrow left" aria-label="Aktiviti sebelumnya">{icon('arrow-left')}</button>
      <div class="activity-grid">{aktiviti_html}</div>
      <button class="carousel-arrow right" aria-label="Aktiviti seterusnya">{icon('arrow-right')}</button>
    </div>
  </div>
</section>

<section class="section-pad seksyen-a">
  <div class="shell">
    <div class="section-title-row activities-head">
      <h2>Berita terkini</h2>
      <a href="/berita/">Semua berita {icon('arrow-right')}</a>
    </div>
    {berita_html}
  </div>
</section>

<section class="section-pad seksyen-b" id="kursus">
  <div class="shell">
    <div class="section-title-row activities-head">
      <h2>Kursus akan datang</h2>
      <a href="/pendidikan/">Lihat semua kursus {icon('arrow-right')}</a>
    </div>
    {kursus_html}
  </div>
</section>

<section class="section-pad seksyen-a">
  <div class="shell">
    <div class="section-title-row activities-head">
      <h2>Mengapa sertai MADOCS</h2>
      <a href="/keahlian/">Maklumat keahlian {icon('arrow-right')}</a>
    </div>
    <div class="grid-3">{manfaat}</div>
  </div>
</section>

{cta_komuniti()}

"""

    halaman("utama", "MADOCS: Pertubuhan Doktor Khatan Malaysia",
            "Pertubuhan Doktor Khatan Malaysia (MADOCS): keahlian, kursus PCC/CCC, latihan klinikal dan garis panduan berkhatan untuk doktor di Malaysia.",
            "/", isi)


# ----------------------------------------------------------------- halaman: tentang
def bina_tentang():
    jk_data = load("jawatankuasa.json")
    jk = jk_data["jawatankuasa"]
    sesi = (jk_data.get("sesi") or "").strip()
    tajuk_jk = "Jawatankuasa Eksekutif" + (f": Sesi {esc(sesi)}" if sesi else "")
    if not jk:
        kurang("Senarai Jawatankuasa Eksekutif kosong (data/jawatankuasa.json) — diperlukan oleh PRD §9.2 dan §55.")
        ahli_html = kosong("users", "Senarai jawatankuasa belum disediakan",
                           "Struktur halaman ini sedia untuk memaparkan Jawatankuasa Eksekutif"
                           + (f" Sesi {esc(sesi)}" if sesi else "")
                           + " sebaik sahaja nama dan gambar disahkan oleh MADOCS.")
    else:
        ahli_html = blok_jawatankuasa(jk_data)

    struktur_html = blok_struktur_organisasi(jk_data)

    fakta = {'<dt>': '<dt>', }
    tadbir = f"""<dl class="facts">
  <div><dt>Nama berdaftar</dt><dd>{esc(SITE.get('nama_rasmi') or (SITE['nama'] + ' (' + SITE['nama_en'] + ', ' + SITE['singkatan'] + ')'))}</dd></div>
  <div><dt>Nombor pendaftaran</dt><dd>{esc(SITE['pendaftaran'])}</dd></div>
  {f'<div><dt>Berdaftar dengan ROS</dt><dd>{esc(SITE["daftar_ros"])}</dd></div>' if SITE.get('daftar_ros') else ''}
  <div><dt>Ditubuhkan</dt><dd>{esc(SITE['ditubuhkan'])}</dd></div>
  <div><dt>Skop</dt><dd>Malaysia</dd></div>
  <div><dt>E-mel urusetia</dt><dd><a href="mailto:{esc(SITE['email'])}">{esc(SITE['email'])}</a></dd></div>
</dl>"""
    kurang("Visi, misi, sejarah dan dokumen tadbir urus/perlembagaan (PRD §9.2, §55) belum disediakan, halaman menggunakan teks sementara.")

    isi = page_hero([("Utama", "/"), ("Mengenai", None)], "Mengenai MADOCS",
                    "Pertubuhan profesional yang menghimpunkan doktor terlibat dalam amalan berkhatan di Malaysia.") + f"""
<section class="content-wrap">
  <div class="shell split">
    <div>
      <div class="card prose">
        <h2>Latar belakang</h2>
        <p>{esc(SITE['nama'])} ({esc(SITE['singkatan'])}) ialah pertubuhan profesional yang berdaftar dengan Pendaftar Pertubuhan Malaysia. MADOCS menghimpunkan doktor yang terlibat dalam amalan berkhatan dengan matlamat meningkatkan standard klinikal, keselamatan pesakit dan kualiti latihan.</p>
        <p>{esc(SITE['singkatan'])} didaftarkan dengan Pendaftar Pertubuhan Malaysia pada {esc(SITE['daftar_ros'])} di bawah nombor pendaftaran {esc(SITE['pendaftaran'])}.</p>
        <h2>Visi</h2>
        <p>Menjadi platform profesional yang terkemuka bagi doktor yang terlibat dalam amalan berkhatan di Malaysia.</p>
        <h2>Misi</h2>
        <ul>
          <li>Meningkatkan standard dan keselamatan amalan berkhatan melalui pendidikan dan latihan.</li>
          <li>Menyediakan latihan klinikal berstruktur dan pembangunan profesional berterusan.</li>
          <li>Menyokong perkongsian ilmu, penyelidikan dan jaringan profesional antara doktor.</li>
          <li>Mewakili kepentingan ahli dan menyokong program kesihatan masyarakat.</li>
        </ul>
        <h2>Tadbir urus</h2>
        {tadbir}
        <p class="nota-isi">Perlembagaan pertubuhan boleh dimuat turun di <a href="/sumber/">Pusat Sumber</a>, atau diminta daripada urusetia MADOCS.</p>
      </div>
      <div class="card">
        <h2>Prakata Presiden</h2>
        <p>Perutusan daripada Presiden MADOCS, Dr. Abdol Rashid bin Masrom.</p>
        <p style="margin-top:14px"><a class="btn btn-outline" href="/dari-meja-presiden/" style="display:inline-flex;align-items:center;text-decoration:none">Baca Dari Meja Presiden</a></p>
      </div>
      <div class="card">
        <h2>Organisasi</h2>
        <p>Carta organisasi, senarai Penasihat dan Jawatankuasa Eksekutif dipaparkan di halaman Organisasi.</p>
        <p style="margin-top:14px"><a class="btn btn-primary" href="/organisasi/">Lihat Organisasi MADOCS {icon('arrow-right')}</a></p>
      </div>
    </div>
    <aside class="side">
      <div class="card">
        <h3>Pintasan</h3>
        <nav class="side-nav">
          <a class="aktif" href="/tentang/">Mengenai MADOCS</a>
          <a href="/organisasi/">Organisasi &amp; jawatankuasa</a>
          <a href="/pendidikan/">Pendidikan &amp; Latihan</a>
          <a href="/keahlian/">Keahlian</a>
          <a href="/hubungi/">Hubungi urusetia</a>
        </nav>
      </div>
      <div class="card">
        <h3>Sertai MADOCS</h3>
        <p style="font-size:14px;line-height:1.7;color:#583c42">Doktor yang berminat dalam amalan berkhatan dialu-alukan menyertai MADOCS.</p>
        <a class="btn-blok" href="/keahlian/sertai/" style="margin-top:14px">Borang keahlian {icon('arrow-right')}</a>
      </div>
    </aside>
  </div>
</section>"""
    halaman("tentang", "Mengenai MADOCS | Pertubuhan Doktor Khatan Malaysia",
            "Mengenai Pertubuhan Doktor Khatan Malaysia (MADOCS): latar belakang, visi, misi, tadbir urus dan jawatankuasa eksekutif.",
            "/tentang/", isi)


# ----------------------------------------------------------------- halaman: organisasi
def bina_organisasi():
    jk_data = load("jawatankuasa.json")
    jk = jk_data.get("jawatankuasa") or []
    sesi = (jk_data.get("sesi") or "").strip()
    tajuk_jk = "Jawatankuasa Eksekutif" + (f": Sesi {esc(sesi)}" if sesi else "")
    if jk:
        ahli_html = blok_jawatankuasa(jk_data)
    else:
        ahli_html = kosong("users", "Senarai jawatankuasa belum disediakan",
                           "Struktur halaman ini sedia untuk memaparkan Jawatankuasa Eksekutif"
                           + (f" Sesi {esc(sesi)}" if sesi else "")
                           + " sebaik sahaja nama dan gambar disahkan oleh MADOCS.")
    struktur_html = blok_struktur_organisasi(jk_data)

    isi = page_hero([("Utama", "/"), ("Mengenai", "/tentang/"), ("Organisasi", None)], "Organisasi MADOCS",
                    "Tadbir urus pertubuhan: carta organisasi, Penasihat dan Jawatankuasa Eksekutif.") + f"""
<section class="content-wrap">
  <div class="shell split">
    <div>
      <div class="card">
        <h2>Struktur Organisasi</h2>
        {struktur_html}
      </div>
      <div class="card">
        <h2>{tajuk_jk}</h2>
        {ahli_html}
      </div>
    </div>
    <aside class="side">
      <div class="card">
        <h3>Pintasan</h3>
        <nav class="side-nav">
          <a class="aktif" href="/organisasi/">Organisasi MADOCS</a>
          <a href="/tentang/">Mengenai MADOCS</a>
          <a href="/dari-meja-presiden/">Dari Meja Presiden</a>
          <a href="/hubungi/">Hubungi urusetia</a>
        </nav>
      </div>
      <div class="card">
        <h3>Sertai MADOCS</h3>
        <p style="font-size:14px;line-height:1.7;color:#583c42">Doktor yang berminat dalam amalan berkhatan dialu-alukan menyertai MADOCS.</p>
        <a class="btn-blok" href="/keahlian/sertai/" style="margin-top:14px">Borang keahlian {icon('arrow-right')}</a>
      </div>
    </aside>
  </div>
</section>"""
    halaman("organisasi", "Organisasi MADOCS | Pertubuhan Doktor Khatan Malaysia",
            "Carta organisasi, Penasihat dan Jawatankuasa Eksekutif Pertubuhan Doktor Khatan Malaysia (MADOCS) sesi 2026-2028.",
            "/organisasi/", isi)


# ----------------------------------------------------------------- halaman: pendidikan
def bina_pendidikan():
    kursus = load("kursus.json")["kursus"]
    hari_ini = date.today()
    akan = sorted([k for k in kursus if k.get("status") in ("open", "limited", "tentatif")], key=lambda k: k.get("tarikh") or "")
    lepas = sorted([k for k in kursus if k.get("status") in ("closed", "done")], key=lambda k: k.get("tarikh") or "", reverse=True)
    if not lepas:
        lebih = sorted(load("aktiviti.json")["aktiviti"], key=lambda a: a.get("tarikh") or "", reverse=True)[:3]
        blok_lepas = ('<div class="listing">%s</div>' % "".join(
            item_kandungan(a["tajuk"], "/aktiviti/%s/" % a["slug"], a.get("ringkas", ""),
                           tarikh=a.get("tarikh"), kategori=a.get("kategori", ""),
                           gambar=a.get("gambar"), alt=a.get("gambar_alt", "")) for a in lebih)
            + '<div style="margin-top:16px"><a class="btn btn-outline" href="/aktiviti/">Semua aktiviti MADOCS</a></div>')
    else:
        blok_lepas = senarai(lepas)

    kategori = [("graduation-cap", "Kursus Komprehensif Berkhatan", "CCC", "Latihan menyeluruh: teori, demonstrasi, amali dan penilaian."),
                ("stethoscope", "Pendidikan Klinikal &amp; Procedural", "PCC", "Kemahiran prosedur klinikal dan pengurusan komplikasi."),
                ("users", "Latihan Tenaga Pengajar", "TTT", "Menyediakan tenaga pengajar bertauliah dalam latihan MADOCS."),
                ("file-text", "Seminar, Bengkel &amp; Konferens", "Aktiviti", "Pembelajaran berterusan dan perkongsian ilmu profesional.")]

    def senarai(items, kosong_teks):
        if not items:
            return kosong_teks
        return '<div class="listing">%s</div>' % "".join(
            item_kandungan(k["tajuk"], "/pendidikan/%s/" % k["slug"], k.get("ringkas", ""),
                           tarikh=k.get("tarikh"), kategori=k.get("kod", ""), gambar=k.get("gambar"),
                           alt=k.get("gambar_alt", ""), kredit=k.get("gambar_kredit"))
            for k in items)

    isi = page_hero([("Utama", "/"), ("Pendidikan & Latihan", None)],
                    "Pendidikan & Latihan",
                    "Program latihan klinikal berstruktur untuk doktor yang terlibat dalam amalan berkhatan.",
                    '<div class="hero-buttons"><a class="btn btn-primary" href="#akan-datang">Kursus akan datang</a>'
                    '<a class="btn btn-outline" href="/keahlian/sertai/">Sertai MADOCS</a></div>') + f"""
<section class="content-wrap">
  <div class="shell">
    <div class="grid-4">{''.join('<div class="tile"><span class="ikon">%s</span><h3>%s</h3><p>%s</p></div>' % (icon(i), t, p) for i, t, c, p in kategori)}</div>
  </div>
</section>

<section class="content-wrap" id="akan-datang">
  <div class="shell">
    <div class="section-title-row activities-head"><h2>Kursus akan datang</h2></div>
    {senarai(akan, kosong("calendar-days", "Tiada kursus akan datang buat masa ini",
                          "Jadual latihan sedang disusun. Hubungi urusetia MADOCS atau semak semula tidak lama lagi.",
                          '<div style="margin-top:20px"><a class="btn btn-primary" href="/hubungi/">Hubungi urusetia</a></div>'))}
  </div>
</section>

<section class="content-wrap">
  <div class="shell">
    <div class="section-title-row activities-head"><h2>Program lepas</h2></div>
    {blok_lepas}
  </div>
</section>

{cta_komuniti(tajuk='Pertanyaan tentang latihan MADOCS',
              mesej='Urusetia MADOCS boleh membantu anda memilih program latihan yang sesuai dengan keperluan amalan anda.',
              label='Hubungi urusetia', href='/hubungi/')}"""
    halaman("pendidikan", "Pendidikan & Latihan | MADOCS",
            "Kursus, bengkel dan latihan klinikal berstruktur MADOCS untuk doktor di Malaysia: CCC, PCC, TTT dan aktiviti pembelajaran berterusan.",
            "/pendidikan/", isi)


def bina_kursus_detail(k):
    d = parse_date(k.get("tarikh"))
    selesai = k.get("status") in ("closed", "done")
    fakta = []

    def baris(kunci, nilai):
        if nilai:
            fakta.append("<div><dt>%s</dt><dd>%s</dd></div>" % (esc(kunci), nilai))

    baris("Tarikh", esc(tarikh_pjg(d)) if d else "")
    if k.get("masa_mula"):
        baris("Masa", esc(k["masa_mula"]) + " - " + esc(k.get("masa_tamat", "")))
    baris("Tempat", esc(k.get("tempat", "")))
    baris("Penganjur", esc(k.get("penganjur", "")))
    baris("Tenaga pengajar", esc(k.get("fakulti") or "Akan disahkan"))
    baris("Peserta sasaran", esc(k.get("sasaran", "")))
    baris("Yuran", esc(k.get("yuran") or "Akan disahkan"))
    if k.get("yuran_ahli"):
        baris("Yuran ahli", esc(k["yuran_ahli"]))
    if k.get("yuran_bukan_ahli"):
        baris("Yuran bukan ahli", esc(k["yuran_bukan_ahli"]))
    baris("Tutup pendaftaran", esc(tarikh_pdk(parse_date(k["tutup_daftar"]))) if k.get("tutup_daftar") else "Akan disahkan")
    baris("Kapasiti peserta", (esc(k["kapasiti"])
          + (f" · {esc(k['baki'])} tempat berbaki" if k.get("baki") else "")) if k.get("kapasiti") else "Akan disahkan")
    baris("Status", badge_status(k.get("status")))

    for medan, label in (("objektif", "Objektif pembelajaran"), ("rangka", "Rangka program")):
        if not k.get(medan):
            kurang("Butiran '%s' belum diisi untuk kursus %s (PRD §12)." % (label, k["kod"]))
    for medan in ("yuran", "tutup_daftar", "kapasiti", "fakulti"):
        if not k.get(medan):
            kurang("Medan '%s' kosong untuk kursus %s (PRD §12)." % (medan, k["kod"]))

    objektif = '<h2>Objektif pembelajaran</h2><p class="nota-isi">Akan disahkan.</p>'
    if k.get("objektif"):
        objektif = "<h2>Objektif pembelajaran</h2><ul>%s</ul>" % "".join("<li>%s</li>" % esc(o) for o in k["objektif"])
    rangka = '<h2>Rangka program</h2><p class="nota-isi">Akan disahkan.</p>'
    if k.get("rangka"):
        rangka = "<h2>Rangka program</h2><dl class='facts'>%s</dl>" % "".join(
            "<div><dt>%s</dt><dd>%s</dd></div>" % (esc(r.get("masa", "")), esc(r.get("slot", ""))) for r in k["rangka"])

    kandungan = "".join("<p>%s</p>" % esc(p) for p in k.get("kandungan", []))

    # pautan kalendar & kongsi (§13)
    kal = ""
    if d and k.get("masa_mula"):
        h1, m1 = (k["masa_mula"].split(":") + ["00"])[:2]
        h2_, m2 = ((k.get("masa_tamat") or k["masa_mula"]).split(":") + ["00"])[:2]
        mula = "%sT%s%s00" % (d.strftime("%Y%m%d"), h1.zfill(2), m1.zfill(2))
        tamat = "%sT%s%s00" % (d.strftime("%Y%m%d"), h2_.zfill(2), m2.zfill(2))
        kal = ("https://calendar.google.com/calendar/render?action=TEMPLATE&text=%s&dates=%s/%s&details=%s&location=%s"
               % (k["tajuk"].replace(" ", "+"), mula, tamat,
                  ("Maklumat lanjut: " + BASE + "/pendidikan/" + k["slug"] + "/").replace(" ", "+"),
                  (k.get("tempat") or "").replace(" ", "+")))
    url_kongsi = BASE + "/pendidikan/" + k["slug"] + "/"
    kongsi = f"""<div class="chips" aria-label="Kongsi kursus ini">
  <span style="background:#fff;border:1px solid var(--line)">Kongsi:</span>
  <a class="badge" href="https://wa.me/?text={esc(k['tajuk'] + ': ' + url_kongsi)}" target="_blank" rel="noopener">WhatsApp</a>
  <a class="badge" href="https://www.facebook.com/sharer/sharer.php?u={esc(url_kongsi)}" target="_blank" rel="noopener">Facebook</a>
  <a class="badge" href="https://t.me/share/url?url={esc(url_kongsi)}&text={esc(k['tajuk'])}" target="_blank" rel="noopener">Telegram</a>
  <a class="badge" href="mailto:?subject={esc(k['tajuk'])}&body={esc(url_kongsi)}">E-mel</a>
</div>"""

    if selesai:
        butang_daftar = (f'<div class="form-note" style="margin-top:18px"><b>Program ini telah selesai.</b> '
                         f'Maklumat program akan datang boleh dilihat di halaman <a href="/pendidikan/">Pendidikan &amp; Latihan</a>. '
                         f'Untuk pertanyaan, hubungi urusetia MADOCS.</div>')
    elif k.get("daftar_url"):
        butang_daftar = (f'<a class="btn-hantar" href="{esc(k["daftar_url"])}" target="_blank" rel="noopener">'
                         f'Daftar sekarang {icon("external-link")}</a>')
    else:
        kurang("Pautan pendaftaran (daftar_url) belum ditetapkan untuk kursus %s (PRD §14)." % k["kod"])
        butang_daftar = (f'<a class="btn-hantar" href="/hubungi/?kursus={esc(k["slug"])}">'
                         f'Daftar melalui urusetia {icon("arrow-right")}</a>')

    kaitan = [x for x in load("kursus.json")["kursus"] if x["slug"] != k["slug"]][:2]
    kaitan_html = ""
    if kaitan:
        kaitan_html = '<div class="card"><h2>Program lain</h2><div class="listing">%s</div></div>' % "".join(
            item_kandungan(x["tajuk"], "/pendidikan/%s/" % x["slug"], x.get("ringkas", ""),
                           tarikh=x.get("tarikh"), kategori=x.get("kod", "")) for x in kaitan)

    ld = []
    if d:
        ld.append({"@context": "https://schema.org", "@type": "Course",
                   "name": k["tajuk"], "description": k.get("ringkas", ""),
                   "provider": {"@type": "Organization", "name": SITE["nama"], "sameAs": BASE + "/"},
                   "url": url_kongsi,
                   "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "onsite",
                                         "startDate": k.get("tarikh", ""),
                                         "location": {"@type": "Place", "name": k.get("tempat", ""),
                                                      "address": {"@type": "PostalAddress", "addressCountry": "MY"}}}})

    isi = page_hero([("Utama", "/"), ("Pendidikan & Latihan", "/pendidikan/"), (k["kod"], None)],
                    k["tajuk"], k.get("ringkas", "")) + f"""
<section class="content-wrap">
  <div class="shell split">
    <div>
      <div class="card">
        <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:16px">
          <span class="course-code">{esc(k.get('kod',''))}</span>{badge_status(k.get('status'))}
        </div>
        {'<img src="/%s" alt="%s" style="width:100%%;border-radius:11px;margin-bottom:22px">' % (esc(k['gambar']), esc(k.get('gambar_alt') or k['tajuk'])) if k.get('gambar') else ''}
        {f'<p class="kredit-foto">{esc(k["gambar_kredit"])}</p>' if k.get('gambar_kredit') else ''}
        <div class="prose">{kandungan}</div>
        {objektif}
        {rangka}
      </div>
      <div class="card">
        <h2>Maklumat program</h2>
        <dl class="facts">{''.join(fakta)}</dl>
        <div style="margin-top:22px;display:flex;gap:12px;flex-wrap:wrap;align-items:center">
          {butang_daftar}
          {f'<a class="btn btn-outline" href="{kal}" target="_blank" rel="noopener">{icon("calendar-days")} TAMBAH KE KALENDAR</a>' if kal else ''}
        </div>
        {kongsi}
      </div>
      {kaitan_html}
    </div>
    <aside class="side">
      <div class="card">
        <h3>Ringkasan</h3>
        <div class="item-meta" style="display:grid;gap:9px">
          <time datetime="{esc(k.get('tarikh',''))}">{icon('calendar-days')}{esc(tarikh_pjg(d))}</time>
          <span>{icon('map-pin')}{esc(k.get('tempat',''))}</span>
          <span>{icon('users')}{esc(k.get('sasaran',''))}</span>
        </div>
        <a class="btn-blok" href="{'/pendidikan/' if selesai else '#kandungan'}" style="margin-top:16px">{icon('calendar-days')} {'Kursus akan datang' if selesai else 'Maklumat pendaftaran'}</a>
      </div>
      <div class="card">
        <h3>Perlukan bantuan?</h3>
        <p style="font-size:14px;line-height:1.7;color:#583c42">Hubungi urusetia MADOCS untuk pertanyaan tentang pendaftaran, yuran atau keperluan kursus.</p>
        <a class="btn-blok wa" href="{wa_pautan('Salam, saya ingin bertanya tentang kursus ' + k['tajuk'] + ' (' + k.get('kod','') + ').')}" target="_blank" rel="noopener" style="margin-top:14px">{icon('message-circle')} WhatsApp urusetia</a>
        <a class="btn-blok ghost" href="/hubungi/" style="margin-top:9px">{icon('mail')} E-mel / borang</a>
      </div>
    </aside>
  </div>
</section>"""

    halaman("pendidikan", "%s: %s | MADOCS" % (k["tajuk"], k.get("kod", "")),
            k.get("ringkas", "%s oleh MADOCS." % k["tajuk"])[:180],
            "/pendidikan/%s/" % k["slug"], isi, og_jenis="article", jsonld=ld,
            gambar_og=k.get("gambar"))


# ----------------------------------------------------------------- halaman: keahlian
def bina_keahlian():
    kh = load("keahlian.json")
    disahkan = kh.get("disahkan")
    jika_belum = ""

    if not disahkan:
        kurang("Maklumat keahlian (kelayakan, kategori, yuran) belum disahkan, data/keahlian.json 'disahkan': false (PRD §56.1-§56.3).")
        jika_belum = ('<div class="pengesahan"><b>Belum disahkan jawatankuasa:</b> kelayakan, kategori dan yuran keahlian '
                      'sedang disahkan. Laman ini hanya menerbitkan maklumat yang telah diluluskan. Sila hubungi urusetia '
                      'MADOCS untuk maklumat terkini.</div>')
    elif kh.get("sumber_nota"):
        jika_belum = '<div class="nota-sumber">%s</div>' % esc(kh["sumber_nota"])

    _form = (kh.get("promosi") or {}).get("borang_url") or kh.get("borang_url") or "/keahlian/sertai/"
    _pautan_borang = esc(_form)
    manfaat = "".join('<div class="tile tile-manfaat"><span class="ikon">%s</span><h3>%s</h3></div>' % (icon("check"), esc(m))
                      for m in kh.get("manfaat", []))

    def jadual(baris, kepala, kosong_teks):
        if not baris:
            return '<div class="form-note">%s</div>' % esc(kosong_teks)
        return ('<div class="table-wrap"><table class="data"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
                % ("".join("<th>%s</th>" % esc(h) for h in kepala),
                   # data-label membolehkan jadual "bertimbun" pada telefon (lihat extra.css)
                   "".join("<tr>%s</tr>" % "".join(
                       '<td data-label="%s">%s</td>' % (esc(kepala[i]) if i < len(kepala) else "", c)
                       for i, c in enumerate(r)) for r in baris)))

    kategori = jadual([[esc(k["nama"]), esc(k.get("kelayakan", ""))] for k in kh.get("kategori", [])],
                      ["Kategori", "Kelayakan"],
                      "Kategori keahlian sedang disahkan oleh jawatankuasa MADOCS.")

    yuran = jadual([[esc(y["kategori"]), esc(y["yuran"]), esc(y.get("nota", ""))] for y in kh.get("yuran", [])],
                   ["Kategori", "Yuran", "Nota"],
                   "Struktur yuran keahlian sedang disahkan. Sila rujuk urusetia MADOCS.")

    hak_undi = ('<div class="form-note" style="margin-top:12px"><b>Hak mengundi:</b> %s</div>'
                % esc(kh["hak_undi"])) if kh.get("hak_undi") else ""

    kelayakan = "".join("<li>%s</li>" % esc(x) for x in kh.get("kelayakan", [])) or \
        "<li>Butiran kelayakan sedang disahkan oleh jawatankuasa.</li>"
    dokumen = "".join("<li>%s</li>" % esc(x) for x in kh.get("dokumen", [])) or \
        "<li>Senarai dokumen sokongan akan disediakan oleh urusetia.</li>"
    proses = "".join('<div><time>Langkah %d</time><strong>%s</strong></div>' % (i + 1, esc(p))
                     for i, p in enumerate(kh.get("proses", [])))

    faq = "".join('<details><summary>%s</summary><div class="jawapan"><p>%s</p></div></details>' % (esc(f["s"]), esc(f["j"]))
                  for f in kh.get("faq", []))
    ld_faq = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": f["s"],
                              "acceptedAnswer": {"@type": "Answer", "text": f["j"]}} for f in kh.get("faq", [])]}

    isi = page_hero([("Utama", "/"), ("Keahlian", None)], "Keahlian MADOCS",
                    "Sertai komuniti profesional doktor yang terlibat dalam amalan berkhatan di Malaysia.",
                    '<div class="hero-buttons"><a class="btn btn-primary" href="/keahlian/sertai/">Sertai MADOCS</a>'
                    '<a class="btn btn-outline" href="#faq">Soalan lazim</a></div>') + f"""
<section class="content-wrap seksyen-rose">
  <div class="shell">
    {jika_belum}
    <div class="form-note" style="display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between">
      <span><b>Credentialing &amp; Privileging (C&amp;P):</b> keahlian MADOCS berasingan daripada penilaian C&amp;P. Doktor yang mahu melakukan prosedur di fasiliti perlu melalui C&amp;P melalui portal iHealth.</span>
      <a class="btn btn-outline" href="/cp/">Maklumat C&amp;P</a>
    </div>
    <div class="grid-2" style="align-items:start">
      <div class="card prose">
        <h2>Mengapa menyertai MADOCS</h2>
        <p>MADOCS menghimpunkan doktor yang serius dalam meningkatkan kualiti amalan berkhatan. Keahlian memberi akses kepada latihan klinikal berstruktur, rangkaian profesional dan sumber pendidikan.</p>
        <p style="margin-top:14px"><b>Manfaat utama keahlian:</b></p>
      </div>
      <div class="card">
        <h2>Kategori &amp; kelayakan</h2>
        {kategori}
        <h3>Syarat am</h3>
        <ul class="prose" style="padding-left:18px">{kelayakan}</ul>
      </div>
    </div>
    <div class="manfaat-keahlian">{manfaat}</div>
    <div class="card" style="margin-top:18px">
      <h2>Yuran keahlian</h2>
      {yuran}
      {hak_undi}
    </div>
    <div class="grid-2" style="margin-top:18px;align-items:start">
      <div class="card">
        <h2>Keahlian MADOCS</h2>
        {blok_statistik_keahlian(kh)}
      </div>
      <div class="card">
        <h2>Dokumen diperlukan</h2>
        <ul class="prose" style="padding-left:18px">{dokumen}</ul>
        <p style="margin-top:14px"><a class="btn btn-outline" href="/semak-ahli/">Semak status keahlian</a></p>
      </div>
    </div>
  </div>
</section>

<section class="content-wrap seksyen-rose" style="padding-top:0">
  <div class="shell split lebar">
    <div>
      <div class="card">
        <h2>Proses permohonan</h2>
        <div class="timeline">{proses}</div>
        <div style="margin-top:24px"><a class="btn-hantar" href="{_pautan_borang}" target="_blank" rel="noopener">Mula permohonan {icon('arrow-right')}</a></div>
      </div>
      <div class="card" id="faq">
        <h2>Soalan lazim</h2>
        <div class="faq">{faq}</div>
      </div>
    </div>
  </div>
</section>

{blok_promosi_keahlian(kh)}
<section class="content-wrap"><div class="shell">{kotak_bantuan("Ada pertanyaan tentang keahlian?", "Hubungi urusetia MADOCS untuk kelayakan, kategori atau yuran keahlian.", "Salam, saya ingin bertanya tentang keahlian MADOCS.", wa_keahlian_nombor())}</div></section>

{cta_komuniti(label='Sertai MADOCS sekarang')}"""
    halaman("keahlian", "Keahlian | MADOCS",
            "Keahlian MADOCS: manfaat, kelayakan, kategori, yuran dan proses permohonan untuk doktor yang terlibat dalam amalan berkhatan di Malaysia.",
            "/keahlian/", isi, jsonld=[ld_faq])


def bina_sertai():
    endpoint = (SITE.get("borang_endpoint") or "").strip()
    # Borang rasmi diuruskan melalui pautan luar (Google Form) yang disahkan jawatankuasa.
    _kh = load("keahlian.json")
    borang_url = (_kh.get("borang_url") or (_kh.get("promosi") or {}).get("borang_url") or "").strip()
    if not endpoint and not borang_url:
        kurang("Borang keahlian belum diaktifkan, tiada site.json → borang_endpoint dan tiada keahlian.json → borang_url (PRD §16).")

    pilihan_kategori = ['<option value="">Pilih kategori</option>'] + [
        '<option value="%s">%s</option>' % (esc(k["nama"]), esc(k["nama"])) for k in load("keahlian.json").get("kategori", [])]

    if borang_url:
        # Borang awam sudah aktif, jangan tunjuk medan berganda; hantar terus ke borang rasmi.
        isi = page_hero([("Utama", "/"), ("Keahlian", "/keahlian/"), ("Permohonan", None)],
                        "Borang Permohonan Keahlian",
                        "Borang rasmi MADOCS. Permohonan dibentangkan dalam mesyuarat Ahli Jawatankuasa sebelum diluluskan.") + f"""
<section class="content-wrap">
  <div class="shell split">
    <div>
      <div class="card prose">
        <h2>Isi borang dalam talian</h2>
        <p>Borang permohonan keahlian MADOCS diuruskan melalui borang rasmi dalam talian. Butiran yang diminta termasuk maklumat peribadi, pendaftaran MMC, tempat praktis dan kategori keahlian.</p>
        <p>Permohonan akan dibentangkan dalam mesyuarat Ahli Jawatankuasa. Nombor ahli diberikan <b>selepas</b> permohonan diluluskan, dan anda akan dimaklumkan melalui e-mel.</p>
        <div class="hero-buttons" style="margin-top:20px">
          <a class="btn btn-primary" href="{esc(borang_url)}" target="_blank" rel="noopener">{icon('file-text')} Isi borang keahlian dalam talian</a>
        </div>
        <p class="nota-isi" style="margin-top:16px">Data peribadi diproses menurut <a href="/dasar-privasi/">Dasar Privasi</a> MADOCS. Borang mengandungi notis privasi dan kotak persetujuan yang perlu ditanda sebelum dihantar.</p>
      </div>
    </div>
    <aside class="side">
      <div class="card">
        <h3>Sebelum mengisi</h3>
        <ul class="prose" style="padding-left:18px;font-size:14px">
          <li>Nombor pendaftaran MMC dan butiran amalan anda.</li>
          <li>E-mel dan nombor telefon yang aktif.</li>
          <li>Alamat rumah dan pejabat (poskod kedua-duanya).</li>
          <li>Bukti bayaran yuran selepas permohonan disemak.</li>
        </ul>
      </div>
      <div class="card">
        <h3>Soalan?</h3>
        <p style="font-size:14px;line-height:1.7;color:#583c42">Urusetia keahlian sedia membantu.</p>
        <a class="btn-blok ghost" href="{wa_pautan('Salam, saya ingin bertanya tentang permohonan keahlian MADOCS.', wa_keahlian_nombor())}" target="_blank" rel="noopener" style="margin-top:14px">{icon('message-circle')} WhatsApp urusetia</a>
      </div>
    </aside>
  </div>
</section>"""
        halaman("keahlian", "Borang Permohonan Keahlian | MADOCS",
                "Borang permohonan keahlian MADOCS untuk doktor yang terlibat dalam amalan berkhatan di Malaysia.",
                "/keahlian/sertai/", isi)
        return

    if endpoint:
        aksi = f'<form class="form" action="{esc(endpoint)}" method="POST">'
        hantar = f'<button class="btn-hantar" type="submit">Hantar permohonan {icon("arrow-right")}</button>'
        nota = ('<div class="form-note">Maklumat anda dihantar kepada urusetia MADOCS untuk semakan. '
                'Sila pastikan butiran tepat. Data peribadi diproses menurut <a href="/dasar-privasi/">Dasar Privasi</a> kami.</div>')
    else:
        aksi = '<form class="form" method="get" action="/hubungi/">'
        hantar = ('<a class="btn-hantar" href="mailto:%s?subject=Permohonan%%20Keahlian%%20MADOCS">'
                  'E-MEL URUSETIA %s</a>' % (esc(SITE["email"]), icon("mail")))
        nota = ('<div class="form-note"><b>Borang dalam talian belum diaktifkan.</b> Buat masa ini, sila hantar '
                'permohonan melalui e-mel atau WhatsApp urusetia MADOCS: <a href="mailto:%s">%s</a> · '
                '<a href="tel:%s">%s</a> · <a href="%s" target="_blank" rel="noopener">WhatsApp</a>. '
                'Sediakan butiran di bawah untuk memudahkan urusan.</div>'
                % (esc(SITE["email"]), esc(SITE["email"]), esc(SITE["telefon"]), esc(SITE["telefon_papar"]),
                   esc(wa_pautan("Salam, saya ingin memohon keahlian MADOCS.", wa_keahlian_nombor()))))

    borang = f"""{aksi}
  <div class="form-grid">
    <div class="field"><label for="nama">Nama penuh (dengan gelaran) *</label><input id="nama" name="nama" required autocomplete="name"></div>
    <div class="field"><label for="email">E-mel *</label><input id="email" name="email" type="email" required autocomplete="email"></div>
    <div class="field"><label for="telefon">No. telefon / WhatsApp *</label><input id="telefon" name="telefon" required autocomplete="tel"></div>
    <div class="field"><label for="mmc">No. pendaftaran MMC</label><input id="mmc" name="mmc" placeholder="cth. 12345"></div>
    <div class="field"><label for="praktis">Tempat praktis / klinik</label><input id="praktis" name="praktis"></div>
    <div class="field"><label for="negeri">Negeri</label>
      <select id="negeri" name="negeri">
        <option value="">Pilih negeri</option>
        {''.join('<option>%s</option>' % n for n in ['Johor','Kedah','Kelantan','Melaka','Negeri Sembilan','Pahang','Perak','Perlis','Pulau Pinang','Sabah','Sarawak','Selangor','Terengganu','W.P. Kuala Lumpur','W.P. Labuan','W.P. Putrajaya'])}
      </select>
    </div>
    <div class="field"><label for="kategori">Kategori keahlian</label>
      <select id="kategori" name="kategori">{''.join(pilihan_kategori)}</select>
    </div>
    <div class="field penuh"><label for="pengalaman">Pengalaman berkaitan amalan berkhatan</label>
      <textarea id="pengalaman" name="pengalaman" placeholder="Ringkaskan pengalaman, latihan atau minat anda berkaitan amalan berkhatan."></textarea>
    </div>
    <div class="field penuh">
      <label class="pilihan"><input type="checkbox" name="persetujuan" required> Saya mengesahkan maklumat di atas benar dan bersetuju data peribadi saya diproses untuk tujuan keahlian MADOCS.</label>
    </div>
  </div>
  <div style="margin-top:22px">{hantar}</div>
  <p class="nota-isi" style="margin-top:14px">* Wajib diisi.</p>
</form>"""

    isi = page_hero([("Utama", "/"), ("Keahlian", "/keahlian/"), ("Permohonan", None)],
                    "Borang Permohonan Keahlian",
                    "Isi maklumat di bawah. Urusetia MADOCS akan menghubungi anda selepas semakan.") + f"""
<section class="content-wrap">
  <div class="shell split">
    <div>
      <div class="card">
        {nota}
        {borang}
      </div>
    </div>
    <aside class="side">
      <div class="card">
        <h3>Sebelum menghantar</h3>
        <ul class="prose" style="padding-left:18px;font-size:14px">
          <li>Sediakan nombor pendaftaran MMC dan butiran amalan anda.</li>
          <li>Pastikan e-mel dan nombor telefon aktif.</li>
          <li>Permohonan disemak oleh Jawatankuasa Keahlian.</li>
        </ul>
      </div>
      <div class="card">
        <h3>Soalan?</h3>
        <p style="font-size:14px;line-height:1.7;color:#583c42">Urusetia MADOCS sedia membantu.</p>
        <a class="btn-blok ghost" href="/hubungi/" style="margin-top:14px">{icon('mail')} Hubungi urusetia</a>
      </div>
    </aside>
  </div>
</section>"""
    halaman("keahlian", "Borang Permohonan Keahlian | MADOCS",
            "Borang permohonan keahlian MADOCS untuk doktor yang terlibat dalam amalan berkhatan di Malaysia.",
            "/keahlian/sertai/", isi)


# ----------------------------------------------------------------- halaman: aktiviti
def bina_aktiviti():
    aktiviti = sorted(load("aktiviti.json")["aktiviti"], key=lambda a: a.get("tarikh") or "", reverse=True)
    senarai = ('<div class="listing">%s</div>' % "".join(
        item_kandungan(a["tajuk"], "/aktiviti/%s/" % a["slug"], a.get("ringkas", ""),
                       tarikh=a.get("tarikh"), kategori=a.get("kategori", ""), gambar=a.get("gambar"),
                       alt=a.get("gambar_alt", ""), tarikh_papar=a.get("tarikh_papar")) for a in aktiviti)) if aktiviti else kosong(
        "users", "Belum ada aktiviti diterbitkan",
        "Laporan dan gambar aktiviti MADOCS akan diterbitkan di sini.")

    isi = page_hero([("Utama", "/"), ("Aktiviti", None)], "Aktiviti MADOCS",
                    "Program latihan, seminar, bengkel dan aktiviti komuniti MADOCS di seluruh Malaysia.",
                    '<div class="hero-buttons"><a class="btn btn-primary" href="/pendidikan/">Program akan datang</a>'
                    '<a class="btn btn-outline" href="/keahlian/sertai/">Sertai MADOCS</a></div>') + f"""
<section class="content-wrap">
  <div class="shell">{senarai}</div>
</section>
{cta_komuniti(label='Hubungi urusetia', href='/hubungi/')}"""
    halaman("aktiviti", "Aktiviti | MADOCS",
            "Aktiviti dan program MADOCS: latihan klinikal, seminar, bengkel dan program komuniti di seluruh Malaysia.",
            "/aktiviti/", isi)


def bina_aktiviti_detail(a):
    d = parse_date(a.get("tarikh"))
    gambar = ('<img src="/%s" alt="%s" style="width:100%%;border-radius:11px;margin-bottom:22px">'
              % (esc(a["gambar"]), esc(a.get("gambar_alt") or a["tajuk"]))) if a.get("gambar") else ""
    if not a.get("ringkas"):
        kurang("Keterangan/laporan belum ditulis untuk aktiviti '%s' (PRD §24)." % a["tajuk"])
    ld = {"@context": "https://schema.org", "@type": "Event", "name": a["tajuk"],
          "startDate": a.get("tarikh", ""),
          "eventStatus": "https://schema.org/EventScheduled",
          "location": {"@type": "Place", "name": a.get("tempat", ""), "address": {"@type": "PostalAddress", "addressCountry": "MY"}},
          "organizer": {"@type": "Organization", "name": SITE["nama"], "url": BASE + "/"}}
    isi = page_hero([("Utama", "/"), ("Aktiviti", "/aktiviti/"), (a["tajuk"], None)], a["tajuk"],
                    ringkas_meta(a.get("ringkas") or (a.get('tarikh_papar') or (tarikh_pdk(d) if d else '')))) + f"""
<section class="content-wrap">
  <div class="shell split">
    <div>
      <div class="card">
        <div class="chips" style="margin-bottom:16px"><span class="badge">{esc(a.get('kategori',''))}</span></div>
        {gambar}
        <div class="prose">
          {('<p>%s</p>' % esc(a['ringkas'])) if a.get('ringkas') else '<p class="nota-isi">Laporan penuh aktiviti ini belum disediakan.</p>'}
        </div>
      </div>
    </div>
    <aside class="side">
      <div class="card">
        <h3>Butiran</h3>
        <div class="item-meta" style="display:grid;gap:9px">
          <time datetime="{esc(a.get('tarikh',''))}">{icon('calendar-days')}{esc(a.get('tarikh_papar') or (tarikh_pjg(d) if d else ''))}</time>
          <span>{icon('map-pin')}{esc(a.get('tempat',''))}</span>
        </div>
        <a class="btn-blok ghost" href="/aktiviti/" style="margin-top:16px">{icon('arrow-left')} Semua aktiviti</a>
      </div>
      <div class="card">
        <h3>Ingin menyertai program seterusnya?</h3>
        <a class="btn-blok" href="/pendidikan/" style="margin-top:12px">Lihat kursus akan datang</a>
      </div>
    </aside>
  </div>
</section>"""
    halaman("aktiviti", tajuk_meta(a["tajuk"], " | Aktiviti MADOCS"),
            ringkas_meta(a.get("ringkas") or ("%s, program MADOCS%s%s. Laporan dan gambar aktiviti "
                                              "Pertubuhan Doktor Khatan Malaysia." %
                                              (a["tajuk"],
                                               (", " + a["tempat"]) if a.get("tempat") else "",
                                               (", " + (a.get('tarikh_papar') or tarikh_pdk(d))) if (a.get('tarikh_papar') or d) else ""))),
            "/aktiviti/%s/" % a["slug"], isi, og_jenis="article", jsonld=[ld],
            gambar_og=a.get("gambar"))


# ----------------------------------------------------------------- halaman: sumber
def bina_sumber():
    sumber = sorted(load("sumber.json")["sumber"], key=lambda s: s.get("tarikh") or "", reverse=True)
    if sumber:
        kad = []
        for s in sumber:
            fail = str(s.get("fail") or "")
            url = fail if fail.startswith("http") else "/" + fail.lstrip("/")
            luar = fail.startswith("http")
            label = "Buka pautan" if luar else "Muat turun"
            kategori = s.get("kategori", "")
            if s.get("akses") == "ahli":
                kategori = (kategori + " · Ahli sahaja").strip(" ·")
            kad.append(item_kandungan(s["tajuk"], url, s.get("ringkas", ""), tarikh=s.get("tarikh"),
                                      kategori=kategori, label=label))
        senarai = '<div class="listing">%s</div>' % "".join(kad)
    else:
        kurang("Pusat Sumber kosong (data/sumber.json) — PRD §19 dan §49.")
        senarai = kosong("book-open", "Pusat Sumber sedang disediakan",
                         "Bahan rujukan klinikal, garis panduan, bahan pendidikan dan pautan luaran akan diterbitkan di sini selepas semakan klinikal oleh penyemak bertauliah (PRD §21).",
                         '<div style="margin-top:20px"><a class="btn btn-primary" href="/hubungi/">Hantar bahan untuk semakan</a></div>')

    isi = page_hero([("Utama", "/"), ("Sumber", None)], "Pusat Sumber",
                    "Bahan rujukan klinikal, garis panduan dan bahan pendidikan untuk doktor yang terlibat dalam amalan berkhatan.") + f"""
<section class="content-wrap">
  <div class="shell">
    <div class="form-note"><b>Nota klinikal:</b> bahan di Pusat Sumber MADOCS adalah untuk tujuan pendidikan profesional dan tidak menggantikan penilaian klinikal individu. Setiap bahan klinikal akan disemak oleh penyemak bertauliah sebelum diterbitkan (PRD §21).</div>
    {senarai}
  </div>
</section>"""
    halaman("sumber", "Pusat Sumber | MADOCS",
            "Pusat Sumber MADOCS: rujukan klinikal, garis panduan dan bahan pendidikan untuk doktor dalam amalan berkhatan.",
            "/sumber/", isi)


def bina_cp():
    """Halaman C&P (Credentialing & Privileging) — pintu masuk ke portal iHealth.

    Tahap 1: tiada integrasi data. Halaman menerangkan aliran C&P MADOCS dan
    membawa doktor ke portal iHealth untuk pendaftaran dan log masuk.
    """
    portal = "https://clinic.ihealth.my/cms/"
    isi = page_hero([("Utama", "/"), ("C&P", None)], "Credentialing & Privileging",
                    "Rangka kerja penilaian kecekapan doktor sebelum diberi hak melakukan prosedur berkhatan di sesebuah fasiliti.") + f"""
<section class="content-wrap"><div class="shell">
  <div class="card prose">
    <h2>Apa itu C&amp;P</h2>
    <p>Credentialing ialah proses menyemak kelayakan seorang doktor, iaitu ijazah perubatan, pendaftaran MMC, latihan berkhatan dan rekod log kes. Privileging ialah keputusan memberi hak melakukan prosedur tertentu di fasiliti tertentu, berdasarkan kelayakan yang telah disemak itu.</p>
    <p>Kedua-duanya berasingan daripada keahlian MADOCS. Keahlian ialah hubungan dengan persatuan; C&amp;P ialah penilaian kecekapan klinikal yang membolehkan doktor melakukan prosedur di sesebuah hospital atau klinik.</p>

    <h2>Aliran C&amp;P MADOCS</h2>
    <div class="langkah-cp">
      <div><b>1</b><span>Pendaftaran calon melalui urusetia MADOCS</span></div>
      <div><b>2</b><span>Semakan dokumen: ijazah, pendaftaran MMC dan log kes</span></div>
      <div><b>3</b><span>Penilaian klinikal, peperiksaan teori dan penilaian stesen amali</span></div>
      <div><b>4</b><span>Keputusan Ahli Jawatankuasa C&amp;P</span></div>
      <div><b>5</b><span>Penyenaraian doktor yang privileged dan pembaharuan berkala</span></div>
    </div>

    <h2>Portal iHealth</h2>
    <p>MADOCS menggunakan sistem iHealth untuk pengurusan C&amp;P: pendaftaran calon, muat naik dokumen, jadual penilaian dan rekod keputusan. Calon yang telah mendaftar melalui urusetia akan dihubungi untuk diberikan akses portal.</p>
    <div class="hero-buttons" style="margin-top:18px">
      <a class="btn btn-primary" href="{portal}" target="_blank" rel="noopener">{icon('shield-check')} Log masuk portal iHealth</a>
      <a class="btn btn-outline" href="/hubungi/">{icon('mail')} Hubungi urusetia</a>
    </div>

    <h2>Privasi dan had data</h2>
    <p>Data pesakit, log kes dan logbook calon kekal dalam sistem fasiliti dan pihak berkuasa kesihatan. Laman MADOCS tidak menyimpan data pesakit. Apabila senarai doktor yang telah privileged disahkan untuk diterbitkan, laman ini akan memaparkan nama, negeri dan tarikh sah sahaja.</p>
  </div>
  {kotak_bantuan("Ada pertanyaan tentang C&P?", "Hubungi urusetia keahlian MADOCS untuk pendaftaran calon, dokumen yang diperlukan atau status permohonan.", "Salam, saya ingin bertanya tentang C&P MADOCS.", wa_keahlian_nombor())}
</div></section>

<style>
.langkah-cp{{display:grid;gap:10px;margin:14px 0 22px}}
.langkah-cp>div{{display:grid;grid-template-columns:34px 1fr;align-items:center;gap:12px}}
.langkah-cp b{{display:grid;place-items:center;width:30px;height:30px;border-radius:50%;background:#510716;color:#fff;font-size:13px}}
.langkah-cp span{{font-size:15px}}
</style>"""
    halaman("cp", "Credentialing & Privileging (C&P) | MADOCS",
            "Aliran C&P MADOCS: penilaian kecekapan doktor untuk prosedur berkhatan, dengan pengurusan melalui portal iHealth.",
            "/cp/", isi)


def bina_berita():
    berita = sorted(load("berita.json")["berita"], key=lambda b: b.get("tarikh") or "", reverse=True)
    if berita:
        senarai = '<div class="listing">%s</div>' % "".join(
            item_kandungan(b["tajuk"], "/berita/%s/" % b["slug"], b.get("ringkas", ""),
                           tarikh=b.get("tarikh"), kategori=b.get("kategori", ""), alt=b.get("gambar_alt", ""), gambar=b.get("gambar"))
            for b in berita)
    else:
        kurang("Tiada berita diterbitkan (data/berita.json) — PRD §49.")
        senarai = kosong("file-text", "Belum ada berita diterbitkan",
                         "Pengumuman, berita latihan dan kemas kini profesional MADOCS akan diterbitkan di sini.",
                         '<div style="margin-top:20px"><a class="btn btn-primary" href="/hubungi/">Hubungi urusetia</a></div>')

    isi = page_hero([("Utama", "/"), ("Berita", None)], "Berita & Pengumuman",
                    "Berita terkini, pengumuman dan kemas kini profesional daripada MADOCS.") + f"""
<section class="content-wrap"><div class="shell">{senarai}</div></section>"""
    halaman("berita", "Berita & Pengumuman | MADOCS",
            "Berita, pengumuman dan kemas kini profesional daripada Pertubuhan Doktor Khatan Malaysia (MADOCS).",
            "/berita/", isi)


def bina_berita_detail(b):
    d = parse_date(b.get("tarikh"))
    gambar = ('<img src="/%s" alt="%s" style="width:100%%;border-radius:11px;margin-bottom:22px">'
              % (esc(b["gambar"]), esc(b.get("gambar_alt") or b["tajuk"]))) if b.get("gambar") else ""
    kandungan = "".join("<p>%s</p>" % esc(p) for p in b.get("kandungan", []))
    if not b.get("kandungan"):
        kurang("Kandungan penuh belum diisi untuk berita '%s' (PRD §23)." % b["tajuk"])
        kandungan = '<p class="nota-isi">Kandungan penuh artikel ini belum disediakan.</p>'
    ld = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": b["tajuk"],
          "datePublished": b.get("tarikh", ""), "description": b.get("ringkas", ""),
          "author": {"@type": "Organization", "name": b.get("penulis") or SITE["nama"]},
          "publisher": {"@type": "Organization", "name": SITE["nama"], "logo": {"@type": "ImageObject", "url": BASE + "/assets/logo-128.webp"}},
          "mainEntityOfPage": BASE + "/berita/" + b["slug"] + "/"}
    isi = page_hero([("Utama", "/"), ("Berita", "/berita/"), (b["tajuk"], None)], b["tajuk"],
                    tarikh_pdk(d)) + f"""
<section class="content-wrap">
  <div class="shell split">
    <div class="card">
      {gambar}
      <div class="prose">{kandungan}</div>
      {blok_sumber_berita(b)}
    </div>
    <aside class="side">
      <div class="card">
        <h3>Butiran</h3>
        <div class="item-meta" style="display:grid;gap:9px">
          <time datetime="{esc(b.get('tarikh',''))}">{icon('calendar-days')}{esc(tarikh_pjg(d))}</time>
          <span>{icon('file-text')}{esc(b.get('kategori',''))}</span>
          <span>{icon('users')}{esc(b.get('penulis') or 'Urusetia MADOCS')}</span>
        </div>
        <a class="btn-blok ghost" href="/berita/" style="margin-top:16px">{icon('arrow-left')} Semua berita</a>
      </div>
    </aside>
  </div>
</section>"""
    halaman("berita", tajuk_meta(b["tajuk"], " | Berita MADOCS"),
            ringkas_meta(b.get("ringkas", "")), "/berita/%s/" % b["slug"], isi, og_jenis="article", jsonld=[ld],
            gambar_og=b.get("gambar"))


# ----------------------------------------------------------------- halaman: hubungi
def bina_hubungi():
    endpoint = (SITE.get("borang_endpoint") or "").strip()
    if endpoint:
        buka = '<form class="form" action="%s" method="POST">' % esc(endpoint)
        hantar = '<button class="btn-hantar" type="submit">Hantar mesej %s</button>' % icon("arrow-right")
    else:
        kurang("Borang hubungi belum diaktifkan (site.json → borang_endpoint kosong).")
        buka = '<form class="form" method="get" action="/hubungi/">'
        hantar = ('<a class="btn-hantar" href="mailto:%s?subject=Pertanyaan%%20laman%%20MADOCS">E-MEL URUSETIA %s</a>'
                  % (esc(SITE["email"]), icon("mail")))

    isi = page_hero([("Utama", "/"), ("Hubungi", None)], "Hubungi MADOCS",
                    "Hubungi urusetia MADOCS untuk pertanyaan tentang keahlian, latihan, kerjasama atau sebarang maklumat.") + f"""
<section class="content-wrap">
  <div class="shell split">
    <div>
      <div class="card">
        <h2>Hantar pertanyaan</h2>
        {'<div class="form-note"><b>Hantar pertanyaan melalui e-mel atau WhatsApp urusetia.</b> Butiran di bawah boleh anda salin terus ke dalam e-mel. Kami membalas dalam tempoh dua hari bekerja.</div>' if not endpoint else ''}
        {buka}
          <div class="form-grid">
            <div class="field"><label for="hnama">Nama *</label><input id="hnama" name="nama" required autocomplete="name"></div>
            <div class="field"><label for="hemail">E-mel *</label><input id="hemail" name="email" type="email" required autocomplete="email"></div>
            <div class="field"><label for="htelefon">No. telefon</label><input id="htelefon" name="telefon" autocomplete="tel"></div>
            <div class="field"><label for="htopik">Topik</label>
              <select id="htopik" name="topik">
                <option>Keahlian</option><option>Latihan / kursus</option><option>Pendaftaran kursus</option>
                <option>Sumber klinikal</option><option>Kerjasama / tajaan</option><option>Lain-lain</option>
              </select>
            </div>
            <div class="field penuh"><label for="hmesej">Mesej *</label><textarea id="hmesej" name="mesej" required></textarea></div>
          </div>
          <div style="margin-top:22px">{hantar}</div>
        </form>
      </div>
    </div>
    <aside class="side">
      <div class="card">
        <h3>Urusetia MADOCS</h3>
        <div class="item-meta" style="display:grid;gap:10px">
          <a href="mailto:{esc(SITE['email'])}">{icon('mail')}{esc(SITE['email'])}</a>
          <a href="tel:{esc(SITE['telefon'])}">{icon('phone')}{esc(SITE['telefon_papar'])}</a>
          <span>{icon('map-pin')}{esc(SITE['alamat'])}</span>
          <span>{icon('shield-check')}{esc(SITE['pendaftaran'])}</span>
        </div>
      </div>
      <div class="card kotak-bantuan">
        <h3>Lebih pantas melalui WhatsApp</h3>
        <p>Urusetia MADOCS boleh dihubungi terus melalui WhatsApp pada waktu pejabat.</p>
        <a class="btn-blok wa" href="{wa_pautan(MESEJ_WA_UMUM)}" target="_blank" rel="noopener">{icon('message-circle')} Buka WhatsApp</a>
      </div>
      <div class="card">
        <h3>Keahlian</h3>
        <p style="font-size:14px;line-height:1.7;color:#583c42">Ingin menyertai MADOCS? Mulakan dengan borang permohonan keahlian.</p>
        <a class="btn-blok" href="/keahlian/sertai/" style="margin-top:14px">Borang keahlian {icon('arrow-right')}</a>
      </div>
    </aside>
  </div>
</section>"""
    halaman("hubungi", "Hubungi MADOCS",
            "Hubungi urusetia MADOCS: e-mel, telefon dan borang pertanyaan untuk keahlian, latihan dan kerjasama.",
            "/hubungi/", isi)


# ----------------------------------------------------------------- halaman: carian
def bina_carian():
    isi = page_hero([("Utama", "/"), ("Carian", None)], "Carian",
                    "Cari kursus, aktiviti, berita, sumber dan halaman MADOCS.") + """
<section class="content-wrap">
  <div class="shell">
    <div class="search-bar">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-search" aria-hidden="true"><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.3-4.3"></path></svg>
      <input type="search" id="medan-carian" placeholder="Taip kata kunci…" aria-label="Kata kunci carian" autofocus>
    </div>
    <p class="hasil" id="hasil-info" aria-live="polite"></p>
    <div class="listing" id="hasil-senarai"></div>
  </div>
</section>"""
    halaman("", "Carian | MADOCS", "Cari kandungan laman MADOCS: kursus, aktiviti, berita dan sumber.",
            "/carian/", isi)

    indeks = []
    for k in load("kursus.json")["kursus"]:
        indeks.append({"t": k["tajuk"], "u": "/pendidikan/%s/" % k["slug"], "r": k.get("ringkas", ""), "j": "Kursus"})
    for a in load("aktiviti.json")["aktiviti"]:
        indeks.append({"t": a["tajuk"], "u": "/aktiviti/%s/" % a["slug"], "r": a.get("ringkas", ""), "j": "Aktiviti"})
    for b in load("berita.json")["berita"]:
        indeks.append({"t": b["tajuk"], "u": "/berita/%s/" % b["slug"], "r": b.get("ringkas", ""), "j": "Berita"})
    for s in load("sumber.json")["sumber"]:
        indeks.append({"t": s["tajuk"], "u": s.get("fail") or "/sumber/", "r": s.get("ringkas", ""), "j": "Sumber"})
    indeks += [
        {"t": "Mengenai MADOCS", "u": "/tentang/", "r": "Latar belakang, visi, misi dan jawatankuasa eksekutif.", "j": "Halaman"},
        {"t": "Dari Meja Presiden", "u": "/dari-meja-presiden/", "r": "Perutusan Presiden MADOCS.", "j": "Halaman"},
        {"t": "Pendidikan & Latihan", "u": "/pendidikan/", "r": "Program latihan klinikal berstruktur MADOCS.", "j": "Halaman"},
        {"t": "Keahlian MADOCS", "u": "/keahlian/", "r": "Manfaat, kelayakan, kategori dan yuran keahlian.", "j": "Halaman"},
        {"t": "Borang permohonan keahlian", "u": "/keahlian/sertai/", "r": "Mohon menjadi ahli MADOCS.", "j": "Halaman"},
        {"t": "Aktiviti MADOCS", "u": "/aktiviti/", "r": "Program dan aktiviti yang telah dijalankan.", "j": "Halaman"},
        {"t": "Galeri", "u": "/galeri/", "r": "Album gambar program, kursus dan perhimpunan MADOCS.", "j": "Halaman"},
        {"t": "Pusat Sumber", "u": "/sumber/", "r": "Rujukan klinikal dan bahan pendidikan.", "j": "Halaman"},
        {"t": "Hubungi MADOCS", "u": "/hubungi/", "r": "E-mel, telefon dan borang pertanyaan urusetia.", "j": "Halaman"},
        {"t": "Pernyataan Aksesibiliti", "u": "/kebolehaksesan/", "r": "Komitmen aksesibiliti laman MADOCS dan cara memberi maklum balas.", "j": "Halaman"},
    ]
    (ROOT / "carian").mkdir(exist_ok=True)
    (ROOT / "carian" / "index.json").write_text(json.dumps(indeks, ensure_ascii=False, indent=0), encoding="utf-8")


# ----------------------------------------------------------------- fail statik
def skala_fon(css):
    """Naikkan saiz fon supaya selesa dibaca (Doc mengadu teks 'kecil sangat, sakit mata').

    Reka bentuk yang dicermin daripada laman lama menggunakan saiz amat kecil (8-11px).
    Tiga jalur: teks hiasan (<7px, tagline logo) → 9px; teks kecil (7-11.9px) → sekurang-kurangnya 12px;
    teks sederhana (12-17.9px) → digandakan 1.15. Tajuk (≥18px) dibiarkan supaya susun atur tidak pecah.
    """
    def ganti(m):
        saiz = float(m.group(1))
        if saiz < 7:
            baharu = 9.0
        elif saiz < 12:
            baharu = max(12.0, round(saiz * 1.35))
        elif saiz < 18:
            baharu = round(saiz * 1.15, 1)
        else:
            baharu = saiz
        teks = ("%d" % baharu) if baharu == int(baharu) else ("%.1f" % baharu)
        return "font-size:%spx" % teks
    return re.sub(r"font-size:([\d.]+)px", ganti, css)


def gabung_css():
    """Gabungkan base.css + extra.css. Blok "GAYA A" dalam extra.css dikecualikan daripada
    skala_fon() kerana nilai di dalamnya sudah nilai akhir (dipilih secara visual)."""
    base = _src_css("base.css")
    extra = _src_css("extra.css")
    tanda = extra.find("GAYA A")
    if tanda == -1:
        return skala_fon(base + "\n" + extra)
    potong = extra.rfind("/* ===", 0, tanda)
    if potong == -1:
        potong = tanda
    return skala_fon(base + "\n" + extra[:potong]) + "\n" + extra[potong:]


def bina_fail_statik():
    # CSS gabungan (saiz fon dinaikkan untuk kebolehbacaan, kecuali blok GAYA A)
    (ROOT / "styles.css").write_text(gabung_css(), encoding="utf-8")

    # CSS tambahan kecil untuk carian
    with open(ROOT / "styles.css", "a", encoding="utf-8") as f:
        f.write("\n.ikon-ganti{display:inline-block;width:1em;height:1em}\n")


def blok_statistik_keahlian(kh):
    """Jadual pecahan keahlian daripada daftar jawatankuasa (data/keahlian.json → statistik)."""
    st = kh.get("statistik") or {}
    if not st.get("baris"):
        return ""
    baris = "".join(
        '<div class="%s"><span>%s</span><b>%s</b></div>'
        % ("baris-tebal" if b.get("tebal") else "", esc(b["label"]), esc(b["nilai"]))
        for b in st["baris"])
    return ("""<div class="stat-keahlian">
  <h3>%s</h3>
  %s
  <p class="nota-isi">Sumber: %s.</p>
</div>""" % (esc(st.get("tajuk", "")), baris, esc(st.get("sumber", ""))))



def blok_jawatankuasa(jk_data):
    """Carta organisasi + senarai Jawatankuasa Eksekutif (nama, jawatan, potret).

    Sumber: carta organisasi rasmi MADOCS sesi 2026-2028 yang diserahkan jawatankuasa.
    Potret dipotong daripada carta (resolusi kecil) — ganti dengan gambar asal jika ada.
    """
    jk = jk_data.get("jawatankuasa") or []
    if not jk:
        return ""
    carta = jk_data.get("carta") or {}
    bahagian_carta = ""
    if False and carta.get("gambar"):  # carta gambar disembunyikan (Dr Azfar, Okt 2026)
        bahagian_carta = (
            '<div class="org-carta">'
            '<button class="gambar" type="button" data-besar="/%s" data-kapsyen="%s" aria-label="%s">'
            '<img src="/%s" alt="%s" loading="lazy" decoding="async"></button>'
            '<p class="nota-isi">Klik carta untuk melihat saiz penuh. Sumber: %s.</p></div>'
            % (esc(carta["gambar"]), esc(carta.get("gambar_alt", "")), esc(carta.get("gambar_alt", "")),
               esc(carta["gambar"]), esc(carta.get("gambar_alt", "")), esc(carta.get("sumber", ""))))

    ahli = "".join(
        '<div class="org-ahli">%s<b>%s</b><small>%s</small></div>'
        % ('<span class="org-bulat"><img src="/%s" alt="%s" loading="lazy" decoding="async"></span>'
           % (esc(a["gambar"]), esc(a["nama"])) if a.get("gambar") else "",
           esc(a["nama"]), esc(a.get("jawatan", "")))
        for a in jk)

    penasihat = jk_data.get("penasihat") or []
    blok_penasihat = ""
    if penasihat:
        def _inisial(nama):
            kata = [k for k in nama.replace("(", " ").replace(")", " ").split()
                    if k.lower() not in ("dr", "dr.", "mr", "mr.", "datuk", "hj", "hj.",
                                         "hjh", "prof", "prof.", "tan", "sri", "b")]
            return "".join(k[0].upper() for k in kata[:2]) or "P"

        kad = "".join(
            '<div class="org-ahli">%s<b>%s</b><small>%s</small></div>'
            % ('<span class="org-bulat"><img src="/%s" alt="%s" loading="lazy" decoding="async"></span>'
               % (esc(p["gambar"]), esc(p["nama"])) if p.get("gambar")
               else '<span class="org-bulat org-bulat-kosong" aria-hidden="true">%s</span>' % esc(_inisial(p["nama"])),
               esc(p["nama"]), esc(p.get("jawatan", "Penasihat")))
            for p in penasihat)
        blok_penasihat = ('<h3 class="tajuk-kumpulan">Penasihat</h3>'
                          '<div class="org-grid penasihat">%s</div>' % kad)

    # ---- Susunan berperingkat (Dr Azfar, Okt 2026) ----
    #   Majlis Tinggi : Presiden & Naib Presiden (tengah), kemudian 2 lajur:
    #                   Setiausaha Agung | Bendahari Kehormat, Penolong Setiausaha
    #   Ahli Jawatankuasa : 4 lajur x 2 baris
    def _kad(a, sisi=False, tanpa_jawatan=False):
        bulat = ('<span class="org-bulat"><img src="/%s" alt="%s" loading="lazy" decoding="async"></span>'
                 % (esc(a["gambar"]), esc(a["nama"])) if a.get("gambar") else "")
        jawatan = "" if tanpa_jawatan else esc(a.get("jawatan", ""))
        teks = '<b>%s</b>%s' % (esc(a["nama"]), ('<small>%s</small>' % jawatan) if jawatan else "")
        if sisi:
            return '<div class="org-ahli org-ahli-sisi">%s<span class="org-teks">%s</span></div>' % (bulat, teks)
        return '<div class="org-ahli">%s%s</div>' % (bulat, teks)

    def _cari(jawatan):
        return [a for a in jk if (a.get("jawatan") or "").strip().lower() == jawatan.lower()]

    presiden = _cari("Presiden")
    naib = _cari("Naib Presiden")
    setiausaha = _cari("Setiausaha Agung")
    bendahari = _cari("Bendahari Kehormat")
    penolong = _cari("Penolong Setiausaha")
    ajk = [a for a in jk if (a.get("jawatan") or "").strip().lower() == "ahli jawatankuasa"]

    majlis = ""
    if presiden or naib or setiausaha or bendahari or penolong:
        tengah = "".join(_kad(a, sisi=True) for a in presiden + naib)
        kiri = "".join(_kad(a) for a in setiausaha + penolong)
        kanan = "".join(_kad(a) for a in bendahari)
        majlis = ('<h3 class="tajuk-kumpulan">Majlis Tertinggi</h3>'
                  '<div class="org-tengah">%s</div>'
                  '<div class="org-dua-lajur"><div>%s</div><div>%s</div></div>'
                  % (tengah, kiri, kanan))

    jawatankuasa = ""
    if ajk:
        jawatankuasa = ('<h3 class="tajuk-kumpulan">Ahli Jawatankuasa</h3>'
                        '<div class="org-ajk">%s</div>'
                        % "".join(_kad(a, tanpa_jawatan=True) for a in ajk))

    # Jika ada jawatan lain yang tidak dikenali, jangan hilangkan — letak di hujung.
    dikenali = {"presiden", "naib presiden", "setiausaha agung", "bendahari kehormat",
                "penolong setiausaha", "ahli jawatankuasa"}
    lain = [a for a in jk if (a.get("jawatan") or "").strip().lower() not in dikenali]
    blok_lain = ('<h3 class="tajuk-kumpulan">Lain-lain</h3><div class="org-ajk">%s</div>'
                 % "".join(_kad(a) for a in lain)) if lain else ""

    return bahagian_carta + blok_penasihat + majlis + jawatankuasa + blok_lain



_LEBAR_CACHE = {}


def lebar_imej(laluan: str) -> int:
    """Lebar sebenar fail imej (cache) untuk atribut srcset yang tepat."""
    if laluan not in _LEBAR_CACHE:
        try:
            from PIL import Image
            with Image.open(ROOT / laluan) as im:
                _LEBAR_CACHE[laluan] = im.width
        except Exception:
            _LEBAR_CACHE[laluan] = 1000
    return _LEBAR_CACHE[laluan]


def srcset_galeri(src: str) -> tuple:
    """Pulangkan (src, atribut_srcset) untuk gambar galeri.

    Versi kecil (520 px) dijana oleh alat/bina_thumb_galeri.py. Grid hanya memaparkan
    gambar selebar 300-400 px, jadi menghantar fail 1400 px membazir data pembaca telefon.
    """
    kecil = src[:-5] + "-kecil.webp" if src.endswith(".webp") else None
    if kecil and (ROOT / kecil).exists():
        return kecil, ' srcset="/%s %dw, /%s %dw" sizes="(max-width: 640px) 45vw, (max-width: 1024px) 31vw, 320px"' % (
            esc(kecil), lebar_imej(kecil), esc(src), lebar_imej(src))
    return src, ""


def bina_galeri():
    """Galeri, senarai album + satu halaman setiap album.

    Hanya gambar dewasa dalam konteks kursus/perhimpunan dimasukkan; gambar pesakit
    menerima rawatan atau kanak-kanak memerlukan kebenaran bertulis.
    """
    al = sorted(load("galeri.json").get("album", []), key=lambda a: a.get("tarikh") or "", reverse=True)
    if not al:
        kurang("Galeri kosong (data/galeri.json) — PRD §24.")

    def meta_album(a):
        d = parse_date(a.get("tarikh"))
        return " · ".join(x for x in (tarikh_pdk(d), a.get("tempat", "")) if x)

    # ---- halaman indeks: kad album ----
    kad_album = []
    for a in al:
        g0 = (a.get("gambar") or [{}])[0]
        cover = g0.get("src", "")
        alt = g0.get("alt", a["tajuk"])
        kad_album.append(f"""    <a class="album-kad" href="/galeri/{esc(a["slug"])}/">
      <span class="album-kad-gambar">{'<img src="/%s"%s alt="%s" loading="lazy" decoding="async">' % (esc(srcset_galeri(cover)[0]), esc(srcset_galeri(cover)[1]), esc(alt)) if cover else ''}</span>
      <span class="album-kad-isi">
        <span class="chip">{esc(a.get("kategori", "") or "Album")}</span>
        <b>{esc(a["tajuk"])}</b>
        <small>{esc(meta_album(a))}</small>
        <em>{len(a.get("gambar", []))} gambar</em>
      </span>
    </a>""")

    isi = page_hero([("Utama", "/"), ("Galeri", None)], "Galeri",
                    "Album gambar sebenar program, kursus dan perhimpunan MADOCS.") + f"""
<section class="content-wrap">
  <div class="shell">
    <div class="album-grid">
{chr(10).join(kad_album)}
    </div>
    <p class="nota-isi">Gambar diambil semasa program MADOCS dan diterbitkan untuk tujuan dokumentasi pertubuhan.
    Ibu bapa, penjaga atau peserta yang ingin gambar tertentu dibuang boleh menghubungi urusetia MADOCS.
    Kami akan memadamkannya.</p>
  </div>
</section>"""
    halaman("galeri", "Galeri | MADOCS",
            "Galeri gambar program, kursus dan perhimpunan Pertubuhan Doktor Khatan Malaysia (MADOCS).",
            "/galeri/", isi)

    # ---- satu halaman bagi setiap album ----
    for a in al:
        _kad = []
        for g in a.get("gambar", []):
            _src, _srcset = srcset_galeri(g["src"])
            _kad.append(
                '<button class="gambar" type="button" data-besar="/%s" data-kapsyen="%s" aria-label="%s">'
                '<img src="/%s"%s alt="%s" loading="lazy" decoding="async"></button>'
                % (esc(g["src"]), esc(g["alt"]), esc(g["alt"]), esc(_src), _srcset, esc(g["alt"])))
        kad = "".join(_kad)
        ringkas = esc(a.get("ringkas", ""))
        isi = page_hero([("Utama", "/"), ("Galeri", "/galeri/"), (a["tajuk"], None)], a["tajuk"],
                        meta_album(a) or "Album gambar program MADOCS.") + f"""
<section class="content-wrap">
  <div class="shell">
    {f'<p class="album-ringkas-teks">{ringkas}</p>' if ringkas else ''}
    <div class="galeri">{kad}</div>
    <p class="nota-isi" style="margin-top:18px">Gambar diambil semasa program MADOCS dan diterbitkan untuk tujuan dokumentasi pertubuhan. Ibu bapa, penjaga atau peserta yang ingin gambar tertentu dibuang boleh menghubungi urusetia MADOCS. <a href="/galeri/">Kembali ke semua album</a>.</p>
  </div>
</section>"""
        _n = len(a.get("gambar") or [])
        _meta = meta_album(a) or ""
        _desc = (a.get("ringkas") or "").strip()
        if len(_desc) < 70:
            _desc = ("%s: %d gambar dokumentasi program MADOCS%s. Koleksi galeri rasmi "
                     "Pertubuhan Doktor Khatan Malaysia." %
                     (a["tajuk"], _n, (", " + _meta) if _meta else ""))
        _gambar_album = ((a.get("gambar") or [{}])[0] or {}).get("src")
        halaman("galeri", tajuk_meta(a["tajuk"], " | Galeri MADOCS"), _desc[:165],
                "/galeri/%s/" % a["slug"], isi, gambar_og=_gambar_album)


def bina_peta_sitemap():
    """Tulis robots.txt, sitemap.xml, CNAME dan .nojekyll.

    Dipanggil selepas versi Inggeris dijana supaya laluan /en/ turut disenaraikan.
    """
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % BASE, encoding="utf-8")
    peta = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in sorted(set(PAGES)):
        keutamaan = "1.0" if p in ("/", "/en/") else ("0.8" if p.count("/") <= 2 else "0.6")
        peta.append("  <url><loc>%s%s</loc><priority>%s</priority></url>" % (BASE, p, keutamaan))
    peta.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(peta) + "\n", encoding="utf-8")
    (ROOT / "CNAME").write_text("madocs.my\n", encoding="utf-8")
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")


def _src_css(name):
    return (ROOT / "_src" / name).read_text(encoding="utf-8")


def bina_kebolehaksesan():
    """Pernyataan aksesibiliti (corak RCOG) — ikhlas tentang apa yang sudah dibuat dan apa yang belum."""
    akses_wa = wa_pautan("Salam, saya menghadapi masalah mengakses laman MADOCS:")
    isi = page_hero([("Utama", "/"), ("Pernyataan Aksesibiliti", None)], "Pernyataan Aksesibiliti",
                    "Komitmen MADOCS supaya laman ini boleh digunakan oleh semua pengunjung.") + f"""
<section class="content-wrap">
  <div class="shell split">
    <div>
      <div class="card prose">
        <h2>Komitmen kami</h2>
        <p>MADOCS mahu maklumat tentang pertubuhan, kursus dan keahlian boleh diakses oleh semua orang, termasuk pengguna pembaca skrin, pengguna papan kekunci, dan mereka yang membaca pada telefon dengan teks besar. Kami merujuk garis panduan <b>WCAG 2.2 tahap AA</b> sebagai sasaran, dan memperbaiki laman secara berperingkat.</p>

        <h2>Apa yang telah kami lakukan</h2>
        <ul>
          <li>Struktur tajuk yang tersusun dan teks alternatif bagi setiap gambar.</li>
          <li>Pautan "lompat ke kandungan utama" pada setiap halaman dan keadaan fokus papan kekunci yang jelas.</li>
          <li>Saiz teks sekurang-kurangnya 12px (kebanyakan teks badan 15-17px) dengan kontras warna yang tinggi.</li>
          <li>Semua gerakan (peralihan halaman, animasi skrol) dimatikan secara automatik apabila peranti pengguna menetapkan "kurang gerakan".</li>
          <li>Laman dwibahasa (Bahasa Melayu dan Inggeris) dengan pemilih bahasa pada setiap halaman.</li>
          <li>Sasaran sentuh sekurang-kurangnya 44px untuk butang dan pautan utama pada telefon.</li>
        </ul>

        <h2>Apa yang masih belum sempurna</h2>
        <ul>
          <li>Sebahagian imej masih merupakan <b>imej ilustrasi</b> (dilabel "Imej ilustrasi") menunggu gambar sebenar daripada jawatankuasa.</li>
          <li>Kandungan yang belum disediakan (angka, jawatankuasa, bahan Pusat Sumber) dipaparkan sebagai "Sedang disediakan". Kami sengaja tidak mengisi ruang itu dengan teks contoh.</li>
          <li>Muat turun fail (PDF) dalam Pusat Sumber belum diuji dengan pembaca skrin untuk semua pembaca PDF.</li>
        </ul>

        <h2>Beritahu kami jika ada halangan</h2>
        <p>Jika anda menghadapi masalah mengakses mana-mana bahagian laman ini, seperti teks yang tidak boleh dibaca, butang yang sukar ditekan, atau maklumat yang hilang, hubungi urusetia kami. Kami akan cuba membetulkannya dan memberi jawapan dalam masa munasabah (biasanya dalam tiga hari bekerja).</p>
        <p>E-mel: <a href="mailto:{esc(SITE['email'])}">{esc(SITE['email'])}</a> &middot;
        Telefon: <a href="tel:{esc(SITE['telefon'])}">{esc(SITE['telefon_papar'])}</a></p>
        <p class="nota-isi">Pernyataan ini dikemas kini pada Oktober 2026 dan akan disemak semula apabila laman
        ditambah ciri baharu.</p>
      </div>
    </div>
    <aside class="side">
      {kotak_bantuan("Ada halangan akses?", "Hantar kepada urusetia butiran halaman dan masalah yang anda hadapi.", "Salam, saya menghadapi masalah mengakses laman MADOCS:")}
      <div class="card">
        <h3>Pintasan</h3>
        <nav class="side-nav">
          <a href="/dasar-privasi/">Dasar Privasi</a>
          <a href="/terma/">Terma Penggunaan</a>
          <a href="/hubungi/">Hubungi urusetia</a>
        </nav>
      </div>
    </aside>
  </div>
</section>"""
    halaman("", "Pernyataan Aksesibiliti | MADOCS",
            "Pernyataan aksesibiliti laman MADOCS: sasaran WCAG 2.2 AA, apa yang telah dibuat dan cara memberi maklum balas.",
            "/kebolehaksesan/", isi)


def bina_404():
    isi = page_hero([("Utama", "/"), ("Halaman tidak dijumpai", None)], "404: Halaman tidak dijumpai",
                    "Maaf, halaman yang anda cari tidak wujud atau telah berpindah.") + """
<section class="content-wrap">
  <div class="shell split lebar">
    <div class="kosong">
      <span class="ikon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-search" aria-hidden="true"><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.3-4.3"></path></svg></span>
      <h3>Halaman tidak dijumpai</h3>
      <p>Semak pautan anda, atau gunakan carian dan navigasi di bawah untuk mencari kandungan yang anda perlukan.</p>
      <div style="margin-top:22px;display:flex;gap:10px;justify-content:center;flex-wrap:wrap">
        <a class="btn btn-primary" href="/">Ke laman utama</a>
        <a class="btn btn-outline" href="/carian/">Cari kandungan</a>
        <a class="btn btn-outline" href="/hubungi/">Hubungi kami</a>
      </div>
    </div>
  </div>
</section>"""
    halaman("", "404: Halaman tidak dijumpai | MADOCS",
            "Halaman yang anda cari tidak dijumpai. Kembali ke laman utama MADOCS atau gunakan carian untuk mencari maklumat yang anda perlukan.", "/404.html", isi, masuk_sitemap=False)


def bina_prakata():
    """Halaman 'Dari Meja Presiden' — kandungan dalam data/prakata.json (draf untuk Presiden)."""
    p = load("prakata.json")
    tunjang = "".join('<li>%s</li>' % esc(t) for t in p.get("tunjang") or [])
    perenggan = "".join("<p>%s</p>" % esc(x) for x in p.get("perenggan") or [])

    isi = page_hero([("Utama", "/"), ("Dari Meja Presiden", None)], p["tajuk"],
                    "Perutusan Presiden MADOCS.") + f"""
<section class="content-wrap">
  <div class="shell split-presiden">
    <aside>
      <div class="card kad-presiden">
        <div class="bulat-presiden"><img src="/{esc(p['gambar'])}" alt="{esc(p['gambar_alt'])}"
             loading="eager" decoding="async"></div>
        <h3>{esc(p['nama'])}</h3>
        <span class="pil-presiden">{esc(p['label'])}</span>
        <p class="jawatan">{esc(p['jawatan'])}</p>
        <p class="organisasi">{esc(p['organisasi'])}</p>
        {f'<ul class="tunjang">{tunjang}</ul>' if tunjang else ''}
      </div>
    </aside>
    <div>
      <div class="card prose prakata">
        <p class="salam">{esc(p['salam'])}</p>
        {perenggan}
        <p class="penutup">{esc(p['penutup'])}</p>
        <div class="tandatangan-prakata">
          <div class="nm">{esc(p['nama'])}</div>
          <div class="jw">{esc(p['label'])}, {esc(p['organisasi'])}</div>
          <div class="tarikh-prakata">{esc(p['tarikh'])}</div>
        </div>
      </div>
      <div class="card nota-prakata">
        <h3>{esc(p['kotak_tajuk'])}</h3>
        <p>{esc(p['kotak'])}</p>
      </div>
    </div>
  </div>
</section>"""
    halaman("tentang", "%s | MADOCS" % p["tajuk"],
            "Dari Meja Presiden: perutusan daripada Presiden Pertubuhan Doktor Khatan Malaysia (MADOCS), Dr. Abdol Rashid bin Masrom.",
            "/dari-meja-presiden/", isi)


def bina_dasar():
    laman_ringkas("dasar-privasi", "Dasar Privasi", f"""
<p>{esc(SITE['nama'])} ({esc(SITE['singkatan'])}) mengumpul maklumat peribadi yang dihantar secara sukarela melalui laman ini, contohnya melalui borang permohonan keahlian, pendaftaran kursus atau borang pertanyaan.</p>
<h2>Maklumat yang dikumpul</h2>
<ul><li>Maklumat hubungan (nama, e-mel, nombor telefon).</li><li>Maklumat profesional (nombor pendaftaran MMC, tempat praktis, negeri).</li><li>Maklumat permohonan keahlian: nombor kad pengenalan, tarikh lahir, alamat rumah dan pejabat, bangsa serta agama.</li><li>Maklumat yang anda taip dalam mesej atau permohonan.</li></ul>
<h2>Kegunaan maklumat</h2>
<p>Maklumat digunakan semata-mata untuk memproses keahlian, pendaftaran program latihan, pertanyaan dan komunikasi berkaitan aktiviti MADOCS.</p>
<p>Bangsa dan agama dikumpul untuk rekod keahlian dan statistik persatuan sahaja, dan tidak digunakan sebagai syarat kelulusan keahlian. Kerana agama termasuk data peribadi sensitif di bawah Akta Perlindungan Data Peribadi 2010, persetujuan nyata diminta pada borang permohonan sebelum data dihantar.</p>
<h2>Perkongsian</h2>
<p>Maklumat peribadi tidak dijual atau dikongsi dengan pihak ketiga untuk tujuan pemasaran. Nama ahli dan maklumat peribadi tidak diterbitkan di laman awam.</p>
<h2>Penyimpanan</h2>
<p>Maklumat disimpan setakat yang diperlukan untuk tujuan di atas dan dilindungi mengikut amalan pentadbiran yang munasabah.</p>
<h2>Hubungi kami</h2>
<p>Untuk permintaan akses, pembetulan atau penghapusan data, hubungi <a href="mailto:{esc(SITE['email'])}">{esc(SITE['email'])}</a>.</p>
<p class="nota-isi">Dasar ini disemak dari semasa ke semasa dan dikemas kini mengikut keperluan perundangan yang berkuat kuasa, termasuk Akta Perlindungan Data Peribadi 2010 (pindaan 2024).</p>
""")
    laman_ringkas("terma", "Terma Penggunaan", f"""
<p>Dengan menggunakan laman ini, anda bersetuju dengan terma berikut.</p>
<h2>Kandungan</h2>
<p>Kandungan laman ini adalah untuk tujuan maklumat dan pendidikan profesional. Ia tidak menggantikan penilaian, nasihat atau keputusan klinikal individu oleh pengamal yang bertauliah.</p>
<h2>Ketepatan maklumat</h2>
<p>MADOCS berusaha memastikan maklumat di laman ini tepat dan terkini. Maklumat seperti jadual latihan, yuran dan keahlian boleh berubah dan akan dikemas kini dari semasa ke semasa.</p>
<h2>Hak cipta</h2>
<p>Nama, logo dan kandungan MADOCS tidak boleh digunakan semula untuk tujuan komersial tanpa kebenaran bertulis.</p>
<h2>Pautan luar</h2>
<p>Pautan ke laman pihak ketiga disediakan untuk kemudahan. MADOCS tidak bertanggungjawab ke atas kandungan laman tersebut.</p>
""")


# ----------------------------------------------------------------- utama
def cap_versi():
    """Tambah cap versi (?v=<hash>) pada pautan styles.css dan app.js.

    GitHub Pages menghidangkan HTML/CSS dengan `cache-control: max-age=600`, jadi pelawat
    boleh nampak versi lama sehingga 10 minit selepas terbitan. Dengan cap berasaskan
    kandungan fail, setiap terbitan menghasilkan URL baharu dan pelayar terus mengambil
    versi terbaharu.
    """
    import hashlib
    cap = hashlib.md5()
    for nama in ("styles.css", "app.js"):
        f = ROOT / nama
        if f.exists():
            cap.update(f.read_bytes())
    tanda = cap.hexdigest()[:8]
    pola = re.compile(r'(/styles\.css|/app\.js)(\?v=[0-9a-f]+)?')
    bil = 0
    for f in ROOT.rglob("*.html"):
        if ".git" in f.parts:
            continue
        teks = f.read_text(encoding="utf-8")
        baharu = pola.sub(lambda m: "%s?v=%s" % (m.group(1), tanda), teks)
        if baharu != teks:
            f.write_text(baharu, encoding="utf-8")
            bil += 1
    # Cap per-aset imej: URL imej berubah apabila fail imej berubah.
    # Penting kerana GitHub Pages mengecualikan imej daripada revalidasi (max-age=600):
    # tanpa cap, telefon boleh memaparkan gambar LAMA walaupun HTML sudah baharu.
    cap_imej = re.compile(r'(/(?:assets/|favicon|apple-touch-icon)[^"\'\s>]*?\.(?:webp|png|jpe?g|svg|ico))(\?v=[0-9a-f]+)?')
    cap_imej_data = re.compile(r'(data-srcset?=")(/[^"?]+)(\?v=[0-9a-f]+)?(")')
    jadual = {}
    for f in ROOT.rglob("*.html"):
        if ".git" in f.parts:
            continue
        teks_fail = f.read_text(encoding="utf-8")
        for laluan in set(cap_imej.findall(teks_fail)) | set(
                (m2.group(2),) for m2 in cap_imej_data.finditer(teks_fail)):
            laluan = laluan[0] if isinstance(laluan, tuple) else laluan
            fail = ROOT / laluan.lstrip("/")
            if laluan not in jadual and fail.exists():
                jadual[laluan] = hashlib.md5(fail.read_bytes()).hexdigest()[:8]
    bil_imej = 0
    for f in ROOT.rglob("*.html"):
        if ".git" in f.parts:
            continue
        teks = f.read_text(encoding="utf-8")
        baharu = cap_imej.sub(
            lambda m: "%s?v=%s" % (m.group(1), jadual.get(m.group(1), tanda)), teks)
        baharu = cap_imej_data.sub(
            lambda m: "%s%s?v=%s%s" % (m.group(1), m.group(2), jadual.get(m.group(2), tanda), m.group(4)), baharu)
        if baharu != teks:
            f.write_text(baharu, encoding="utf-8")
            bil_imej += 1
    print("Cap versi %s digunakan pada %d fail HTML." % (tanda, bil))
    print("Cap imej (per-fail) digunakan pada %d fail HTML (%d aset)." % (bil_imej, len(jadual)))


SEKSYEN_SLUG = ("aktiviti", "berita", "pendidikan", "sumber", "kursus", "galeri", "en")


def bersih_halaman_sisa():
    """Buang direktori halaman slug yang tidak lagi dijana.

    Contoh: slug aktiviti bertukar (pcc3-putrajaya -> 2026-05-30-pcc2-3-putrajaya).
    Tanpa langkah ini, halaman lama kekal di repo dan terus boleh diakses pelawat
    dengan maklumat yang sudah usang.
    """
    dibuang = []
    for f in ROOT.rglob("index.html"):
        if ".git" in f.parts:
            continue
        if f.resolve() in DIJANA:
            continue
        folder = f.parent
        if folder == ROOT:
            continue          # jangan sentuh laman utama
        shutil.rmtree(folder, ignore_errors=True)
        dibuang.append(str(folder.relative_to(ROOT)))
    for sisa in sorted(dibuang, reverse=True):
        print("  halaman sisa dibuang:", sisa)
    return dibuang


def main():
    bina_fail_statik()
    bina_utama()
    bina_tentang()
    bina_organisasi()
    bina_pendidikan()
    for k in load("kursus.json")["kursus"]:
        bina_kursus_detail(k)
    bina_keahlian()
    bina_semak_ahli()
    bina_sertai()
    bina_aktiviti()
    bina_galeri()
    for a in load("aktiviti.json")["aktiviti"]:
        bina_aktiviti_detail(a)
    bina_sumber()
    bina_cp()
    bina_berita()
    for b in load("berita.json")["berita"]:
        bina_berita_detail(b)
    bina_hubungi()
    bina_carian()
    bina_prakata()
    bina_kebolehaksesan()
    bina_sahkan()

    bina_dasar()
    bina_404()

    bina_bahasa_inggeris()
    bina_peta_sitemap()
    bersih_halaman_sisa()
    cap_versi()

    if "--report" in sys.argv:
        print("\n=== KANDUNGAN YANG MASIH DIPERLUKAN (%d) ===" % len(KURANG))
        for i, k in enumerate(sorted(set(KURANG)), 1):
            print("%2d. %s" % (i, k))
    print("\nSelesai: %d halaman dibina." % len(PAGES))


if __name__ == "__main__":
    main()
