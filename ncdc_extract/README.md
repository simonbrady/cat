# NCDC Extract

Extract NCDC records for a given list of station IDs. For example, given the input list
```
# Comments and blank lines are ignored
029070-99999   So is everything after the first occurrence of whitespace
029500-99999
```
the job will create an output file for each station that appears at least once in
the input. 

To build the code and upload it to S3 where EMR can find it, do:
```
make upload
```

By default the job will read from and write to S3:
```
make extract
```

This can be overridden, e.g. if you've already copied the input files to HDFS:
```
STATIONS=stations INPUT="1901-1910 1911-1930" make extract
```

The job runs as the default `hadoop` user so it would look for these input paths
under `/user/hadoop` in HDFS.
