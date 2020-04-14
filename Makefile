UPLOAD_SUBDIRS=ncdc_count ncdc_download ncdc_extract
SUBDIRS=$(UPLOAD_SUBDIRS) util

# Pass these targets straight on to subdirectories
all build clean test:
	for f in $(SUBDIRS); do \
		$(MAKE) -C $$f $@; \
	done

upload:
	for f in $(UPLOAD_SUBDIRS); do \
		$(MAKE) -C $$f $@; \
	done
