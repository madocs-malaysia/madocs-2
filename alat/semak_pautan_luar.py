#!/usr/bin/env python3
"""Semak semua pautan luar pada laman MADOCS (status, masa, sijil TLS).

Pautan luar diambil daripada folder data/ dan fail HTML yang dibina. Setiap URL diuji
dengan permintaan sebenar (ikuti ubah hala) dan sijil TLS diperiksa, kerana laman kerajaan
kadang-kadang memasang sijil lalai hosting yang menyebabkan amaran "not secure".

Guna: python3 alat/semak_pautan_luar.py [--json]
"""
import json
import re
import ssl
import socket
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import urlparse

AKAR = Path('/home/ubuntu/madocs-site')
AGEN = {'User-Agent': 'Mozilla/5.0 (compatible; MADOCS-link-check/1.0)'}
HAD_MASA = 25


def kumpul():
    url = set()
    for fail in list((AKAR / 'data').glob('*.json')):
        try:
            teks = fail.read_text(encoding='utf-8')
        except Exception:
            continue
        url |= set(re.findall(r'https?://[^\s"\'<>\\)]+', teks))
    for fail in AKAR.rglob('*.html'):
        if '.git' in fail.parts:
            continue
        try:
            teks = fail.read_text(encoding='utf-8')
        except Exception:
            continue
        url |= set(re.findall(r'href="(https?://[^"]+)"', teks))
    buang = ('madocs.my', 'www.madocs.my', 'github.com/madocs-malaysia',
             'schema.org', 'w3.org', 'facebook.com/sharer', 'wa.me', 't.me',
             'cloudflareinsights', 'cdnjs.cloudflare')
    return sorted(u for u in url if '…' not in u and not any(b in u for b in buang))


def semak_tls(host):
    cuba = ssl.create_default_context()
    try:
        with socket.create_connection((host, 443), timeout=12) as s:
            with cuba.wrap_socket(s, server_hostname=host) as ss:
                return True, ss.getpeercert().get('subject', [])
    except ssl.SSLCertVerificationError as e:
        return False, 'sijil tidak sah: %s' % e.verify_message
    except Exception as e:
        return False, str(e)[:80]


def semak(url):
    hasil = {'url': url}
    if urlparse(url).scheme == 'https':
        ok, maklumat = semak_tls(urlparse(url).hostname)
        hasil['tls'] = 'ok' if ok else maklumat
    else:
        hasil['tls'] = 'http'
    req = urllib.request.Request(url, headers=AGEN)
    mula = time.time()
    try:
        with urllib.request.urlopen(req, timeout=HAD_MASA) as r:
            hasil['status'] = r.status
            hasil['muka'] = r.geturl()
            hasil['saiz_kb'] = round(len(r.read()) / 1024)
            hasil['masa'] = round(time.time() - mula, 2)
    except urllib.error.HTTPError as e:
        hasil['status'] = e.code
    except Exception as e:
        hasil['status'] = 0
        hasil['ralat'] = str(e)[:90]
    return hasil


def utama():
    senarai = kumpul()
    hasil = [semak(u) for u in senarai]
    rosak = [h for h in hasil if h.get('status') != 200 or h.get('tls') not in ('ok', 'http')]
    if '--json' in sys.argv:
        print(json.dumps(hasil, ensure_ascii=False, indent=1))
        return
    print('Pautan luar diperiksa: %d | bermasalah: %d' % (len(hasil), len(rosak)))
    for h in hasil:
        tanda = 'OK ' if h not in rosak else '!! '
        print('%s%-56s %s %5ss %5s KB%s' % (tanda, h['url'][:56], h.get('status'), h.get('masa','-'), h.get('saiz_kb','-'),
                                ('' if h.get('tls') in ('ok', 'http') else '  TLS: ' + str(h.get('tls'))[:60])))


if __name__ == '__main__':
    utama()
