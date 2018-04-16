# CloudFormation Template

This directory contains a
[CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html)
template to deploy an EMR cluster and configure
[debugging](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-plan-debugging.html)
on it. You can either load the [template](cluster.yml) from the CloudFormation console, or
deploy straight from the command line with `make`. You can override various
[Makefile](Makefile) variables to configure the cluster, e.g.
```
CORE_TYPE=i3.xlarge CORE_COUNT=4 CORE_EBS_SIZE=0 make
```
would deploy a cluster with four i3.xlarge nodes in its core instance group and not
attach any EBS volumes (since these instances provide locally-attached instance store
for HDFS).

Some settings are not exposed as CloudFormation parameters, but are hard-coded in the
`RegionSpecific` mapping table in the template: you'll need to update these for
your environment before you can deploy. The EC2 keypairs shoud match up with what's
set in [common.mk](../common.mk).

To terminate the cluster when you've finshed, simply do:
```
make terminate
```

If you choose to deploy your cluster without using the template, you should set the
`CLUSTER` environment variable to its ID since other components' Makefiles expect
this to resolve to the cluster ID.
