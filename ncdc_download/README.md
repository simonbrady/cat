# NCDC Download

Due to the size of the datasets it's easiest to host the project in the
[Amazon Web Services](http://aws.amazon.com/) cloud. The CCAFS data is already
available as an
[AWS public dataset](http://aws.amazon.com/datasets/0241269495883982), but the
NCDC data is spread over more than half a million small files on the NOAA FTP
site (`ftp://ftp.ncdc.noaa.gov/pub/data/noaa/`, which Markdown
[won't link to](https://github.com/jch/html-pipeline/issues/187)).

To avoid downloading these files every time I need them, the first step is
to download them to S3 and aggregate them into larger chunks that are easier
to process with Hadoop. I do this with two map-only
[Hadoop Streaming](http://hadoop.apache.org/docs/stable/hadoop-streaming/HadoopStreaming.html)
jobs:

1. Take a list of years and produce a list of (year, filename) key-value pairs as input
to the second step.
2. Download each listed filename and add it to a bzip2-compressed output file, with all
the files for each year in their own subdirectory.

Because of the way Hadoop splits input to map tasks, there can be multiple output files
for a single year (one for each mapper that processed files for that year). To direct
map output to different directories I use a small Java class that implements a custom
output format.

Processing is driven by `make` commands. After deploying an EMR cluster (e.g. using
the included [CloudFormation template](../cloudformation), build and upload the
required code to S3:
```
make upload
```

You can then run a download job to transfer files to S3 (destination bucket can be
specified in [common.mk](../common.mk)):
```
make download
```

By default the job will download data for 1901 to 1910 inclusive. To override this
range set the appropriate Makefile variables - for example, to download the entire
dataset up to the end of 2017 I did:
```
FROM=1901 TO=2017 MAPS=300 make download
```

This took about 25 hours on a cluster of two m4.large nodes in us-east-1 (even if
that isn't your local region, FTP is so slow in the face of network latency that
it's worth running the download from there).

To scale jobs up without breaking the bank it's worth having a range of input datasets.
As a rough guide these are the sizes I use:

|Years    |Stations Included|Records      |Compressed Size:|
|---------|----------------:|------------:|---------------:|
|1901-1910|               13|       65,570|          390 KB|
|1901-1930|              144|      326,261|          2.5 MB|
|1901-1950|            4,880|   55,528,105|          604 MB|
|1901-1970|            9,893|  255,143,894|          3.2 GB|
|1901-1990|           19,234|  853,164,630|         12.1 GB|
|1901-2017|           31,741|3,126,682,587|         56.8 GB|

Once you have the data in S3, you can use
```
make copy
```

to copy it to HDFS using
[s3-dist-cp](https://docs.aws.amazon.com/emr/latest/ReleaseGuide/UsingEMR_s3distcp.html) -
see the [Makefile](Makefile) for the variables to set.
