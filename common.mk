# Common definitions included by all Makefiles

# Settings shared across sub-projects
REGION ?= ap-southeast-2
KEYPAIR ?= $(HOME)/keys/home-$(REGION).pem
BUCKET ?= s3://ncdc.hikari.org.nz
CODE ?= $(BUCKET)/code
CONTROL ?= $(BUCKET)/control
DATA ?= $(BUCKET)/data

# Commands to use
AWS=aws
EMR=$(AWS) emr --region $(REGION)
S3=$(AWS) s3
GRADLE=gradle
SED=sed
TF=terraform

# Helper for AWS CLI commands that take a cluster ID
CLUSTER=$$(cd ../terraform; $(TF) output cluster_id)
