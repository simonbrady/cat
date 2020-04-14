include ../common.mk

# Range of years to download data for
FROM ?= 1901
TO ?= 1910

# Job-specific details
INPUT ?= $(CONTROL)/ncdc_download/years
OUTPUT ?= $(DATA)
MAPS ?= 12
# See https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-hadoop-task-config.html for sizing
MAP_MEMORY_MB ?= 3072
COPY_SOURCE ?= $(OUTPUT)
COPY_DEST ?= /user/hadoop
JAR=ncdc_download.jar

.PHONY: build clean test upload download copy

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
	for f in download_mapper1.py download_mapper2.py; do \
		$(S3) cp src/main/python/$$f $(CODE)/$$(basename $$f); \
	done

download:
	@echo Starting download of NCDC data for $(FROM)-$(TO) to $(OUTPUT)
	$(EMR) put --cluster-id $(CLUSTER) --key-pair-file $(KEYPAIR) --src build/libs/$(JAR)
	t=$$(mktemp); seq $(FROM) $(TO) > $$t; $(S3) cp $$t $(INPUT); rm $$t
	$(EMR) ssh --cluster-id $(CLUSTER) --key-pair-file $(KEYPAIR) \
		--command "hadoop fs -rm -R -f files"
	$(EMR) add-steps --cluster-id $(CLUSTER) --steps "$$($(SED) \
		-e "s|%CODE%|$(CODE)|" \
		-e "s|%INPUT%|$(INPUT)|" \
		-e "s|%MAPS%|$(MAPS)|" \
		-e "s|%MAP_MEMORY_MB%|$(MAP_MEMORY_MB)|" \
		-e "s|%OUTPUT%|$(OUTPUT)|" \
		download_steps.json)"

copy:
	@echo Copying from $(COPY_SOURCE) to $(COPY_DEST)
	$(EMR) add-steps --cluster-id $(CLUSTER) --steps "$$($(SED) \
		-e "s|%COPY_SOURCE%|$(COPY_SOURCE)|" \
		-e "s|%COPY_DEST%|$(COPY_DEST)|" \
		copy_step.json)"
