include common.mk

SUBDIRS=ncdc_download

all: doc

doc: README.html $(SUBDIRS)
	for f in $(SUBDIRS); do \
		$(MAKE) -C $$f $@; \
	done

.PHONY: doc $(SUBDIRS)
