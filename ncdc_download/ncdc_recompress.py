#!/usr/bin/env python

import argparse
from datetime import datetime
import glob
import os
import stat
from subprocess import PIPE, Popen
import sys
import time

# Command line arguments
args = None

# Station ID to region map
region_map = {}

# Input files for each region encountered
input_files = {}

# Active compression worker tasks, stored as tuples of (gzip process, bzip2
# process, output filename, output file)
workers = []

# Range-checked integer command line arguments, inspired by
# http://stackoverflow.com/questions/12116685/
def positive_int(arg):
    val = int(arg)
    if val > 0:
        return val
    else:
        raise argparse.ArgumentTypeError("{0} is not a positive integer".
                                         format(arg))

# Parse command line and set up args global variable with result
def parse_args():
    global args
    parser = argparse.ArgumentParser()
    output_opts = parser.add_mutually_exclusive_group()
    output_opts.add_argument("-q", "--quiet", action="store_true",
                             help="suppress normal output")
    output_opts.add_argument("-v", "--verbose", action="store_true",
                             help="verbose output")
    parser.add_argument("-p", "--poll-interval", type=positive_int, default=10,
                        help="seconds between polling workers (default 10)")
    parser.add_argument("-r", "--region-map", type=str,
                        default="station_regions.txt", help="file of station" +
                            "-to-region mappings, default station_regions.txt")
    parser.add_argument("-w", "--workers", type=positive_int, default=1,
                        help="number of compression worker tasks (default 1)")
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
    if not args.quiet:
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
                input_files[region] = [[], 0]
            input_files[region][0].append(filename)
            input_files[region][1] += size
    except Exception as e:
        fatal("Error processing {0}: {1}".format(year, str(e)))

def add_worker(region, input_files, size):
    global workers
    output_filename = args.output_pattern.format(region)
    log("Creating {0} from {1} input files ({2} bytes)".
        format(output_filename, len(input_files), size))
    try:
        output_file = open(output_filename, "w")
        gzip = Popen(["gzip", "-cd"] + input_files, stdout=PIPE,
                     stderr=PIPE, bufsize=-1)
        bzip2 = Popen(["bzip2", "-c", "-9"], stdin=gzip.stdout,
                      stdout=output_file, stderr=PIPE)
        workers.append((gzip, bzip2, output_filename, output_file))
    except Exception as e:
        fatal("Error creating {0}: {1}".format(output_filename, str(e)))

def wait_for_worker():
    global workers
    completed = False
    while not completed:
        if args.verbose:
            log("Waiting for worker task to complete ({0} active)".
                format(len(workers)))
        time.sleep(args.poll_interval)
        for worker in workers:
            gzip, bzip2, output_filename, output_file = worker
            if Popen.poll(gzip) == None and Popen.poll(bzip2) == None:
                continue
            log("Created {0}: gzip returned {1}, bzip2 returned {2}".
                format(output_filename, Popen.wait(gzip), Popen.wait(bzip2)))
            if gzip.returncode != 0:
                sys.stdout.write(Popen.communicate(gzip)[1])
            if bzip2.returncode != 0:
                sys.stdout.write(Popen.communicate(bzip2)[1])
            output_file.close()
            workers.remove(worker)
            completed = True

def create_output_files():
    work_list = sorted(input_files.items(), key=lambda x: x[1][1])
    while len(work_list) > 0:
        # Wait for a free worker task slot
        while len(workers) == args.workers:
            wait_for_worker()
        item = work_list.pop()
        add_worker(item[0], item[1][0], item[1][1])
    # No more work to add, so wait for remaining workers to finish
    while len(workers) > 0:
        wait_for_worker()

def main():
    start_time = datetime.now()
    parse_args()
    load_region_map()
    for year in range(args.start_year, args.end_year + 1):
        scan_input(year)
    create_output_files()
    log("Done (elapsed time {0})".format(str(datetime.now() - start_time)))

if __name__ == '__main__':
    main()
