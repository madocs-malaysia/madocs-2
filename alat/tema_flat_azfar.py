#!/usr/bin/env python3
"""Kemas kini tema (Okt 2026, permintaan Dr Azfar):
1. Font: betulkan `var(--font-geist)` yang tidak tertakrif (menyebabkan Times New Roman di seluruh laman).
2. Logo: jangan paksa kotak 55x55 — tinggi tetap, lebar ikut nisbah.
3. Ikon: ganti gaya 3D/cembung dengan ikon rata (flat).
4. Tile manfaat: ikon di kiri, teks di kanan.
5. Ejaan: "Abdul Rashid" -> "Abdol Rashid".
"""
import json
import pathlib
import re

ROOT = pathlib.Path("/home/ubuntu/madocs-site")

# ---------------------------------------------------------------- 1. font + 2. logo
base_p = ROOT / "_src/base.css"
base = base_p.read_text(encoding="utf-8")

lama_font = "font-family:var(--font-geist), Arial, sans-serif"
baharu_font = ('font-family:"Segoe UI",system-ui,-apple-system,"Helvetica Neue",'
               'Arial,"Liberation Sans",sans-serif')
assert base.count(lama_font) == 1, base.count(lama_font)
base = base.replace(lama_font, baharu_font)

lama_logo = ".logo img{object-fit:contain;width:55px;height:55px}"
baharu_logo = ".logo img{object-fit:contain;height:55px;width:auto;max-width:60px}"
assert base.count(lama_logo) == 1
base = base.replace(lama_logo, baharu_logo)

lama_logo_m = ".logo img{width:43px;height:43px}"
baharu_logo_m = ".logo img{height:43px;width:auto;max-width:48px}"
assert base.count(lama_logo_m) == 1
base = base.replace(lama_logo_m, baharu_logo_m)
base_p.write_text(base, encoding="utf-8")

# ---------------------------------------------------------------- 3 + 4. ikon rata & tile
extra_p = ROOT / "_src/extra.css"
extra = extra_p.read_text(encoding="utf-8")

mula = extra.find("/* --- Ikon sosial 3D")
tamat = extra.find("/* --- Kredit foto pihak ketiga")
assert mula != -1 and tamat > mula, (mula, tamat)

ganti = '''/* ================= IKON RATA (flat) =================
   Ganti gaya 3D/cembung lama (gradien bola berkilat + bayang dalam) yang Doc kata
   nampak kuno. Gaya baharu: bulatan rata, satu warna, tanpa gradien, tanpa bayang. */

footer .socials a{
  display:grid;
  place-items:center;
  padding:0;
  background:#ffffff1f;
  border:0;
  box-shadow:none;
  color:#fff;
  transition:background .15s ease;
}
footer .socials a svg{filter:none}
footer .socials a:hover{background:#ffffff38}
footer .socials a:active{background:#ffffff14}
@media (prefers-reduced-motion:reduce){footer .socials a{transition:none}}

/* Jalur gelap: bulatan garis nipis, ikon putih rata */
.credential-grid>div>span,
.cta-icon{
  border:1.5px solid #ffffff80;
  background:transparent;
  box-shadow:none;
  transition:none;
}
.credential-grid svg,.cta-icon svg{filter:none}
.cta-icon{color:#fff}

/* Latar terang: bulatan warna lembut, ikon warna jenama rata */
.service-grid article>span,
.tile>span.ikon,
.modal .close,
.success>span,
.kosong span.ikon{
  border:0;
  background:var(--pale);
  color:var(--blue);
  box-shadow:none;
  transition:background .15s ease;
}
.stat>span{
  border:1px solid #f6d9df;
  background:#fff;
  color:var(--blue);
  box-shadow:none;
}
.service-grid svg,.stat svg,.tile>span.ikon svg,.kosong span.ikon svg{filter:none}

.carousel-arrow{
  background:#fff;
  border:1px solid var(--line);
  color:var(--navy);
  box-shadow:none;
}
.carousel-arrow:hover{background:var(--pale);color:var(--blue)}

/* Kesan sentuh: tiada bayang, hanya warna */
footer .socials a:hover,.tile:hover>span.ikon{transform:none}

/* --- Tile manfaat: ikon di kiri, teks di kanan (Doc, Okt 2026) --- */
.tile-manfaat{
  display:grid;
  grid-template-columns:auto 1fr;
  align-items:center;
  gap:14px;
}
.tile-manfaat>span.ikon{margin:0;flex:none}
.tile-manfaat h3{margin:0}

'''
extra = extra[:mula] + ganti + extra[tamat:]
extra_p.write_text(extra, encoding="utf-8")
print("extra.css: blok ikon diganti (%d -> %d aksara)" % (tamat - mula, len(ganti)))

# ---------------------------------------------------------------- 5. Abdol Rashid
berita_p = ROOT / "data/berita.json"
berita_raw = berita_p.read_text(encoding="utf-8")
n = berita_raw.count("Abdul Rashid")
berita_raw = berita_raw.replace("Abdul Rashid", "Abdol Rashid")
berita_p.write_text(berita_raw, encoding="utf-8")

terj_p = ROOT / "data/terjemahan.json"
terj = json.loads(terj_p.read_text(encoding="utf-8"))
baharu = {}
tukar = 0
for k, v in terj.items():
    k2 = k.replace("Abdul Rashid", "Abdol Rashid")
    v2 = v.replace("Abdul Rashid", "Abdol Rashid")
    if (k2, v2) != (k, v):
        tukar += 1
    baharu[k2] = v2
teks = json.dumps({k: baharu[k] for k in sorted(baharu)}, ensure_ascii=False, indent=1)
terj_p.write_text(teks if teks.endswith("\n") else teks + "\n", encoding="utf-8")

print("berita.json: %d ganti; terjemahan.json: %d entri dikemas kini" % (n, tukar))
