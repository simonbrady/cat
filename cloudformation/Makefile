include ../common.mk

# Optional template parameters in form key=value, e.g. "CoreInstanceType=c4.large CoreInstanceCount=1"
PARAMETERS ?= ""

# Expand parameters into the format expected by the CloudFormation CLI
CF_PARAMETERS=--parameters $$(echo $(PARAMETERS) | \
	$(SED) -ne 's/\([^ =]*\)=\([^ =]*\)\( *\)/ParameterKey=\1,ParameterValue=\2\3/gp')

.PHONY: cluster terminate proxy

all: cluster

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

proxy:
	@echo Setting up SOCKS proxy connection to cluster
	$(EMR) ssh --cluster-id $(CLUSTER) --key-pair-file $(KEYPAIR) --command hostname
	$(EMR) socks --cluster-id $(CLUSTER) --key-pair-file $(KEYPAIR)
