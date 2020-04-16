include ../common.mk

FROM ?= 1901
TO ?= 1910
INPUT ?= $(foreach year, $(shell seq $(FROM) $(TO)), $(DATA)/$(year))
OUTPUT ?= $(BUCKET)/output/ncdc_count/$(FROM)-$(TO)

.PHONY: build clean test upload count

JAR=ncdc_count.jar

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

count:
	@echo Writing count of NCDC records for $(FROM)-$(TO) to $(OUTPUT)
	$(EMR) add-steps --cluster-id $(CLUSTER) --steps "$$($(SED) \
		-e "s|%CODE%|$(CODE)|" \
		-e "s|%INPUT%|$$(echo $(INPUT) | $(SED) -e 's/ /","/g')|" \
		-e "s|%JAR%|$(JAR)|" \
		-e "s|%OUTPUT%|$(OUTPUT)|" \
		count_step.json)"
