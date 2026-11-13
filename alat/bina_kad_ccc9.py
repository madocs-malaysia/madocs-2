#!/usr/bin/env python3
"""Kad hero promosi CCC 9 — direka penuh (bukan poster ditampal atas latar kabur).

Keluaran (dua saiz sepadan kotak hero sebenar):
  assets/hero/berita-2026-11-13-ccc9-pendaftaran-dibuka-besar.webp    1400x1015
  assets/hero/berita-2026-11-13-ccc9-pendaftaran-dibuka-telefon.webp   720x640

Cara guna:
  python3 alat/bina_kad_ccc9.py            # tulis /tmp/kad/ccc9-*.html
  (tangkap skrin melalui pelayar -> /tmp/kad/ccc9-*.png)
  python3 alat/bina_kad_ccc9.py --pasang   # PNG -> webp dalam repo
"""
import os
import shutil
import sys

from PIL import Image

AKAR = "/home/ubuntu/madocs-site"
TMP = "/tmp/kad"
FON = os.path.join(AKAR, "alat", "fon")
SAIZ = {"besar": (1400, 1015), "telefon": (720, 640)}


def css_besar(w, h):
    return f"""
@font-face{{font-family:'Jost';src:url('fon/jost.ttf') format('truetype');font-weight:300 800}}
@font-face{{font-family:'PD';src:url('fon/pd.ttf') format('truetype')}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{w}px;height:{h}px;overflow:hidden;font-family:'Jost',sans-serif}}
.kad{{position:relative;width:{w}px;height:{h}px;overflow:hidden;background:#3d0410}}
.latar{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
  filter:saturate(.55) brightness(.42) contrast(1.05)}}
.tirai{{position:absolute;inset:0;background:
  radial-gradient(120% 100% at 78% 45%, #5a071b00 0%, #3a0410cc 62%, #2a0209f2 100%),
  linear-gradient(100deg,#2a0209 0%,#4a0514d9 42%,#5e091a99 62%,#2a0209e6 100%)}}
.garis{{position:absolute;inset:0;opacity:.16;
  background-image:repeating-linear-gradient(115deg,#ffcf8a 0 1px,#0000 1px 46px)}}
.sembilan{{position:absolute;right:-60px;top:-190px;font-family:'Jost';font-weight:700;
  font-size:900px;line-height:1;color:#ffd08a;opacity:.075;letter-spacing:-.04em}}
.blok{{position:absolute;left:636px;top:50%;transform:translateY(-50%);width:646px}}
.logo{{display:flex;align-items:center;gap:14px;margin-bottom:34px}}
.logo img{{width:62px;height:62px;object-fit:contain;filter:drop-shadow(0 4px 12px #0007)}}
.logo div{{display:flex;flex-direction:column;gap:3px}}
.logo b{{font-size:19px;font-weight:600;letter-spacing:.18em;color:#ffe6c9;text-transform:uppercase}}
.logo span{{font-size:13px;letter-spacing:.09em;color:#e9b9a8;text-transform:uppercase}}
.kicker{{display:inline-flex;align-items:center;gap:12px;font-size:19px;font-weight:600;
  letter-spacing:.24em;text-transform:uppercase;color:#ffc46b;margin-bottom:16px}}
.kicker:before{{content:'';width:46px;height:2px;background:#ffc46b;display:block}}
.tajuk{{font-family:'Jost';font-weight:700;font-size:154px;line-height:.86;letter-spacing:-.035em;
  color:#fff;text-shadow:0 10px 40px #1c0009cc}}
.sub{{font-weight:300;font-size:33px;line-height:1.24;color:#ffd9c4;margin-top:14px;letter-spacing:.005em}}
.rule{{width:250px;height:2px;background:linear-gradient(90deg,#ffcf8a,#ffcf8a00);margin:26px 0 24px}}
.baris{{display:flex;flex-direction:column;gap:12px;margin-bottom:26px}}
.baris p{{display:flex;align-items:center;gap:12px;font-size:23px;color:#fbe7de;font-weight:300}}
.dot{{width:9px;height:9px;border-radius:50%;background:#ffc46b;flex:none;box-shadow:0 0 0 5px #ffc46b22}}
.kaedah{{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:28px;max-width:600px}}
.kaedah span{{border:1px solid #ffcf8a66;background:#ffffff10;border-radius:999px;
  padding:9px 17px;font-size:16px;letter-spacing:.05em;color:#ffe9d2;font-weight:400}}
.yuran{{display:flex;align-items:flex-end;gap:20px}}
.yuran b{{font-size:21px;font-weight:400;color:#e8b49f;letter-spacing:.04em}}
.yuran strong{{font-family:'Jost';font-size:46px;font-weight:600;color:#ffc46b;line-height:1}}
.yuran small{{font-size:16px;color:#e8b49f;margin-bottom:5px}}
"""


