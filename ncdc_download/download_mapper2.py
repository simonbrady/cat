#!/usr/bin/env python3

import ftplib
import gzip
import os
import sys

host = 'ftp.ncdc.noaa.gov'
base = '/pub/data/noaa'
retries = 3

ftp = ftplib.FTP(host)
ftp.login()
for line in sys.stdin:
    (year, filename) = line.strip().split()
    for i in range(retries):
        sys.stderr.write('reporter:status:Processing file %s/%s (FTP attempt %d of %d)\n' % (year,
            filename, i + 1, retries))
        try:
            ftp.retrbinary('RETR %s/%s/%s' % (base, year, filename), open(filename, 'wb').write)
        except ftplib.all_errors as error:
            sys.stderr.write('%s\n' % error)
            continue
        count = 0
        for record in gzip.open(filename, 'rb'):
            print('%s\t%s' % (year, record.decode('ISO-8859-1').strip()))
            count += 1
        sys.stderr.write('reporter:counter:NCDC Download,%s,%d\n' % (year, count))
        os.remove(filename)
        break
    else:
        ftp.quit()
        sys.exit(1)
ftp.quit()
