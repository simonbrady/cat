#!/usr/bin/env python3

import ftplib
import sys

host = 'ftp.ncdc.noaa.gov'
base = '/pub/data/noaa'

ftp = ftplib.FTP(host)
ftp.login()
print('"year","count","max_size","total_size"')
for line in sys.stdin:
    year = line.strip()
    sys.stderr.write('%s\r' % year)
    count = max_size = total_size = 0
    for (name, facts) in ftp.mlsd('%s/%s' % (base, year), ['size']):
        if not name.startswith('.'):
            count += 1
            size = int(facts.get('size', 0))
            if size > max_size:
                max_size = size
            total_size += size
    print('%s,%d,%d,%d' % (year, count, max_size, total_size))
sys.stderr.write('\n')
ftp.quit()
