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
* Server-side presentation layer in [Django](https://www.djangoproject.com/)
* Client-side presentation using the
[Google Maps JavaScript API](https://developers.google.com/maps/documentation/javascript/)
* Automation with [Gradle](https://gradle.org/) and
[AWS CloudFormation](https://aws.amazon.com/cloudformation/)

The unimaginative project name was inspired by
[these little guys](http://www.hikari.org.nz/stuff/random/kitten_helpers.jpg)
who enjoy climbing onto my lap when I'm trying to code.

## Datasets

The NCDC data comprises historic observations from (mostly fixed) weather
stations around the world. The data runs from 1901 to the present day, but
since I'm interested in annual trends I only take it up to the end of 2017.
This is still large enough to be interesting, giving us a little over 3.1
billion observations from around 32,000 stations.

By contrast, the CCAFS data comprises global predictions for future climate.
The overall dataset is
[huge](http://www.ccafs-climate.org/downloads/docs/mapping_data_ccafs-climate.pdf),
so to keep things manageable I've decided to focus on the 19
[bioclimatic variables](http://www.ccafs-climate.org/downloads/docs/bioclimatic-variables.pdf)
derived from data used by the
[IPCC Fifth Assessment Report](https://www.ipcc.ch/report/ar5/) (IPCC AR5). The
AR5 data is generated from the [CMIP5](https://esgf-node.llnl.gov/projects/cmip5/)
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

## Processing Steps

1. [Cluster setup with CloudFormation](cloudformation)
2. [NCDC Download](ncdc_download)
3. [NCDC Record Count](ncdc_count)

## To Do

[All the things](http://knowyourmeme.com/memes/all-the-things)
