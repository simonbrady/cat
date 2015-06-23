# NCDC Record Count

This is a simple Hadoop job to run over the downloaded NCDC data, heavily based
on the examples in Tom White, _Hadoop: the Definitive Guide_ (3rd ed.: Oreilly,
2012). It counts records by station ID (the concatenation of a station's USAF
catalogue number and WBAN identifier, e.g. 029070-99999) and produces
tab-delimted ID-count pairs as output. Its main purpose is to sanity-check the
data and Hadoop configuration.

The code can be built in Eclipse or from the command-line with Maven (this is
automated by the Makefile so you can build everything from the top-level
project directory). The output is a JAR archive,
`target/ncdc_download-VERSION.jar` to submit to Hadoop. I've used Hadoop 2.4.0
as bundled with the
[Elastic MapReduce AMI 3.7.0](http://docs.aws.amazon.com/ElasticMapReduce/latest/DeveloperGuide/emr-plan-hadoop.html),
but the code is so simple that any Hadoop version should work (you'll just need
to update the Maven dependency in [pom.xml](pom.xml)).

To run the job from the command line, install and configure the
[AWS CLI](http://docs.aws.amazon.com/cli/latest/index.html) then set up your
[EMR default roles](http://docs.aws.amazon.com/cli/latest/reference/emr/create-default-roles.html)
if you haven't already done so:
```
aws emr create-default-roles
```
Next, start up a small cluster:
```
S3=s3://BUCKETNAME/ncdc/

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
Save this as shell variable then check that the cluster is starting:
```
id=j-1AB234CDEFG56

aws emr describe-cluster --cluster-id $id
```
The cluster will take a while to start - once its EC2 instances are provisioned,
you can get a simplified view of them with
[this script]( https://github.com/simonbrady/utils/blob/master/emr_instance_list.py).
