# Common definitions included by all Makefiles

# Settings shared across sub-projects
REGION ?= ap-southeast-2
KEYPAIR ?= $(HOME)/keys/home-$(REGION).pem
STACK ?= cat-emr-cluster
BUCKET ?= s3://ncdc.hikari.org.nz
CODE ?= $(BUCKET)/code

# Commands to use
AWS=aws
CF=$(AWS) cloudformation --region $(REGION)
EMR=$(AWS) emr --region $(REGION)
S3=$(AWS) s3
GRADLE=gradle
SED=sed

# Helper for AWS CLI commands that take a cluster ID
CLUSTER=$$($(CF) describe-stacks --stack-name $(STACK) \
	--query "Stacks[0].Outputs[?OutputKey=='ClusterId'].OutputValue" --output text)
