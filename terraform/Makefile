include ../common.mk

VARS=-var region=$(REGION) -var key_name=$(basename $(notdir $(KEYPAIR)))

.PHONY: cluster terminate proxy

all: cluster

cluster:
	@echo Creating EMR cluster
	$(TF) init
	$(TF) apply $(VARS)

terminate:
	@echo Terminating EMR cluster
	$(TF) destroy $(VARS)

proxy:
	@echo Setting up SOCKS proxy connection to cluster
	$(EMR) ssh --cluster-id $(CLUSTER) --key-pair-file $(KEYPAIR) --command hostname
	$(EMR) socks --cluster-id $(CLUSTER) --key-pair-file $(KEYPAIR)
