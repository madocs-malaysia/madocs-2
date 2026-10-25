#!/usr/bin/env python3
"""Ambil fail senarai ahli MADOCS terus dari Google Drive (service account).

Menggunakan kredensial: ~/.hermes/profiles/madocs/secrets/madocs-sync.json
Fail mesti dikongsi dengan alamat service account sebagai Viewer.

Guna:
    python3 ambil_senarai.py            # muat turun ke cache
    python3 ambil_senarai.py --bina     # muat turun, bina data/ahli.json, bina laman
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

KRED = Path('/home/ubuntu/.hermes/profiles/madocs/secrets/madocs-sync.json')
FAIL_ID = '1YgFxsYLadQd81u16kNtGHi9jo75aoMxy'
SIMBOL = Path('/home/ubuntu/.hermes/profiles/madocs/cache/senarai-ahli-terkini.xlsx')
SKOP = ['https://www.googleapis.com/auth/drive.readonly']
AKAR = Path('/home/ubuntu/madocs-site')


def ambil() -> Path:
    if not KRED.exists():
        sys.exit('Kredensial tidak dijumpai: %s' % KRED)
    kred = service_account.Credentials.from_service_account_file(str(KRED), scopes=SKOP)
    servis = build('drive', 'v3', credentials=kred, cache_discovery=False)

    meta = servis.files().get(fileId=FAIL_ID, fields='name,mimeType,modifiedTime,size',
                              supportsAllDrives=True).execute()
    print('fail    :', meta.get('name'))
    print('jenis   :', meta.get('mimeType'))
    print('diubah  :', meta.get('modifiedTime'))
    print('saiz    :', round(int(meta.get('size', 0)) / 1024), 'KB')

    SIMBOL.parent.mkdir(parents=True, exist_ok=True)
    data = servis.files().get_media(fileId=FAIL_ID, supportsAllDrives=True).execute()
    SIMBOL.write_bytes(data)
    print('disimpan:', SIMBOL, '(%d KB)' % (len(data) // 1024))
    return SIMBOL


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bina', action='store_true', help='bina data/ahli.json dan laman selepas muat turun')
    a = ap.parse_args()

    try:
        fail = ambil()
    except HttpError as e:
        if e.resp.status == 404:
            print('RALAT: fail tidak dijumpai. Pastikan fail dikongsi dengan akaun service account.', file=sys.stderr)
        elif e.resp.status == 403:
            print('RALAT: tiada kebenaran. Kongsi fail sebagai Viewer dengan akaun service account.', file=sys.stderr)
        else:
            print('RALAT Drive API:', e, file=sys.stderr)
        sys.exit(1)

    if a.bina:
        pybin = sorted(Path('/home/ubuntu/.hermes/tools').glob('python-3.*/bin/python3'))[-1]
        subprocess.run([str(pybin), 'alat/bina_ahli_json.py', str(fail), '--tulis'],
                       cwd=AKAR, check=True)
        subprocess.run(['python3', 'build.py'], cwd=AKAR, check=True)


if __name__ == '__main__':
    main()
