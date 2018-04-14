include ../common.mk

# Core node EBS volume size in GB
CORE_EBS_SIZE ?= 32
# Number of core nodes
CORE_COUNT ?= 2
# Core node instance type
CORE_TYPE ?= m4.large
# Master node instance type
MASTER_TYPE ?= m4.large
# EMR release label to install
RELEASE_LABEL ?= emr-5.13.0

.PHONY: cluster terminate proxy

all: cluster

cluster:
	@echo Creating EMR cluster
	$(CF) create-stack --stack-name $(STACK) --template-body file://./cluster.yml --parameters \
		ParameterKey=CoreEbsVolumeSize,ParameterValue=$(CORE_EBS_SIZE) \
		ParameterKey=CoreInstanceCount,ParameterValue=$(CORE_COUNT) \
		ParameterKey=CoreInstanceType,ParameterValue=$(CORE_TYPE) \
		ParameterKey=MasterInstanceType,ParameterValue=$(MASTER_TYPE) \
		ParameterKey=ReleaseLabel,ParameterValue=$(RELEASE_LABEL)
	$(CF) wait stack-create-complete --stack-name $(STACK)
	@echo Cluster $(CLUSTER) created

terminate:
	@echo Terminating EMR cluster
	$(CF) delete-stack --stack-name $(STACK)
	$(CF) wait stack-delete-complete --stack-name $(STACK)
	@echo Cluster terminated

proxy:
	@echo Setting up SOCKS proxy connection to cluster
	$(EMR) ssh --cluster-id $(CLUSTER) --key-pair-file $(KEYPAIR) --command hostname
	$(EMR) socks --cluster-id $(CLUSTER) --key-pair-file $(KEYPAIR)
