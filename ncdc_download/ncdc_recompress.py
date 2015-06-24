#!/usr/bin/env python

# Combine downloaded NCDC data files by CCAFS region and recompress them as
# bzip2 archives, one file per region. The station-to-region mapping is driven
# by a lookup file created by gen_station_regions.py (see that file for an
# explanation of CCAFS region codes).
#
# Because the large number of input files for one region can exceed kernel
# limits on the length of a process argument list, we proceed as follows:
#
#  1. Scan the NCDC input directories for each year of interest, and for each
#     file found record its pathname and size under the appropriate region
#     key in the input_details dictionary.
#
#  2. For each region, read and recompress its input files in chunks of 20000
#     (by default) to an intermediate bzip2 file.
#
#  3. Concatenate the intermediate files for each region into a single output
#     file. This works because bzip2 treats concatenated archives as a single
#     valid archive.
#
# Steps 2 and 3 are performed in parallel using a configurable number of
# asynchronous subprocesses.

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

# Input files and sizes for each region encountered
input_details = {}

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

# Load the station-to-region mapping file created by gen_station_regions.py
# into a dictionary keyed by station ID
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

# Scan a subdirectory of NCDC files for the given year and add details for each
# file to the appropriate region key of input_files. For each file we record
# its absolute pathname and size in bytes as a tuple appended to the region's
# value. Region keys and value lists are created as needed. Any station ID
# missing from region_map (and hence from isd-history.csv on the NCDC FTP site)
# is assigned to pseudo-region E.
def scan_input(year):
    global input_details
    log("Scanning {0}/{1}".format(args.source_dir, year))
    try:
        for filename in glob.glob("{0}/{1}/*.gz".format(args.source_dir, year)):
            # Strip "-YYYY.gz" suffix off filename
            station = os.path.basename(filename)[:-8]
            region = region_map.get(station, "E")
            size = os.stat(filename)[stat.ST_SIZE]
            if input_details.get(region) == None:
                input_details[region] = []
            input_details[region].append((filename, size))
    except Exception as e:
        fatal("Error processing {0}/{1}: {1}".
              format(args.source_dir,year, str(e)))

# Start a compression worker task to decompress the listed input files and
# recompress them as a single bzip2 archive, then append the task details to
# compress_workers to be waited on by wait_for_compress_worker()
def add_compress_worker(input_filenames, output_filename):
    global compress_workers
    try:
        output_file = open(output_filename, "w")
        gzip = Popen(["gzip", "-cd"] + list(input_filenames), stdout=PIPE,
                     stderr=PIPE, bufsize=-1)
        bzip2 = Popen(["bzip2", "-c9"], stdin=gzip.stdout,
                      stdout=output_file, stderr=PIPE)
        compress_workers.append((gzip, bzip2, output_filename, output_file))
    except Exception as e:
        fatal("Error creating {0}: {1}".format(output_filename, str(e)))

# Wait for a compression worker task to complete then report its completion
# status. All tasks in compress_workers are polled until one completes. Since
# any failure in this process is likely to have a fundamental cause, e.g. wrong
# input directory given or output disk full, we quit with a fatal error should
# any single worker fail.
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
            # Get subprocess return codes, or None if they're still running
            gzip_rc = Popen.poll(gzip)
            bzip2_rc = Popen.poll(bzip2)
            # If both subprocesses are still running, try the next worker task
            if gzip_rc == None and bzip2_rc == None:
                continue
            # At least one subprocess for this task has completed, but the
            # other may still be running. If one of them has completed
            # successfully then wait for the other to finish.
            if gzip_rc == 0:
                bzip2_rc = Popen.wait(bzip2)
            elif bzip2_rc == 0:
                gzip_rc = Popen.wait(gzip)
            # In some failure modes one subprocess will fail but leave the
            # other running, so check for this and terminate the hung process
            # if necessary.
            if gzip_rc != None and gzip_rc != 0 and bzip2_rc == None:
                Popen.terminate(bzip2)
                bzip2_rc = 0
            elif bzip2_rc != None and bzip2_rc != 0 and gzip_rc == None:
                Popen.terminate(gzip)
                gzip_rc = 0
            # Either way both processes should now have finished, so close the
            # output file
            assert gzip_rc != None and bzip2_rc != None
            output_file.close()
            # If a subprocess failed, include its stderr output in the error
            # message as we die
            if gzip_rc != 0:
                fatal("gzip failed creating {0}: {1}".
                      format(output_filename, Popen.communicate(gzip)[1]))
            if bzip2_rc != 0:
                fatal("bzip2 failed creating {0}: {1}".
                      format(output_filename, Popen.communicate(bzip2)[1]))
            compress_workers.remove(worker)
            log("Created {0}".format(output_filename))
            completed = True

