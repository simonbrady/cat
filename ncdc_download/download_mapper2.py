#!/usr/bin/env python3

import ftplib
import gzip
import os
import sys

host = 'ftp.ncdc.noaa.gov'
base = '/pub/data/noaa'
retries = 3

def connect(host):
    ftp = ftplib.FTP(host)
    ftp.login()
    return ftp

def fail(ftp):
    ftp.quit()
    sys.exit(1)
    
def status(msg):
    sys.stderr.write('%s\n' % msg)
    sys.stderr.write('reporter:status:%s\n' % msg)

ftp = connect(host)
for line in sys.stdin:
    (year, filename) = line.strip().split()
    for i in range(retries):
        status('Downloading file %s/%s (FTP attempt %d of %d)' % (year, filename, i + 1, retries))
        try:
            ftp.retrbinary('RETR %s/%s/%s' % (base, year, filename), open(filename, 'wb').write)
        except ftplib.all_errors as error:
            sys.stderr.write('%s\n' % error)
            if str(error).startswith('421'):
                sys.stderr.write('Attemptng reconnection after idle timeout\n')
                try:
                    ftp.quit()
                    ftp = connect(host)
                    sys.stderr.write('Reconnection succeeded\n')
                except ftplib.all_errors as nested_error:
                    sys.stderr.write('%s\n' % nested_error)
                    fail(ftp)
            continue
        status('Decompressing file %s/%s' % (year, filename))
        count = 0
        for record in gzip.open(filename, 'rb'):
            print('%s\t%s' % (year, record.decode('ISO-8859-1').strip()))
            count += 1
        os.remove(filename)
        sys.stderr.write('reporter:counter:NCDC Download,%s,%d\n' % (year, count))
        break
    else:
        fail(ftp)
ftp.quit()
