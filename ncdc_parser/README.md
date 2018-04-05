# NCDC Parser

This will hold a MapReduce job to read the raw NCDC files from S3 and process
them into an easier-to-use form (e.g. CSV or JSON instead of fixed-width text).

Part of this processing will be to match each station with its corresponding
CCAFS region (CCAFS data is available in "tiles" covering 50 degrees
of latitude by 60 degrees of longitude, from the north pole to 60 degrees
south). The [gen\_station\_regions.py](gen\_station\_regions.py)
script reads the NCDC station list `isd-history.csv` and produces a
station-to-region lookup file to assist the matching process. This binning
into regions will make it easier for Hadoop jobs to operate on data one region
at a time, which is especially useful when combining NCDC data with a CCAFS tile.
