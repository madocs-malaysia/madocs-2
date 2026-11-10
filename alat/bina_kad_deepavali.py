#!/usr/bin/env python3
"""Hasilkan kad ucapan Deepavali sebagai imej PENUH (bukan poster menegak ditampal
atas latar kabur seperti kad lama — itulah yang buatkan kad nampak kecil dan
terpotong pada telefon).

Dua saiz, sepadan dengan kotak hero sebenar:
  assets/hero/ucapan-deepavali-besar.webp    1400x1015  (hero desktop)
  assets/hero/ucapan-deepavali-telefon.webp   720x640   (hero telefon)

Cara guna:
  python3 alat/bina_kad_deepavali.py           # tulis /tmp/kad/kad-*.html
  (tangkap skrin 2x melalui pelayar -> /tmp/kad/kad-*.png)
  python3 alat/bina_kad_deepavali.py --pasang  # PNG 2x -> webp dalam repo
"""
import math
import os
import sys

from PIL import Image

AKAR = '/home/ubuntu/madocs-site'
TMP = '/tmp/kad'
FON = os.path.join(AKAR, 'alat', 'fon')
SAIZ = {'besar': (1400, 1015), 'telefon': (720, 640)}

TEKS = {
    'happy': 'HAPPY',
    'tajuk': 'Deepavali',
    'sub': 'Wishing you and your family<br>a bright and joyous Deepavali',
    'dari_b': 'From President',
    'dari_s': 'Malaysian Doctors of Circumcision Society (MADOCS)',
}


def petal(panjang, lebar):
    return ('M0,0 C %.1f,-%.1f %.1f,-%.1f 0,-%.1f C -%.1f,-%.1f -%.1f,-%.1f 0,0 Z'
            % (lebar, panjang * .34, lebar, panjang * .70, panjang,
               lebar, panjang * .70, lebar, panjang * .34))


def mandala(r, warna='#ffcf5a'):
    """Kolam/mandala: cincin kelopak + titik + gerbang, satu warna garis emas."""
    g = []
    # titik terluar
    for i in range(48):
        a = 2 * math.pi * i / 48
        g.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" opacity=".55"/>'
                 % (r * .97 * math.sin(a), -r * .97 * math.cos(a), r * .012, warna))
    # cincin kelopak besar
    for i in range(16):
        a = 360 * i / 16
        g.append('<path d="%s" transform="rotate(%.1f) translate(0,-%.1f)" fill="none" '
                 'stroke="%s" stroke-width="%.1f" opacity=".5"/>'
                 % (petal(r * .30, r * .085), a, r * .62, warna, max(1.3, r * .009)))
    # gerbang kecil antara kelopak
    for i in range(16):
        a = 360 * i / 16 + 11.25
        g.append('<path d="M %.1f,0 A %.1f,%.1f 0 0 1 %.1f,0" transform="rotate(%.1f) translate(0,-%.1f)" '
                 'fill="none" stroke="%s" stroke-width="%.1f" opacity=".38"/>'
                 % (-r * .07, r * .07, r * .07, r * .07, a, r * .90, warna, max(1.2, r * .008)))
    # cincin kelopak dalam
    for i in range(8):
        a = 360 * i / 8 + 22.5
        g.append('<path d="%s" transform="rotate(%.1f) translate(0,-%.1f)" fill="%s" '
                 'opacity=".22"/>' % (petal(r * .22, r * .07), a, r * .30, warna))
    for rr, op in ((.42, .45), (.46, .30), (.92, .30)):
        g.append('<circle r="%.1f" fill="none" stroke="%s" stroke-width="%.1f" opacity="%.2f"/>'
                 % (r * rr, warna, max(1.2, r * .009), op))
    g.append('<circle r="%.1f" fill="none" stroke="%s" stroke-width="%.1f" opacity=".55"/>'
             % (r * .10, warna, max(1.4, r * .014)))
    return ('<svg class="mandala" viewBox="%.0f %.0f %.0f %.0f">%s</svg>'
            % (-r, -r, r * 2, r * 2, ''.join(g)))


