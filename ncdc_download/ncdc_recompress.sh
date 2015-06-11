#!/bin/sh

# Read the gzipped NCDC data files downloaded by ncdc_download.sh, accumulate
# their contents by station ID, and bzip all the data for each station into a
# single file in the appropriate CCAFS region directory (see comments in
# gen_station_regions.py for details).
#
# To run this in parallel:
#
#   find /mnt/work/stage/ -type f | cut -d/ -f6 | cut -c-12 | sort -u | \
#      split -d -n r/4 - stations_
#   for i in `seq -f %02.0f 0 3`
#   do
#      sh ncdc_recompress.sh < stations_$i > recomp_$i.log 2>&1 &
#   done

src=/mnt/work/stage
dest=/mnt/work/data
lookup=$HOME/station_regions.txt

while read station
do
	echo `date` Recompressing $station
	region=`grep $station $lookup | cut -f2`
	region=${region:-D}
	gzip -cd `find $src -name $station\*` | \
		bzip2 -c -9 >> $dest/$region/$station.bz2
done
echo `date` Done
