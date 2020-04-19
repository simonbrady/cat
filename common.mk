# Common definitions included by all Makefiles

# Settings shared across sub-projects
REGION ?= us-east-1
KEYPAIR ?= /path/to/keypair.pem
BUCKET ?= s3://bucket
CODE ?= $(BUCKET)/code
CONTROL ?= $(BUCKET)/control
DATA ?= $(BUCKET)/data

# Commands to use
AWS=aws
EMR=$(AWS) emr --region $(REGION)
S3=$(AWS) s3
GRADLE=gradle
PYTHON=python3
SED=sed
TF=terraform

# Helper for AWS CLI commands that take a cluster ID
CLUSTER=$$(cd ../terraform; $(TF) output cluster_id)