def diya(lebar):
    """Diya emas + nyala api + cahaya, sebagai SVG (nisbah 300x400)."""
    return """
<svg class="diya" viewBox="0 0 300 400" style="width:%(w)spx">
  <defs>
    <radialGradient id="cahaya" cx="50%%" cy="50%%" r="50%%">
      <stop offset="0%%" stop-color="#ffd873" stop-opacity=".62"/>
      <stop offset="42%%" stop-color="#ff9d2e" stop-opacity=".20"/>
      <stop offset="100%%" stop-color="#ff7a00" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="api" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0%%" stop-color="#fffbe8"/>
      <stop offset="34%%" stop-color="#ffe27a"/>
      <stop offset="70%%" stop-color="#ffab28"/>
      <stop offset="100%%" stop-color="#ff7d00"/>
    </linearGradient>
    <linearGradient id="bekas" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%%" stop-color="#ffeeae"/>
      <stop offset="26%%" stop-color="#f7c53f"/>
      <stop offset="74%%" stop-color="#d68d10"/>
      <stop offset="100%%" stop-color="#8b5204"/>
    </linearGradient>
    <radialGradient id="dalam" cx="50%%" cy="34%%" r="66%%">
      <stop offset="0%%" stop-color="#6f4305"/>
      <stop offset="58%%" stop-color="#a8680a"/>
      <stop offset="100%%" stop-color="#452602"/>
    </radialGradient>
  </defs>
  <ellipse cx="150" cy="150" rx="150" ry="150" fill="url(#cahaya)"/>
  <g class="nyala">
    <path d="M150 26 C 178 88, 199 126, 186 166 C 175 200, 125 200, 114 166 C 101 126, 122 88, 150 26 Z"
          fill="url(#api)"/>
    <path d="M150 82 C 165 118, 174 140, 167 161 C 161 180, 139 180, 133 161 C 126 140, 135 118, 150 82 Z"
          fill="#fffdf2" opacity=".95"/>
  </g>
  <path d="M22 196 A128 40 0 0 0 278 196 C 278 268, 224 312, 150 312 C 76 312, 22 268, 22 196 Z"
        fill="url(#bekas)"/>
  <ellipse cx="150" cy="196" rx="128" ry="40" fill="url(#dalam)"/>
  <ellipse cx="150" cy="196" rx="128" ry="40" fill="none" stroke="#ffeaa8" stroke-width="6" opacity=".8"/>
  <ellipse cx="150" cy="302" rx="98" ry="16" fill="#1a0006" opacity=".33"/>
</svg>
""" % {'w': lebar}


def lampu(tinggi):
    """Rentetan lampu (vilakku) melengkung di bahagian atas kad."""
    titik = [(-10, 8), (150, 34), (310, 62), (470, 88), (630, 106),
             (790, 110), (950, 94), (1110, 66), (1270, 34), (1410, 10)]
    bulatan = ''.join(
        '<circle cx="%d" cy="%d" r="6.5"/><circle cx="%d" cy="%d" r="17" opacity=".20"/>'
        % (x, y, x, y) for x, y in titik)
    return """
<svg class="lampu" viewBox="0 0 1400 240" preserveAspectRatio="none" style="height:%dpx">
  <path d="M-20 6 Q 700 214 1420 38" fill="none" stroke="#ffdca6" stroke-width="2.2" opacity=".5"/>
  <g fill="#fff8e2">%s</g>
</svg>
""" % (tinggi, bulatan)


CSS = """
@font-face{font-family:'Playfair';src:url('fon/pd.ttf')}
@font-face{font-family:'Jost';src:url('fon/jost.ttf')}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%(w)spx;height:%(h)spx;overflow:hidden;background:#3c030c}
.kad{position:relative;width:%(w)spx;height:%(h)spx;overflow:hidden;color:#fff;
  font-family:'Jost',sans-serif;
  background:radial-gradient(118%% 96%% at 70%% 38%%, #c21634 0%%, #a2102a 28%%, #7e0a1e 56%%, #560613 82%%, #38030a 100%%)}
.vin{position:absolute;inset:0;background:radial-gradient(125%% 105%% at 64%% 40%%, #0000 42%%, #2a020959 78%%, #1c01047d 100%%)}
.mandala{position:absolute;%(mand)s;overflow:visible;opacity:.40}
.diya{position:absolute;%(diya)s;height:auto;filter:drop-shadow(0 16px 40px #ff9d2e4d)}
.lampu{position:absolute;left:0;top:0;width:100%%;opacity:.85;
  filter:drop-shadow(0 0 9px #ffca7a) drop-shadow(0 0 24px #ffa63e7d)}
.blok{position:absolute;%(blok)s}
.happy{font-weight:%(happyW)s;font-size:%(happyF)spx;letter-spacing:.46em;color:#ffe7cb;opacity:.96}
.tajuk{font-family:'Playfair';font-weight:400;font-size:%(tajukF)spx;line-height:1.04;letter-spacing:-.012em;
  text-shadow:0 0 %(glow)spx #ff9b3eb3, 0 0 %(glow2)spx #ffb3476b}
.rule{width:%(ruleW)spx;height:1.5px;background:linear-gradient(90deg,#ffd08a,#ffd08a00);opacity:.85;
  margin:%(ruleM)spx 0 %(ruleM2)spx}
.sub{font-weight:300;font-size:%(subF)spx;line-height:%(subL)s;color:#ffeee1;letter-spacing:.012em}
.dari{display:flex;align-items:center;gap:%(gap)spx;margin-top:%(dariM)spx}
.dari img{width:%(kres)spx;height:%(kres)spx;object-fit:contain;filter:drop-shadow(0 3px 9px #00000059)}
.dari .txt{display:flex;flex-direction:column;gap:%(dariGap)spx}
.dari b{font-weight:500;font-size:%(dariBF)spx;letter-spacing:.02em;color:#ffeed9}
.dari span{font-weight:300;font-size:%(dariSF)spx;line-height:1.4;color:#f8ddcc;opacity:.9;max-width:%(dariSW)spx}
.tahun{position:absolute;%(tahun)s;font-weight:400;font-size:%(tahunF)spx;letter-spacing:.34em;color:#ffd9a8;opacity:.66}
"""


