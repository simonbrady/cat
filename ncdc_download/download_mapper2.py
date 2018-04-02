#!/usr/bin/env python3

import ftplib
import gzip
import sys

host = 'ftp.ncdc.noaa.gov'
base = '/pub/data/noaa'
retries = 3

ftp = ftplib.FTP(host)
ftp.login()
for line in sys.stdin:
    (year, filename) = line.strip().split()
    for i in range(retries):
        sys.stderr.write('reporter:status:Processing file %s/%s (FTP attempt %d of %d)\n' % (year, filename, i + 1, retries))
        data = bytearray()
        try:
            ftp.retrbinary('RETR %s/%s/%s' % (base, year, filename), data.extend)
        except ftplib.all_errors as error:
            sys.stderr.write('%s\n' % error)
            continue
        records = gzip.decompress(data).decode('ISO-8859-1').split('\n')[0:-1]
        for record in records:
            print('%s\t%s' % (year, record))
        sys.stderr.write('reporter:counter:NCDC Download,%s,%d\n' % (year, len(records)))
        break
    else:
        ftp.quit()
        sys.exit(1)
ftp.quit()
