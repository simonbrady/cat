# NCDC Record Count

This is a simple Hadoop job to run over the downloaded NCDC data, heavily based
on the examples in Tom White,
[_Hadoop: The Definitive Guide_](http://hadoopbook.com/) (4th ed: O'Reilly,
2015). It counts records by station ID (the concatenation of a station's USAF
catalogue number and WBAN identifier, e.g. 029070-99999) and produces
tab-delimited ID-count pairs as output. Its main purpose is to sanity-check the
data and Hadoop configuration.

To build the code and upload it to S3 where EMR can find it, do:
```
make upload
```

By default the job will read from and write to S3:
```
make count
```

This can be overridden, e.g. if you've already copied the input files to HDFS:
```
INPUT="1901-1910 1911-1930" make count
```

The job runs as the default `hadoop` user so it would like for these input paths
under `/user/hadoop` in HDFS.
