# NCDC Download

Due to the size of the datasets and the speed of New Zealand domestic broadband
it's easiest to host the project in the
[Amazon Web Services](http://aws.amazon.com/) cloud. The CCAFS data is already
available as an
[AWS public dataset](http://aws.amazon.com/datasets/0241269495883982), but the
NCDC data is published as 500,000+ small files on the NOAA FTP site
(`ftp://ftp.ncdc.noaa.gov/pub/data/noaa/`, which Markdown
[won't link to](https://github.com/jch/html-pipeline/issues/187)).

To avoid downloading
these files every time I need them, the first step in the process is to
script a bulk download and restructuring of the raw data. The NCDC files are
gzipped text, one file per station per year, so after downloading them I
add all the records for a station to a single file corresponding to the
station's CCAFS region (CCAFS data is available in "tiles" covering 50 degrees
of latitude by 60 degress of longitude, from the north pole to 60 degrees
south). The [gen\_station\_regions.py](gen\_station\_regions.py)
script reads the NCDC station list `isd-history.csv` and produces a
station-to-region lookup file to drive the binning process. This binning makes
it easy for Hadoop jobs to operate on data one region at a time, which is
especially useful when combining NCDC data with a CCAFS tile.

The region files
are then recompressed with bzip2, which reduces 81 GB of downloaded data to
49 GB. Since bzip2 is splittable it's much more Hadoop-friendly than gzip:
the large region files can be split into 128 MB HDFS blocks for parallel
processing by Hadoop map tasks.
