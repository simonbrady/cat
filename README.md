# Climate Analysis Tool

This is an ongoing project of mine to build a web app fusing two non-trivial
climate data sets, [NCDC ISD](http://www.ncdc.noaa.gov/isd) and
[CCAFS-CGIAR](http://www.ccafs-climate.org/). While the data is inherently
interesting (at least to me), the main purpose of the project is to demonstrate
a number of technologies I like working with:

* Back-end data crunching with
[Elastic MapReduce](https://aws.amazon.com/elasticmapreduce/) (Amazon's hosted
version of [Hadoop](http://hadoop.apache.org/)),
Oracle [database](https://www.oracle.com/database/) and
[Big Data Connectors](http://www.oracle.com/technetwork/database/database-technologies/bdc/big-data-connectors/overview/),
and a bit of Fortran (there's life in the old dog yet!)
* A Java mid-tier hosted on
[WebLogic Server](http://www.oracle.com/technetwork/middleware/weblogic/overview/),
using [Jersey](https://jersey.java.net/) and
[Jackson](https://github.com/FasterXML/jackson) to publish and consume RESTful
web services
* Server-side presentation layer in [Rails](http://rubyonrails.org/)
* Client-side presentation using the
[Google Maps JavaScript API](https://developers.google.com/maps/documentation/javascript/)

The unimaginative project acronym is thanks to
[these little guys](http://www.hikari.org.nz/stuff/random/kitten_helpers.jpg)
who enjoy climbing onto my lap when I'm trying to code.

## Datasets

The NCDC data comprises historic observations from (mostly fixed) weather
stations around the world. The data runs from 1901 to the present day, but
since I'm interested in annual trends I only take it up to the end of 2014.
This is still large enough to be interesting, giving us a little over 2.7
billion observations from around 30,000 stations.

By contrast, the CCAFS data comprises global predictions for future climate.
The overall dataset is
[huge](http://www.ccafs-climate.org/downloads/docs/mapping_data_ccafs-climate.pdf),
so to keep things manageable I've decided to focus on the 19
[bioclimatic variables](http://www.ccafs-climate.org/downloads/docs/bioclimatic-variables.pdf)
derived from data used by the
[IPCC Fifth Assessment Report](https://www.ipcc.ch/report/ar5/) (IPCC AR5). The
AR5 data is generated from the [CMIP5](http://cmip-pcmdi.llnl.gov/cmip5/)
ensemble of general circulation models (GCMs) under various scenarios, then
[downscaled](http://www.ccafs-climate.org/statistical_downscaling_delta_cmip5/)
to finer spatial resolution.
 
With the two datasets being so different, how can we meaningfully combine them?
A couple of approaches come to mind:

1. Display NCDC stations on the map, overlaid with images derived from the
CCAFS data (e.g. predicted temperature maps), and let the user drill down by
station to see historical information for areas the CCAFS data highlights as
interesting

2. As above, but spatially interpolate the CCAFS data to predict future
conditions at individual station locations and compare these to historical
patterns. Interpolation is necessary because NCDC coordinates are given to a
resolution of 0.001 degrees, while the finest-grained CCAFS data is on a
30 arc second grid (approximately 0.00833 degrees).

Once the back-end is up and running with actual data, other ideas will
hopefully present themselves.

## Preprocessing

Due to the size of the datasets and the speed of New Zealand domestic broadband
it's easiest to host the project in the
[Amazon Web Services](http://aws.amazon.com/) cloud. The CCAFS data is already
available as an
[AWS public dataset](http://aws.amazon.com/datasets/0241269495883982), but the
NCDC data is published as 500,000+ small files on the NOAA FTP site
(`ftp://ftp.ncdc.noaa.gov/pub/data/noaa/`, which Markdown
[won't link to](https://github.com/jch/html-pipeline/issues/187)).
To avoid downloading
these files every time I need them, the first step in the project is to
script a bulk download and restructuring of the raw data. The NCDC files are
gzipped text, one file per station per year, so after downloading them I
combine all the records for a station into a single file then recompress
them with bzip2 (this reduces 81 GB of downloaded data to 49 GB, and since
bzip2 is splittable it's much more Hadoop-friendly than gzip).

The scripts to do this are in the `ncdc_download` directory. In addition to
recompressing, the second stage sorts the output
files into bins based on the CCAFS region containing the station (CCAFS data
is available in "tiles" covering 50 degrees of latitude by 60 degress of
longitude, from the north pole to 60 degrees south). This binning makes it
easy for Hadoop jobs to operate on data one region at a time, which is
especially useful when combining NCDC data with a CCAFS tile. The
[gen\_station\_regions.py](ncdc\_download/gen\_station\_regions.py) script
reads the NCDC station list `isd-history.csv`
and produces a station-to-region lookup file to drive the binning process. 

As a guide, downloading the data from the NOAA server to an Amazon EC2 instance
took me the better part of a day (mostly because I did it in small chunks to
avoid hitting FTP connection limits). Once I had the raw data on an EBS volume
it took about 3 hours to copy it into memory on an `r3.8xlarge` instance (32
virtual CPUs and 244GB RAM, with 200GB mounted as tmpfs), then process it with
16 recompress jobs running in parallel. Your mileage may vary.
 
## To Do

Lots and lots of stuff to finish off, tidy up, and publish on GitHub. Stay
tuned!
