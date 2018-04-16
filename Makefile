SUBDIRS=ncdc_count ncdc_download

# Pass these targets straight on to subdirectories
all build clean test:
	for f in $(SUBDIRS); do \
		$(MAKE) -C $$f $@; \
	done
