# NCDC Download

Due to the size of the datasets it's easiest to host the project in the
[Amazon Web Services](http://aws.amazon.com/) cloud. The CCAFS data is already
available as an
[AWS public dataset](https://registry.opendata.aws/cgiardata/), but the
NCDC data is spread over more than 630,000 small files on the NOAA FTP
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

One advantage of streaming is that you can run the mappers directly from the command
line to test small jobs. For example, this will download all 65570 records for 1901-1910
to a single 9.2 MB uncompressed file:
```
cd src/main/python
seq 1901 1910 | python3 download_mapper1.py | python3 download_mapper2.py > 1901-1910.txt
```

Because of the way Hadoop splits input to map tasks, there can be multiple output files
for a single year (one for each mapper that processed files for that year). To direct
map output to different directories I use a small Java class that implements a custom
output format.

Processing is driven by `make` commands. After deploying an EMR cluster (e.g. using
the included [Terraform template](../terraform)), build and upload the
required code to S3:
```
make upload
```

You can then run a download job to transfer files to S3 (destination path is
specified in [common.mk](../common.mk)):
```
make download
```

By default the job will download data for 1901 to 1910 inclusive. To override this
range set the appropriate Makefile variables - for example, to download the entire
dataset up to the end of 2019 I did:
```
TO=2019 MAPS=300 make download
```

This took about 24 hours on a cluster of two m4.large nodes in us-east-1 (even if
that isn't your local region, FTP is so slow in the face of network latency that
it's worth running the download from there).

To scale jobs up without breaking the bank it's worth having a range of input datasets.
As an example these are the subsets I use:

|Years    |Files on FTP Site|Stations Included|Records      |Compressed Size|
|---------|----------------:|----------------:|------------:|--------------:|
|1901-1910|               60|               13|       65,570|         390 KB|
|1901-1930|              472|              144|      326,261|         2.5 MB|
|1901-1950|           22,025|            4,880|   55,528,105|         603 MB|
|1901-1970|           95,419|            9,893|  255,143,894|         3.2 GB|
|1901-1990|          284,350|           19,234|  847,649,686|        12.0 GB|
|1901-2019|          630,259|           30,804|3,164,850,728|        57.4 GB|

Once you have the data in S3, you can use
```
make copy
```

to copy it to HDFS using
[s3-dist-cp](https://docs.aws.amazon.com/emr/latest/ReleaseGuide/UsingEMR_s3distcp.html) -
see the [Makefile](Makefile) for the variables to set.

## Performance

The code has been kept as simple as possible to favour clarity and robustness
over performance. The main bottleneck is that the NOAA website only allows three
concurrent FTP connections from a single IP, which restricts the number of map
tasks we can run at once. The mappers themselves alternate between downloading
each small file from the site, decompressing it from gzip format, and adding its
content to a much smaller number of bzip2 archives.

While this slows the process down, it does do NOAA the courtesy of reducing the
load on their public FTP server, which is largely why I haven't tried to optimise
things.

That said, the obvious way to shorten runtime (but not necessarily lower cost) is
to separate the download and decompress/recompress parts. We would then have a
small number of mappers dedicated to FTP transfers feeding a larger number
of compression tasks running in parallel. The challenge is that the mapper output
should remain in gzip format, because decompressing the files at this stage would
lead to a massive increase in I/O within the cluster that would probably outweigh
the benefits of parallel recompression.

Streaming is best suited for text input and output, so for binary output we could
code the mapper in Java (using say the
[Apache Commons Net](http://commons.apache.org/proper/commons-net/) `FTPClient`
class), with output values of type `BytesWritable`. We could then have a larger
number of reducers decompressing the gzip data they receive and writing text
output for the framework to compress to bzip2 format. Because MapReduce doesn't
know when it's seen the last key for a partition this might still lead to a large
build-up of mapper output on local disk that you'd need to size the cluster nodes
for.
