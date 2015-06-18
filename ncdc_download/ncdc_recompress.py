#!/usr/bin/env python

import argparse
from datetime import datetime
import glob
import os
import stat
from subprocess import check_call, PIPE, Popen
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
compress_workers = []

# Active concatenation worker tasks, stored as tuples of (cat process, input
# filenames, output filename, output file)
concat_workers = []

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
    parser.add_argument("-f", "--file-count", type=positive_int, default=20000,
                        help="input files per worker task (default 20000)")
    parser.add_argument("-p", "--poll-interval", type=positive_int, default=10,
                        help="seconds between polling workers (default 10)")
    parser.add_argument("-r", "--region-map", type=str,
                        default="station_regions.txt", help="file of station" +
                            "-to-region mappings, default station_regions.txt")
    parser.add_argument("-w", "--workers", type=positive_int, default=1,
                        help="number of worker tasks (default 1)")
    parser.add_argument("source_dir", type=str,
                        help="directory of NCDC files, one subdir per year")
    parser.add_argument("output_pattern", type=str,
                        help="output filename pattern, e.g. 'ncdc_{0}.bz2'")
    parser.add_argument("start_year", type=int,
                        help="first year of files to process")
    parser.add_argument("end_year", type=int,
                        help="last year of files to process")
    args = parser.parse_args()

def log(msg, flush=False):
    if not args.quiet:
        print datetime.now().ctime(), msg
    if flush:
        sys.stdout.flush()

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
                input_files[region] = []
            input_files[region].append((filename, size))
    except Exception as e:
        fatal("Error processing {0}/{1}: {1}".
              format(args.source_dir,year, str(e)))

def add_compress_worker(output_filename, files):
    global compress_workers
    try:
        output_file = open(output_filename, "w")
        gzip = Popen(["gzip", "-cd"] + list(files), stdout=PIPE, stderr=PIPE,
                     bufsize=-1)
        bzip2 = Popen(["bzip2", "-c", "-9"], stdin=gzip.stdout,
                      stdout=output_file, stderr=PIPE)
        compress_workers.append((gzip, bzip2, output_filename, output_file))
    except Exception as e:
        fatal("Error creating {0}: {1}".format(output_filename, str(e)))

def wait_for_compress_worker():
    global compress_workers
    completed = False
    while not completed:
        if args.verbose:
            log("Waiting for compression task to complete ({0} active)".
                format(len(compress_workers)), True)
        time.sleep(args.poll_interval)
        for worker in compress_workers:
            gzip, bzip2, output_filename, output_file = worker
            if Popen.poll(gzip) == None and Popen.poll(bzip2) == None:
                continue
            output_file.close()
            log("Created {0}: gzip returned {1}, bzip2 returned {2}".
                format(output_filename, Popen.wait(gzip), Popen.wait(bzip2)))
            if gzip.returncode != 0:
                sys.stdout.write(Popen.communicate(gzip)[1])
            if bzip2.returncode != 0:
                sys.stdout.write(Popen.communicate(bzip2)[1])
            compress_workers.remove(worker)
            completed = True

def compress_files():
    global input_files
    work_list = []
    for (region, file_list) in input_files.items():
        start = 0
        chunk = 0
        while start < len(file_list):
            output_filename = args.output_pattern. \
                format("{0}_{1:03d}".format(region, chunk))
            end = start + min(len(file_list) - start, args.file_count)
            count = end - start
            files = (x[0] for x in file_list[start:end])
            size = sum(x[1] for x in file_list[start:end])
            work_list.append((output_filename, files, count, size))
            start = end
            chunk += 1
    # Sort in ascending order of input size
    work_list.sort(key=lambda x: x[3])
    # Assign compression work to compress_workers as they become available
    while len(work_list) > 0:
        # Wait for a free worker task slot
        while len(compress_workers) == args.workers:
            wait_for_compress_worker()
        output_filename, files, count, size = work_list.pop()
        log("Creating {0} from {1} input files ({2} bytes)".
            format(output_filename, count, size))
        add_compress_worker(output_filename, files)
    # No more compression to do, so wait for remaining workers to finish
    while len(compress_workers) > 0:
        wait_for_compress_worker()

def add_concat_worker(output_filename, files):
    global concat_workers
    try:
        output_file = open(output_filename, "w")
        cat = Popen(["cat"] + list(files), stdout=output_file, stderr=PIPE)
        concat_workers.append((cat, files, output_filename, output_file))
    except Exception as e:
        fatal("Error creating {0}: {1}".format(output_filename, str(e)))

def wait_for_concat_worker():
    global concat_workers
    completed = False
    while not completed:
        if args.verbose:
            log("Waiting for concatenation task to complete ({0} active)".
                format(len(concat_workers)), True)
        time.sleep(args.poll_interval)
        for worker in concat_workers:
            cat, files, output_filename, output_file = worker
            if Popen.poll(cat) == None:
                continue
            output_file.close()
            log("Created {0}: cat returned {1}".
                format(output_filename, Popen.wait(cat)))
            if cat.returncode != 0:
                sys.stdout.write(Popen.communicate(cat)[1])
            file_list = " ".join(files)
            try:
                check_call(["rm"] + files)
                if args.verbose:
                    log("Removed " + file_list)
                else:
                    log("Removed {0} intermediate files".format(len(files)))
            except Exception as e:
                fatal("Error removing {0}: {1}".format(file_list, str(e)))
            concat_workers.remove(worker)
            completed = True

def concat_files():
    global concat_workers
    work_list = []
    for region in input_files.keys():
        output_filename = args.output_pattern.format(region)
        files = glob.glob(args.output_pattern.format("{0}_*".format(region)))
        work_list.append((output_filename, files))
    # Sort in ascending order of number of files 
    work_list.sort(key=lambda x: len(x[1]))
    # Assign concatenation work to workers as they become available
    while len(work_list) > 0:
        # Wait for a free worker task slot
        while len(concat_workers) == args.workers:
            wait_for_concat_worker()
        output_filename, files = work_list.pop()
        log("Concatenating {0} input files to {1}".
            format(len(files), output_filename))
        add_concat_worker(output_filename, files)
    # No more concatenation, so wait for remaining workers to finish
    while len(concat_workers) > 0:
        wait_for_concat_worker()

def main():
    start_time = datetime.now()
    parse_args()
    load_region_map()
    for year in range(args.start_year, args.end_year + 1):
        scan_input(year)
    compress_files()
    concat_files()
    log("Done (elapsed time {0})".format(str(datetime.now() - start_time)))

if __name__ == '__main__':
    main()
