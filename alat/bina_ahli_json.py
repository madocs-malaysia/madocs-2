#!/usr/bin/env python3
"""Bina data/ahli.json untuk /semak-ahli/ daripada senarai rasmi ahli MADOCS (xlsx).

Hanya empat medan awam diambil: no, nama_papar, kategori, status, sah_hingga.
Nombor kad pengenalan, telefon, e-mel dan nombor MMC TIDAK diambil.

Guna: python3 bina_ahli_json.py "<laluan xlsx>" [--tulis]
"""
import sys, json, re, calendar, datetime, collections
import openpyxl

JENIS = {'LM': 'Ahli Seumur Hidup', 'OM': 'Ahli Biasa', 'AM': 'Ahli Bersekutu'}
STATUS = {'active': 'aktif', 'inactive': 'tamat', 'aktif': 'aktif', 'tidak aktif': 'tamat'}

HARI_INI = datetime.date.today()

# Ahli yang permohonannya ditolak oleh jawatankuasa — tidak diterbitkan di laman.
# Nombor ahli mereka dibiarkan "bersara" (tidak digunakan semula untuk ahli lain).
DITOLAK = {
    'PPM7',   # Tan Thean Hee — tiada APC semasa pendaftaran; ditolak AJK (Okt 2026)
}


def tarikh(v):
    """Terima datetime, date, atau teks d/m/Y."""
    if isinstance(v, datetime.datetime):
        return v.date()
    if isinstance(v, datetime.date):
        return v
    if not v:
        return None
    teks = str(v).strip()
    for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%y', '%d.%m.%Y'):
        try:
            return datetime.datetime.strptime(teks, fmt).date()
        except ValueError:
            pass
    return None


def tambah_bulan(d, n=12):
    m = d.month - 1 + n
    tahun, bulan = d.year + m // 12, m % 12 + 1
    return d.replace(year=tahun, month=bulan,
                     day=min(d.day, calendar.monthrange(tahun, bulan)[1]))

GELARAN = {'dr', 'dr.', 'datuk', 'mej', 'hj', 'hj.', 'hjh', 'prof', 'prof.', 'mr', 'mr.', 'tan', 'sri', 'dato', 'dato\'', 'datin'}
SAMBUNG = {'bin', 'binti', 'bt', 'b.', 'b'}


def topeng(nama):
    keluar = []
    for k in str(nama).split():
        bersih = k.replace('(', '').replace(')', '').replace('.', '')
        bawah = bersih.lower()
        if bawah in GELARAN:
            keluar.append(k)
        elif '/' in k:                      # A/L, A/P — kekalkan
            keluar.append(k)
        elif bawah in SAMBUNG:
            keluar.append('b.')
        else:
            keluar.append(k[0].upper() + '***' if k else '')
    return ' '.join(x for x in keluar if x)


def baca(xlsx):
    wb = openpyxl.load_workbook(xlsx, data_only=True)
    ws = wb['SENARAI NAMA AHLI MADOCS']
    baris = list(ws.iter_rows(min_row=3, values_only=True))
    hdr = [('' if c is None else str(c)).strip() for c in baris[0]]

    def idx(*kunci):
        for i, h in enumerate(hdr):
            if any(k.lower() in h.lower() for k in kunci):
                return i
        return None

    iNama, iNo = idx('Name'), idx('Membership Number')
    iJenis, iStatus = idx('Type'), idx('Status Membership')
    iMula = idx('Date of Membership')
    iBayar = [i for i, h in enumerate(hdr) if 'Date of Payment' in h]
    iLuput = idx('Validity Membership', 'Tarikh Luput', 'Valid Until', 'Expiry')

    rekod, dibuang, perlu_semak = [], [], []
    for r in baris[1:]:
        g = lambda i: '' if i is None or i >= len(r) or r[i] is None else str(r[i]).strip()
        nama, no = g(iNama), g(iNo)
        if not nama or not no or not re.match(r'^[A-Z]{2,4}\d+$', no.upper()):
            if nama:
                dibuang.append((nama[:36], no or '(tiada nombor)'))
            continue
        status = STATUS.get(g(iStatus).lower(), '')
        if no.upper() in DITOLAK:
            dibuang.append((nama[:36], 'ditolak AJK'))
            continue
        if not status:
            dibuang.append((nama[:36], 'status kosong'))
            continue
        jenis = g(iJenis).upper()

        # tarikh sah: utamakan lajur "Validity Membership" (dikemas kini oleh setiausaha).
        # Nilai "Lifetime" bermaksud keahlian seumur hidup. Jika kosong, kira sandaran:
        # 12 bulan dari bayaran terakhir, atau dari tarikh keahlian.
        mentah = r[iLuput] if (iLuput is not None and iLuput < len(r)) else None
        teks = ('' if mentah is None else str(mentah).strip())
        seumur = bool(re.search(r'lifetime|seumur', teks, re.I)) or jenis == 'LM'
        tetap = None if seumur else tarikh(mentah)
        bayar = [tarikh(r[i]) for i in iBayar if i < len(r)]
        bayar = [b for b in bayar if b]
        asas = max(bayar) if bayar else (tarikh(r[iMula]) if iMula is not None else None)
        sah = ''
        if not seumur:
            if tetap:
                sah = tetap.isoformat()
            elif asas:
                luput = tambah_bulan(asas)
                if status == 'aktif' and luput < HARI_INI:
                    perlu_semak.append((no.upper(), nama[:30], str(luput)))
                else:
                    sah = luput.isoformat()
            else:
                perlu_semak.append((no.upper(), nama[:30], '(tiada tarikh)'))
        kategori = 'Ahli Seumur Hidup' if (seumur or jenis == 'LM') else JENIS.get(jenis, 'Ahli Biasa')

        rekod.append({
            'no': no.upper(),
            'nama_papar': topeng(nama),
            'kategori': kategori,
            'status': status,
            'sah_hingga': sah,
        })
    return rekod, dibuang, perlu_semak


def main():
    xlsx = sys.argv[1]
    rekod, dibuang, perlu_semak = baca(xlsx)
    awalan = collections.Counter(re.match(r'^([A-Z]+)', x['no']).group(1) for x in rekod)

    data = {
        'nota': ('Rekod awam status keahlian MADOCS. Tiada kad pengenalan, nombor MMC, '
                 'telefon atau e-mel disimpan di sini. Nombor ahli mengikut kod negeri.'),
        'dikemas_kini': HARI_INI.isoformat(),
        'contoh': False,
        'ahli': rekod,
    }

    print(f'ahli diterima : {len(rekod)}')
    print(f'aktif         : {sum(1 for x in rekod if x["status"] == "aktif")}')
    print(f'tamat         : {sum(1 for x in rekod if x["status"] == "tamat")}')
    print(f'seumur hidup  : {sum(1 for x in rekod if x["kategori"] == "Ahli Seumur Hidup")}')
    print(f'ada tarikh    : {sum(1 for x in rekod if x["sah_hingga"])}')
    print(f'perlu semak   : {len(perlu_semak)}')
    for n in perlu_semak:
        print('   •', n[0], n[1], n[2])
    print(f'kod negeri    : {dict(awalan.most_common())}')
    print(f'dibuang       : {len(dibuang)}')
    for n, s in dibuang[:12]:
        print('   •', n, '|', s)

    if '--tulis' in sys.argv:
        with open('/home/ubuntu/madocs-site/data/ahli.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
            f.write('\n')
        print('ditulis: data/ahli.json')


if __name__ == '__main__':
    main()
