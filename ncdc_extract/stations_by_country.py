#!/usr/bin/env python3

# Extract station IDs for given countries from NCDC metadata file isd-history.csv

import csv
import sys

if len(sys.argv) < 3:
    sys.stderr.write('Usage: stations_by_country.py /path/to/isd-history.csv NZ AU ...\n')
    sys.exit(1)
countries = [c.upper() for c in sys.argv[2:]]
reader = csv.reader(open(sys.argv[1]))
next(reader)   # Skip header row
for row in reader:
    if row[3] in countries:
        print('%s-%s # %s (%s)' % tuple(row[0:4]))