def css_telefon(w, h):
    return f"""
@font-face{{font-family:'Jost';src:url('fon/jost.ttf') format('truetype');font-weight:300 800}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{w}px;height:{h}px;overflow:hidden;font-family:'Jost',sans-serif}}
.kad{{position:relative;width:{w}px;height:{h}px;overflow:hidden;background:#3d0410}}
.latar{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
  filter:saturate(.5) brightness(.4)}}
.tirai{{position:absolute;inset:0;background:
  radial-gradient(120% 90% at 70% 30%, #6a0a1f00 0%, #3a0410e0 58%, #260208f7 100%),
  linear-gradient(160deg,#2a0209f2,#4a0514cc 60%,#5e091acc)}}
.garis{{position:absolute;inset:0;opacity:.14;
  background-image:repeating-linear-gradient(115deg,#ffcf8a 0 1px,#0000 1px 34px)}}
.blok{{position:absolute;left:44px;top:41%;transform:translateY(-50%);width:632px}}
.logo{{display:flex;align-items:center;gap:10px;margin-bottom:20px}}
.logo img{{width:62px;height:62px;object-fit:contain}}
.logo b{{font-size:20px;font-weight:600;letter-spacing:.16em;color:#ffe6c9}}
.kicker{{display:inline-flex;align-items:center;gap:11px;font-size:20px;font-weight:600;
  letter-spacing:.2em;text-transform:uppercase;color:#ffc46b;margin-bottom:12px}}
.kicker:before{{content:'';width:42px;height:3px;background:#ffc46b;display:block}}
.tajuk{{font-family:'Jost';font-weight:700;font-size:142px;line-height:.82;letter-spacing:-.04em;color:#fff}}
.sub{{font-weight:300;font-size:29px;line-height:1.2;color:#ffd9c4;margin-top:9px}}
.rule{{width:220px;height:3px;background:linear-gradient(90deg,#ffcf8a,#ffcf8a00);margin:20px 0 16px}}
.baris{{display:flex;flex-direction:column;gap:9px;margin-bottom:16px}}
.baris p{{display:flex;align-items:center;gap:10px;font-size:21px;color:#fbe7de;font-weight:300}}
.dot{{width:8px;height:8px;border-radius:50%;background:#ffc46b;flex:none}}
.kaedah{{display:flex;flex-wrap:wrap;gap:9px;margin-bottom:18px;max-width:620px}}
.kaedah span{{border:1px solid #ffcf8a55;background:#ffffff12;border-radius:999px;
  padding:9px 16px;font-size:19px;color:#ffe9d2}}
.yuran{{display:flex;align-items:flex-end;gap:12px}}
.yuran b{{font-size:21px;font-weight:400;color:#e8b49f}}
.yuran strong{{font-size:46px;font-weight:600;color:#ffc46b;line-height:1}}
.yuran small{{font-size:16px;color:#e8b49f;margin-bottom:4px}}
"""


def html(nama):
    w, h = SAIZ[nama]
    css = css_besar(w, h) if nama == "besar" else css_telefon(w, h)
    if nama == "besar":
        logo_txt = "<b>MADOCS</b><span>Malaysian Doctors of Circumcision Society</span>"
    else:
        logo_txt = "<b>MADOCS</b>"
    return f"""<!doctype html><html lang="ms"><head><meta charset="utf-8">
<title>CCC 9 hero — {nama}</title><style>{css}</style></head><body>
<div class="kad">
  <img class="latar" src="{AKAR}/assets/kursus-ccc9-dewan.webp" alt="">
  <div class="garis"></div>
  <div class="tirai"></div>
  {f'<div class="sembilan">9</div>' if nama == 'besar' else ''}
  <div class="blok">
    <div class="logo"><img src="{AKAR}/assets/logo-192.webp" alt="MADOCS"><div>{logo_txt}</div></div>
    <div class="kicker">Pendaftaran dibuka</div>
    <div class="tajuk">CCC 9</div>
    <div class="sub">Comprehensive Circumcision Course</div>
    <div class="rule"></div>
    <div class="baris">
      <p><span class="dot"></span>Ahad, 13 Disember 2026 · 8.00 pagi – 5.00 petang</p>
      <p><span class="dot"></span>Masjid Saidina Uthman Ibn Affan, Bandar Tun Razak</p>
    </div>
    <div class="kaedah"><span>Forceps-guided</span><span>Smart Clamp</span><span>Tekno Klem</span><span>ZSR Stapler</span></div>
    <div class="yuran"><b>Yuran dari</b><strong>RM900</strong><small>· 10 tempat setiap kaedah</small></div>
  </div>
</div></body></html>"""


def tulis():
    os.makedirs(os.path.join(TMP, "fon"), exist_ok=True)
    for f in ("pd.ttf", "jost.ttf"):
        asal = os.path.join(FON, f)
        sementara = os.path.join(TMP, "fon", f)
        if os.path.exists(asal) and not os.path.exists(sementara):
            shutil.copy(asal, sementara)
    for nama in SAIZ:
        p = os.path.join(TMP, "ccc9-%s.html" % nama)
        with open(p, "w", encoding="utf-8") as f:
            f.write(html(nama))
        print("tulis", p)


def pasang():
    for nama, saiz in SAIZ.items():
        src = os.path.join(TMP, "ccc9-%s.png" % nama)
        if not os.path.exists(src):
            print("TIADA", src)
            continue
        im = Image.open(src).convert("RGB")
        if im.size != saiz:
            im = im.resize(saiz, Image.LANCZOS)
        out = os.path.join(AKAR, "assets", "hero",
                           "berita-2026-11-13-ccc9-pendaftaran-dibuka-%s.webp" % nama)
        im.save(out, "WEBP", quality=88, method=6)
        print("pasang %-70s %s %d KB" % (out, im.size, os.path.getsize(out) // 1024))


if __name__ == "__main__":
    if "--pasang" in sys.argv:
        pasang()
    else:
        tulis()
