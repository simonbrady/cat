include ../common.mk

.PHONY: cluster terminate proxy

all: cluster

cluster:
	@echo Creating EMR cluster
	$(TF) init
	$(TF) apply

terminate:
	@echo Terminating EMR cluster
	$(TF) destroy

proxy:
	@echo Setting up SOCKS proxy connection to cluster
	$(EMR) ssh --cluster-id $(CLUSTER) --key-pair-file $(KEYPAIR) --command hostname
	$(EMR) socks --cluster-id $(CLUSTER) --key-pair-file $(KEYPAIR)
