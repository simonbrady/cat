include common.mk

SUBDIRS=ncdc_download

# Pass these targets straight on to subdirectories
all clean test:
	$(process-subdirs)

doc: $(README)
	$(process-subdirs)

distclean:
	-$(RM) $(README)
	$(process-subdirs)
