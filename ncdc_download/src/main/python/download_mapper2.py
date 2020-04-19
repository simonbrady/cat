#!/usr/bin/env python3

import ftplib
import gzip
import os
import time
import sys
from datetime import datetime

host = 'ftp.ncdc.noaa.gov'
base = '/pub/data/noaa'
retries = 3

def connect(host):
    ftp = ftplib.FTP(host)
    ftp.login()
    return ftp

def status(msg):
    sys.stderr.write('%s %s\n' % (datetime.utcnow().isoformat(), msg))
    sys.stderr.write('reporter:status:%s\n' % msg)

def fail(year, filename):
    status('Failed to download %s/%s' % (year, filename))
    sys.stderr.write('reporter:counter:NCDC Download Failures,%s,1\n' % year)
    try:
        os.remove(filename)
    except FileNotFoundError:
        pass # File might not even have been created

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
                status('Attempting reconnection after idle timeout')
                try:
                    ftp = connect(host)
                    status('Reconnection succeeded')
                except ftplib.all_errors as error:
                    sys.stderr.write('%s\n' % error)
                    fail(year, filename)
                    sys.exit(1) # Fail the map task if we can't even reconnect
            else:
                time.sleep(30) # Unknown error, so delay in case it's something transient
            continue # Retry download
        break # Download succeeded
    else:
        fail(year, filename) # Retries exhausted, move on to next file
        continue
    status('Decompressing file %s/%s' % (year, filename))
    count = 0
    for record in gzip.open(filename, 'rb'):
        print('%s\t%s' % (year, record.decode('ISO-8859-1').strip()))
        count += 1
    os.remove(filename)
    sys.stderr.write('reporter:counter:NCDC Download Records,%s,%d\n' % (year, count))
ftp.quit()