def html(nama):
    w, h = SAIZ[nama]
    if nama == 'besar':
        # Desktop: hero image hanya kelihatan jelas di bahagian KANAN kotak
        # (gradien putih hero menutupi ~45% kiri imej), jadi semua teks duduk 46%-88%.
        g = dict(
            mand='right:-140px;bottom:-210px;width:780px;height:780px',
            diya='right:44px;bottom:118px;width:250px',
            lampuH=200,
            blok='left:646px;top:186px;width:600px',
            happyW=300, happyF=31, tajukF=124, glow=22, glow2=54,
            ruleW=270, ruleM=16, ruleM2=18, subF=25, subL=1.5,
            gap=15, dariM=30, kres=68, dariGap=3, dariBF=18, dariSF=15, dariSW=380,
            tahun='right:112px;bottom:52px', tahunF=16,
        )
    else:
        # Telefon: kotak hero 390x340; tepi kiri/kanan terpotong ~12% setiap sisi
        # (object-fit:cover), bawah pula diliputi gradien putih hero.
        g = dict(
            mand='right:-56px;bottom:-84px;width:400px;height:400px',
            diya='right:66px;top:170px;width:186px',
            lampuH=120,
            blok='left:96px;top:56px;width:330px',
            happyW=300, happyF=21, tajukF=84, glow=13, glow2=32,
            ruleW=200, ruleM=10, ruleM2=12, subF=21, subL=1.45,
            gap=11, dariM=18, kres=50, dariGap=2, dariBF=18, dariSF=16, dariSW=250,
            tahun='right:26px;bottom:18px', tahunF=11,
        )
    isi = CSS % dict(g, w=w, h=h)
    dari_s = TEKS['dari_s'] if nama == 'besar' else 'MADOCS'
    return """<!doctype html><html lang="ms"><head><meta charset="utf-8">
<title>Kad Deepavali 2026 — %s</title><style>%s</style></head><body>
<div class="kad">
  %s
  <div class="vin"></div>
  %s
  %s
  <div class="blok">
    <div class="happy">%s</div>
    <div class="tajuk">%s</div>
    <div class="rule"></div>
    <p class="sub">%s</p>
    <div class="dari">
      <img src="%s/assets/logo-192.webp" alt="Lambang MADOCS">
      <div class="txt"><b>%s</b><span>%s</span></div>
    </div>
  </div>
  <div class="tahun">2026</div>
</div></body></html>""" % (
        nama, isi, lampu(g['lampuH']), mandala(210 if nama == 'besar' else 205),
        diya(250 if nama == 'besar' else 186),
        TEKS['happy'], TEKS['tajuk'], TEKS['sub'],
        AKAR, TEKS['dari_b'], dari_s)


def tulis():
    os.makedirs(os.path.join(TMP, 'fon'), exist_ok=True)
    for f in ('pd.ttf', 'jost.ttf'):
        asal, sementara = os.path.join(FON, f), os.path.join(TMP, 'fon', f)
        if os.path.exists(asal) and not os.path.exists(sementara):
            import shutil
            shutil.copy(asal, sementara)
    for nama in SAIZ:
        p = os.path.join(TMP, 'kad-%s.html' % nama)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(html(nama))
        print('tulis', p)


def pasang():
    for nama, saiz in SAIZ.items():
        src = os.path.join(TMP, 'kad-%s.png' % nama)
        if not os.path.exists(src):
            print('TIADA', src)
            continue
        im = Image.open(src).convert('RGB')
        if im.size != saiz:
            im = im.resize(saiz, Image.LANCZOS)
        out = os.path.join(AKAR, 'assets', 'hero', 'ucapan-deepavali-%s.webp' % nama)
        im.save(out, 'WEBP', quality=88, method=6)
        print('pasang %-46s %s %d KB' % ('assets/hero/ucapan-deepavali-%s.webp' % nama,
                                         im.size, os.path.getsize(out) // 1024))


if __name__ == '__main__':
    if '--pasang' in sys.argv:
        pasang()
    else:
        tulis()
