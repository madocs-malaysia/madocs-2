#!/usr/bin/env python3
"""Peringatan perayaan Malaysia untuk laman MADOCS.

Dijalankan oleh cron Hermes (no_agent): stdout dihantar terus ke Telegram Doc.
Tiada output = tiada mesej (jangan spam).

Guna:
  python3 semak_perayaan.py           # mod cron: cetak hanya bila tiba masa
  python3 semak_perayaan.py --lapor   # senarai 12 bulan akan datang (manual)
  python3 semak_perayaan.py --hari-ini 2026-12-04   # uji logik peringatan
"""
import json
import os
import sys
from datetime import date

AKAR = '/home/ubuntu/madocs-site'
DATA = os.path.join(AKAR, 'data', 'perayaan.json')
STATE = os.path.expanduser('~/.hermes/profiles/madocs/scripts/.dilapor-perayaan.json')

HARI_KAD = 21      # kad ucapan perlu disiapkan: peringatan 3 minggu awal
HARI_INFO = 7      # perayaan tanpa kad: makluman seminggu awal
HARI_KEMAS = 60    # kalau tiada perayaan dalam tempoh ini, minta kemas kini kalendar

HARI_INI = date.today()   # boleh ditindih dengan --hari-ini YYYY-MM-DD untuk ujian

NAMA_BULAN = ('Januari', 'Februari', 'Mac', 'April', 'Mei', 'Jun', 'Julai',
              'Ogos', 'September', 'Oktober', 'November', 'Disember')
NAMA_HARI = ('Isnin', 'Selasa', 'Rabu', 'Khamis', 'Jumaat', 'Sabtu', 'Ahad')


def baca_data():
    with open(DATA, encoding='utf-8') as f:
        return json.load(f)


def baca_state():
    if os.path.exists(STATE):
        try:
            with open(STATE, encoding='utf-8') as f:
                return json.load(f)
        except (OSError, ValueError):
            pass
    return {}


def tulis_state(state):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    tmp = STATE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATE)


def tarikh_teks(d):
    return '%d %s %d (%s)' % (d.day, NAMA_BULAN[d.month - 1], d.year, NAMA_HARI[d.weekday()])


def akan_datang(hari=400):
    hari_ini = HARI_INI
    senarai = []
    for p in baca_data()['perayaan']:
        try:
            d = date.fromisoformat(p['tarikh'])
        except (KeyError, ValueError):
            continue
        beza = (d - hari_ini).days
        if 0 <= beza <= hari:
            senarai.append((d, beza, p))
    senarai.sort(key=lambda x: x[0])
    return senarai


def mesej_perayaan(d, beza, p):
    baris = ['Peringatan perayaan: %s' % p['nama'],
             'Tarikh: %s' % tarikh_teks(d),
             'Lagi %d hari.' % beza if beza else 'Hari ini.']
    if p.get('kad'):
        baris.append('')
        baris.append('Kad ucapan hero perlu disiapkan. Beritahu aku bila Doc nak '
                     'aku reka / pasang kad %s.' % p['nama'])
    if p.get('nota'):
        baris.append('Nota: %s' % p['nota'])
    return '\n'.join(baris)


def main():
    global HARI_INI
    if '--hari-ini' in sys.argv:
        HARI_INI = date.fromisoformat(sys.argv[sys.argv.index('--hari-ini') + 1])
    lapor = '--lapor' in sys.argv
    datang = akan_datang()

    if lapor:
        if not datang:
            print('Tiada perayaan dalam kalendar 400 hari akan datang.')
        for d, beza, p in datang:
            tanda = 'KAD' if p.get('kad') else '   '
            print('%s  %-22s %s  %4d hari' % (tanda, p['nama'], tarikh_teks(d), beza))
        return

    state = baca_state()
    keluar = []

    for d, beza, p in datang:
        kunci = '%s@%s' % (p['nama'], p['tarikh'])
        had = HARI_KAD if p.get('kad') else HARI_INFO
        if beza <= had and kunci not in state:
            keluar.append(mesej_perayaan(d, beza, p))
            state[kunci] = HARI_INI.isoformat()

    # Kalendar hampir habis: minta kemas kini setahun sekali (maks sekali sebulan).
    if datang:
        tarikh_terakhir = max(d for d, _, _ in datang)
        if (tarikh_terakhir - HARI_INI).days <= HARI_KEMAS:
            kunci = 'kemas-kini@%d-%02d' % (HARI_INI.year, HARI_INI.month)
            if kunci not in state:
                keluar.append('Kalendar perayaan hampir habis (terakhir: %s).\n'
                              'Beritahu aku untuk kemas kini takwim tahun berikutnya.'
                              % tarikh_teks(tarikh_terakhir))
                state[kunci] = HARI_INI.isoformat()
    else:
        kunci = 'kemas-kini@%d-%02d' % (HARI_INI.year, HARI_INI.month)
        if kunci not in state:
            keluar.append('Kalendar perayaan kosong untuk tarikh akan datang.\n'
                          'Beritahu aku untuk tambah takwim tahun berikutnya.')
            state[kunci] = HARI_INI.isoformat()

    if keluar:
        print('\n\n'.join(keluar))
    if state != baca_state():
        tulis_state(state)


if __name__ == '__main__':
    main()
