include ../common.mk

.PHONY: build clean upload

all: build

build:
	@echo Building Java code
	$(GRADLE) jar

clean:
	@echo Cleaning build directory
	$(GRADLE) clean
