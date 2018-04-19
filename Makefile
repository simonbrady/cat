SUBDIRS=ncdc_count ncdc_download ncdc_extract

# Pass these targets straight on to subdirectories
all build clean test:
	for f in $(SUBDIRS); do \
		$(MAKE) -C $$f $@; \
	done
