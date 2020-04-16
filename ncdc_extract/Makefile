include ../common.mk

FROM ?= 1901
TO ?= 1910
INPUT ?= $(foreach year, $(shell $(SEQ) $(FROM) $(TO)), $(DATA)/$(year))
OUTPUT ?= $(BUCKET)/output/ncdc_extract/$(FROM)-$(TO)
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
	@echo Extracting selected NCDC records for $(FROM)-$(TO) to $(OUTPUT)
	$(EMR) add-steps --cluster-id $(CLUSTER) --steps "$$($(SED) \
		-e "s|%CODE%|$(CODE)|" \
		-e "s|%INPUT%|$$(echo $(INPUT) | $(SED) -e 's/ /","/g')|" \
		-e "s|%JAR%|$(JAR)|" \
		-e "s|%OUTPUT%|$(OUTPUT)|" \
		-e "s|%STATIONS%|$(STATIONS)|" \
		extract_step.json)"
