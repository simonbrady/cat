include ../common.mk

# Keep version in sync with pom.xml
VERSION=1.0.0-SNAPSHOT
TARGET=ncdc_count-$(VERSION).jar

all: $(TARGET)

$(TARGET):
	$(MAVEN) package

clean test:
	$(MAVEN) $@
	
doc: $(README)

distclean: clean
	$(RM) $(README)