# For each region, decompress all the gzipped input files for stations in that
# region then append them and recompress with bzip2. Ideally we'd process all
# the inputs at once but this would lead to to gzip being called with an
# argument list too long for the underlying execve() call, so we process the
# input list in chunks and leave them for concat_files() to merge later.
# Recompression is done with asynchronous subprocesses, up to the user-
# specified maximum number of workers, where each worker task is similar to
#
#   gzip -cd input1.gz input2.gz ... inputN.gz | bzip2 -c9 > output.bz2
#
def compress_files():
    global input_details
    work_list = []
    for (region, file_list) in input_details.items():
        start = 0
        chunk = 0
        while start < len(file_list):
            output_filename = args.output_pattern. \
                format("{0}_{1:03d}".format(region, chunk))
            end = start + min(len(file_list) - start, args.file_count)
            count = end - start
            input_filenames = (x[0] for x in file_list[start:end])
            size = sum(x[1] for x in file_list[start:end])
            work_list.append((output_filename, input_filenames, count, size))
            start = end
            chunk += 1
    # Sort in ascending order of input size
    work_list.sort(key=lambda x: x[3])
    # Assign compression work to workers as they become available, in
    # descending order of input size. Assigning work this way achieves a near-
    # optimal balance across workers (see the discussion of the "longest
    # processing time first" rule in Sedgewick and Wayne, "Algorithms"
    # (4th ed: Addison Wesley, 2011), p349).
    while len(work_list) > 0:
        # Wait for a free worker task slot
        while len(compress_workers) == args.workers:
            wait_for_compress_worker()
        output_filename, input_filenames, count, size = work_list.pop()
        log("Creating {0} from {1} input files ({2} bytes)".
            format(output_filename, count, size))
        add_compress_worker(input_filenames, output_filename)
    # No more compression to do, so wait for remaining workers to finish
    while len(compress_workers) > 0:
        wait_for_compress_worker()

# Start a worker task to concatenate the listed input files together as a
# single output file, then append the task details to concat_workers to be
# waited on by wait_for_concat_worker()
def add_concat_worker(input_filenames, output_filename):
    global concat_workers
    try:
        output_file = open(output_filename, "w")
        cat = Popen(["cat"] + list(input_filenames), stdout=output_file,
                    stderr=PIPE)
        concat_workers.append((cat, input_filenames, output_filename,
                               output_file))
    except Exception as e:
        fatal("Error creating {0}: {1}".format(output_filename, str(e)))

# Wait for a concatenation worker task to complete, report its completion
# status, and remove its input files. All tasks in concat_workers are polled
# until one completes.
def wait_for_concat_worker():
    global concat_workers
    completed = False
    while not completed:
        if args.verbose:
            log("Waiting for concatenation task to complete ({0} active)".
                format(len(concat_workers)), True)
        time.sleep(args.poll_interval)
        for worker in concat_workers:
            cat, input_filenames, output_filename, output_file = worker
            # Get subprocess return code, or None if it's still running
            cat_rc = Popen.poll(cat)
            # Try next worker if this one hasn't finished yet
            if cat_rc == None:
                continue
            output_file.close()
            # If the process failed then quit and include its stderr in the
            # error message
            if cat_rc != 0:
                fatal("cat failed creating {0}: {1}".
                      format(output_filename, Popen.communicate(cat)[1]))
            log("Created " + output_filename)
            # Now delete the input files
            input_filenames.sort()
            file_list = " ".join(input_filenames)
            try:
                check_call(["rm"] + input_filenames)
                log("Removed " + file_list)
            except Exception as e:
                fatal("Error removing {0}: {1}".format(file_list, str(e)))
            concat_workers.remove(worker)
            completed = True

# For each region we've processed, concatenate its intermediate .bz2 files into
# a single archive then delete them. This is equivalent to (for exanple)
#
#   cat ncdc_A1_000.bz2 ncdc_A1_001.bz2 > ncdc_A1.bz2
#   rm ncdc_A1_000.bz2 ncdc_A1_001.bz2
#
# Concatenation is done using asynchronous subprocesses, up to the user-
# specified maximum number of worker tasks.
def concat_files():
    global concat_workers
    work_list = []
    for region in input_details.keys():
        input_filenames = glob.glob(args.output_pattern.
                                    format("{0}_*".format(region)))
        output_filename = args.output_pattern.format(region)
        work_list.append((input_filenames, output_filename))
    # Sort work list in ascending order of number of input_filenames
    work_list.sort(key=lambda x: len(x[0]))
    # Assign concatenation work to workers as they become available, starting
    # with the longest list of inputs and ending with the shortest to keep
    # things balanced
    while len(work_list) > 0:
        # Wait for a free worker task slot
        while len(concat_workers) == args.workers:
            wait_for_concat_worker()
        input_filenames, output_filename = work_list.pop()
        log("Concatenating {0} input files to {1}".
            format(len(input_filenames), output_filename))
        # Start the new worker
        add_concat_worker(input_filenames, output_filename)
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
