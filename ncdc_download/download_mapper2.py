#!/usr/bin/env python3

from ftplib import FTP
import gzip
import sys

host = 'ftp.ncdc.noaa.gov'
base = '/pub/data/noaa'

ftp = FTP(host)
ftp.login()
for line in sys.stdin:
    (year, filename) = line.strip().split()
    sys.stderr.write('reporter:status:Processing file %s/%s\n' % (year, filename))
    data = bytearray()
    ftp.retrbinary('RETR %s/%s/%s' % (base, year, filename), data.extend)
    records = gzip.decompress(data).decode('ISO-8859-1').split('\n')[0:-1]
    for record in records:
        print('%s\t%s' % (year, record))
    sys.stderr.write('reporter:counter:NCDC Download,%s,%d\n' % (year, len(records)))
ftp.quit()
