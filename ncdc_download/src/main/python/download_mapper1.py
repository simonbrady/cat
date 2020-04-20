#!/usr/bin/env python3

import ftplib
import sys

host = 'ftp.ncdc.noaa.gov'
base = '/pub/data/noaa'

ftp = ftplib.FTP(host)
ftp.login()
for line in sys.stdin:
    year = line.strip()
    sys.stderr.write('reporter:status:Processing year %s\n' % year)
    ftp.cwd('%s/%s' % (base, year))
    for filename in ftp.nlst():
        print('%s\t%s' % (year, filename))
ftp.quit()
