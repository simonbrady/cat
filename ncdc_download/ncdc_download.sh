#!/bin/sh

# Download all NCDC files for the input year(s). Example usage:
#
#   seq 1901 2014 | sh ncdc_download.sh > ncdc_download.log 2>&1
#
# then tail -f download.log to keep an eye on progress.

# Staging directory to work in
dest=/mnt/work/stage

pushd $dest
while read year
do
	rm -Rf $year
	echo `date` Started download for $year
	wget -nv -r -nH --cut-dirs=3 --timeout=180 \
		ftp://ftp.ncdc.noaa.gov/pub/data/noaa/$year
	echo `date` Finished download for $year
done
popd
echo `date` Done
