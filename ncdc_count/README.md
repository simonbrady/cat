# NCDC Record Count

This is a simple Hadoop job to run over the downloaded NCDC data, heavily based
on the examples in Tom White, _Hadoop: the Definitive Guide_ (3rd ed: O'Reilly,
2012). It counts records by station ID (the concatenation of a station's USAF
catalogue number and WBAN identifier, e.g. 029070-99999) and produces
tab-delimted ID-count pairs as output. Its main purpose is to sanity-check the
data and Hadoop configuration.

The code can be built in Eclipse or from the command line with Maven (this is
automated by the [Makefile](Makefile) so you can build everything from the
top-level project directory). The output is a JAR archive,
`target/ncdc_count-VERSION.jar` to submit to Hadoop. I've used Hadoop 2.4.0
as bundled with the
[Elastic MapReduce AMI 3.7.0](http://docs.aws.amazon.com/ElasticMapReduce/latest/DeveloperGuide/ami-versions-supported.html),
but the code is so simple that any Hadoop version should work (you'll just need
to update the Maven dependency in [pom.xml](pom.xml)).

To run the job from the command line, install and configure the
[AWS CLI](http://aws.amazon.com/documentation/cli/) then set up your
[EMR default roles](http://docs.aws.amazon.com/cli/latest/reference/emr/create-default-roles.html)
if you haven't already done so:
```
aws emr create-default-roles
```
Next, start up a small cluster:
```
S3=s3://BUCKETNAME/ncdc

aws emr create-cluster --ami-version 3.7.0 --use-default-roles \
--ec2-attributes \
KeyName=home-us-east-1,SubnetId=VPC_SUBNET_ID \
--log-uri $S3/logs/ \
--instance-groups \
InstanceGroupType=MASTER,InstanceCount=1,InstanceType=m1.medium \
InstanceGroupType=CORE,InstanceCount=2,InstanceType=m1.medium
```
I've chosen to work in the North Virginia region (us-east-1) to be close to the
CCAFS S3 bucket. Replace _BUCKETNAME_ and _VPC_SUBNET_ID_ with appropriate
values (note that the VPC you create your cluster in must have DNS Resolution
and DNS Hostnames both set to Yes, or the cluster nodes won't be able to
communicate with each other). The output of this command is the new cluster ID:
```
{
    "ClusterId": "j-1AB234CDEFG56"
}
```
Save this as a shell variable then check that the cluster is starting:
```
id=j-1AB234CDEFG56

aws emr describe-cluster --cluster-id $id
```
The cluster will take a while to start - once its EC2 instances are provisioned,
you can get a simplified view of them with
[this script]( https://github.com/simonbrady/utils/blob/master/emr_instance_list.py).

While the cluster is starting, copy the code to S3 so EMR can find it:
```
aws s3 cp target/ncdc_count-VERSION.jar $S3/code/
```
Assuming you've downloaded the NCDC data into your own S3 bucket, you now have
two choices: run the job using S3 as its input source, or copy the data to
HDFS then count records from there. To count records in S3 directly, submit the
job like this:
```
aws emr add-steps --cluster-id $id --steps \
Name="NCDC record count",Type=CUSTOM_JAR,Jar=$S3/code/ncdc_count-VERSION.jar,\
Args="$S3/data,$S3/out,1"
```
The first two arguments are the map source and reduce destination respectively.
The bulk of the work is in the map phase since we use a combiner to do most of
the reduction (accumulating record counts) before the reducers even start,
so the optional third argument overrides the default number of reducers to
save excess book-keeping. Running the job for the entire NCDC dataset will take
a long time on a small cluster, so to try it out you can either create a subset
of the data or specify a single year as input, e.g. `$S3/ncdc/data/1901`.

The status of the step can be monitored in the EMR web console, directly
through the Hadoop UI if you've set up an
[SSH tunnel](http://docs.aws.amazon.com/ElasticMapReduce/latest/DeveloperGuide/emr-ssh-tunnel-local.html),
or from the command-line:
```
step=<output of add-steps command>

aws emr describe-step --cluster-id $id --step-id $step
```
Once it completes, copy the output from S3:
```
aws s3 cp --recursive $S3/out out

sort out/part* | less
```
**NB**: By design, Hadoop jobs will fail if their output directory already
exists. Before re-running the job be sure to delete the output in S3:
```
aws s3 rm --recursive $S3/out
``` 
To copy data to HDFS then count it there, first submit an
[S3DistCp](http://docs.aws.amazon.com/ElasticMapReduce/latest/DeveloperGuide/UsingEMR_s3distcp.html)
step:
```
aws emr add-steps --cluster-id $id --steps \
Name="NCDC copy from S3",Type=CUSTOM_JAR,Jar=/home/hadoop/lib/emr-s3distcp-1.0.jar,\
Args="--src,$S3/data,--dest,/in"
```
This will create a directory `hdfs:///in` on the cluster which you can then
specify as input for the record count:
```
aws emr add-steps --cluster-id $id --steps \
Name="NCDC record count",Type=CUSTOM_JAR,Jar=$S3/code/ncdc_count-VERSION.jar,\
Args="/in,$S3/out,1"
```
Once you're finished, remember to shut the cluster down unless you like giving
all your money to Amazon:
```
aws emr terminate-clusters --cluster-ids $id
```
