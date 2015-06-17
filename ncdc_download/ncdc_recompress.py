#!/usr/bin/env python

import argparse
from datetime import datetime
import glob
import os
import stat
from subprocess import PIPE, Popen
import sys

# Command line arguments
args = None

# Station ID to region map
region_map = {}

# Input files for each region encountered
input_files = {}

# Parse command line and set up args global variable with result
def parse_args():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--region-map", type=str,
                        default="station_regions.txt", help="file of station" +
                            "-to-region mappings, default station_regions.txt")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="verbose output")
    parser.add_argument("source_dir", type=str,
                        help="directory of NCDC files, one subdir per year")
    parser.add_argument("output_pattern", type=str,
                        help="output filename pattern, e.g. 'ncdc_{0}.bz2'")
    parser.add_argument("start_year", type=int,
                        help="first year of files to process")
    parser.add_argument("end_year", type=int,
                        help="last year of files to process")
    args = parser.parse_args()

def log(msg):
    if args.verbose:
        print datetime.now().ctime(), msg

def fatal(msg):
    sys.stderr.write(msg + "\n")
    sys.exit(1)

def load_region_map():
    global region_map
    try:
        mapfile = open(args.region_map, "r")
        for line in mapfile:
            line = line.strip()
            if len(line) == 0 or line[0] == "#":
                continue
            station, region = line.split()[:2]
            region_map[station] = region
        mapfile.close()
        log("Loaded {0} mappings from {1}".format(len(region_map.keys()),
            args.region_map))
    except Exception as e:
        fatal("Error reading map file {0}: {1}".format(args.region_map, str(e)))

def scan_input(year):
    global input_files
    log("Scanning {0}/{1}".format(args.source_dir, year))
    try:
        for filename in glob.glob("{0}/{1}/*.gz".format(args.source_dir, year)):
            # Strip "-YYYY.gz" suffix off filename
            station = os.path.basename(filename)[:-8]
            region = region_map.get(station, "E")
            size = os.stat(filename)[stat.ST_SIZE]
            if input_files.get(region) == None:
                input_files[region] = [0, []]
            input_files[region][0] += size
            input_files[region][1].append(filename)
    except Exception as e:
        fatal("Error processing {0}: {1}".format(year, str(e)))

def create_output_files():
    work_list = sorted(input_files.items(), key=lambda x: x[1][0])
    while len(work_list) > 0:
        item = work_list.pop()
        output_filename = args.output_pattern.format(item[0])
        log("Creating {0} from {1} input files ({2} bytes)".
            format(output_filename, len(item[1][1]), item[1][0]))
        output_file = None
        try:
            output_file = open(output_filename, "w")
            gzip = Popen(["gzip", "-cd"] + item[1][1], stdout=PIPE,
                         stderr=PIPE, bufsize=-1)
            bzip2 = Popen(["bzip2", "-c", "-9"], stdin=gzip.stdout,
                          stdout=output_file, stderr=PIPE)
            log("gzip returned {0}, bzip2 returned {1}".
                format(Popen.wait(gzip), Popen.wait(bzip2)))
            if gzip.returncode != 0:
                sys.stdout.write(Popen.communicate(gzip)[1])
            if bzip2.returncode != 0:
                sys.stdout.write(Popen.communicate(bzip2)[1])
            output_file.close()
        except Exception as e:
            log("Error writing {0}: {1}".format(output_filename, str(e)))
        finally:
            if output_file:
                output_file.close()

def main():
    parse_args()
    load_region_map()
    for year in range(args.start_year, args.end_year + 1):
        scan_input(year)
    create_output_files()
    log("Done")

if __name__ == '__main__':
    main()
