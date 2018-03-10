# Range of years to download data for
FROM ?= 1901
TO ?= 1910

# Environment-specific details
BUCKET ?= s3://ncdc.hikari.org.nz
CODE ?= $(BUCKET)/code
INPUT ?= $(BUCKET)/input/years
OUTPUT ?= $(BUCKET)/data/$(FROM)-$(TO)
KEYPAIR ?= $(HOME)/keys/home-us-east-1.pem
REGION ?= us-east-1
STACK ?= ncdc-download

# Optional template parameters in form key=value, e.g. "CoreInstanceType=c4.large CoreInstanceCount=1"
PARAMETERS ?= ""

# Commands to use
AWS=aws
CF=$(AWS) cloudformation --region $(REGION)
EMR=$(AWS) emr --region $(REGION)
S3=$(AWS) s3
GRADLE=gradle
SED=sed

# Helper for commands that take a cluster ID
CLUSTER=$$($(CF) describe-stacks --stack-name $(STACK) \
	--query "Stacks[0].Outputs[?OutputKey=='ClusterId'].OutputValue" --output text)

# Expand parameters into the format expected by the CloudFormation CLI
CF_PARAMETERS=--parameters $$(echo $(PARAMETERS) | \
	$(SED) -ne 's/\([^ =]*\)=\([^ =]*\)\( *\)/ParameterKey=\1,ParameterValue=\2\3/gp')

.PHONY: build clean cluster terminate upload download proxy

all: build

build:
	@echo Building Java code
	$(GRADLE) jar

clean:
	@echo Cleaning build directory
	$(GRADLE) clean

cluster:
	@echo Creating EMR cluster
	$(CF) create-stack --stack-name $(STACK) --template-body file://./cluster.yml $(CF_PARAMETERS)
	$(CF) wait stack-create-complete --stack-name $(STACK)
	@echo Cluster $(CLUSTER) created

terminate:
	@echo Terminating EMR cluster
	$(CF) delete-stack --stack-name $(STACK)
	$(CF) wait stack-delete-complete --stack-name $(STACK)
	@echo Cluster terminated

upload: build
	@echo Uploading code
	$(EMR) put --cluster-id $(CLUSTER) --key-pair-file $(KEYPAIR) --src build/libs/ncdc_download.jar
	for f in download_mapper1.py download_mapper2.py; do \
		$(S3) cp $$f $(CODE)/$$(basename $$f); \
	done

download:
	@echo Starting download of NCDC data for $(FROM)-$(TO) to $(OUTPUT)
	t=$$(mktemp); seq $(FROM) $(TO) > $$t; $(S3) cp $$t $(INPUT); rm $$t
	$(EMR) ssh --cluster-id $(CLUSTER) --key-pair-file $(KEYPAIR) \
		--command "hadoop fs -rm -R -f files"
	$(EMR) add-steps --cluster-id $(CLUSTER) \
		--steps "$$($(SED) -e 's|%CODE%|$(CODE)|;s|%INPUT%|$(INPUT)|;s|%OUTPUT%|$(OUTPUT)|' download_steps.json)"

proxy:
	@echo Setting up SOCKS proxy connection to cluster
	$(EMR) socks --cluster-id $(CLUSTER) --key-pair-file $(KEYPAIR)
