include ../common.mk

# Input can be a space-separated list of paths
INPUT ?= $(DATA)
OUTPUT ?= $(BUCKET)/out
STATIONS ?= $(CONTROL)/ncdc_extract/stations

.PHONY: build clean test upload extract

JAR=ncdc_extract.jar

all: build

build:
	@echo Building Java code
	$(GRADLE) build

clean:
	@echo Cleaning build directory
	$(GRADLE) clean

test:
	@echo Running unit tests
	$(GRADLE) test

upload: build
	@echo Uploading code
	$(S3) cp build/libs/$(JAR) $(CODE)/$(JAR)

extract:
	@echo Extracting selected NCDC records from $(INPUT) to $(OUTPUT)
	$(EMR) add-steps --cluster-id $(CLUSTER) --steps "$$($(SED) \
		-e "s|%CODE%|$(CODE)|" \
		-e "s|%INPUT%|$$(echo $(INPUT) | $(SED) -e 's/ /","/g')|" \
		-e "s|%JAR%|$(JAR)|" \
		-e "s|%OUTPUT%|$(OUTPUT)|" \
		-e "s|%STATIONS%|$(STATIONS)|" \
		extract_step.json)"
