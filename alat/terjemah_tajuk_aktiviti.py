#!/usr/bin/env python3
"""Lengkapkan kamus terjemahan untuk tajuk dan subtajuk halaman aktiviti.

Masalah: <title> memakai "Tajuk | Aktiviti MADOCS" dan subtajuk hero memakai ayat pertama
ringkas — dua bentuk yang tidak sama dengan teks dalam data, jadi kamus tidak menjumpainya
dan halaman Inggeris kekal Bahasa Melayu.
"""
import json
from pathlib import Path

AKAR = Path('/home/ubuntu/madocs-site')


def potong_meta(teks: str, had: int = 158) -> str:
    """Sama seperti ringkas_meta() dalam build.py."""
    import re
    t = re.sub(r"\s+", " ", str(teks or "")).strip()
    if len(t) <= had:
        return t
    potong = t[:had].rsplit(" ", 1)[0]
    return potong.rstrip(" ,.;:") + "\u2026"


def ayat1(teks: str) -> str:
    teks = (teks or '').strip()
    return (teks.split('. ')[0] + '.') if '. ' in teks else teks


def utama():
    p = AKAR / 'data' / 'terjemahan.json'
    kamus = json.loads(p.read_text(encoding='utf-8'))
    aktiviti = json.loads((AKAR / 'data' / 'aktiviti.json').read_text(encoding='utf-8'))['aktiviti']

    tambah = 0
    for a in aktiviti:
        tajuk, ringkas = a.get('tajuk', ''), a.get('ringkas', '')
        tajuk_en = kamus.get(tajuk)
        ringkas_en = kamus.get(ringkas)

        if tajuk_en:
            for akhiran_bm, akhiran_en in ((' | Aktiviti MADOCS', ' | MADOCS Activities'),
                                           (' | MADOCS', ' | MADOCS')):
                kunci = tajuk + akhiran_bm
                if kunci not in kamus:
                    kamus[kunci] = tajuk_en + akhiran_en
                    tambah += 1

        if ringkas_en:
            a1_bm, a1_en = ayat1(ringkas), ayat1(ringkas_en)
            if a1_bm and a1_bm != ringkas and a1_bm not in kamus:
                kamus[a1_bm] = a1_en
                tambah += 1
            # deskripsi meta dipotong pada 158 aksara — daftarkan bentuk terpotong juga
            potong_bm, potong_en = potong_meta(ringkas), potong_meta(ringkas_en)
            if potong_bm != ringkas:
                kamus.setdefault(potong_bm, potong_en)
                tambah += 1

    # Varian HTML-escaped: teks dalam HTML sudah di-escape (&quot; &amp;), jadi kunci kamus
    # mesti ada bentuk yang sama untuk dipadankan.
    import html as _html
    for kunci, nilai in list(kamus.items()):
        if '&' in kunci or '"' in kunci or '<' in kunci:
            k_esc, v_esc = _html.escape(kunci, quote=True), _html.escape(nilai, quote=True)
            if k_esc not in kamus:
                kamus[k_esc] = v_esc
                tambah += 1

    p.write_text(json.dumps(kamus, ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    print('entri baharu:', tambah, '| jumlah kamus:', len(kamus))


if __name__ == '__main__':
    utama()
