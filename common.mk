# Common definitions included by all Makefiles

# Standard README file for doc target, built from README.md by default
README=README.html

# Standard command-line tools
RM=rm

# Markdown to HTML converter
MARKDOWN=markdown_py

# Build target in all subdirectories
define process-subdirs
	for f in $(SUBDIRS); do \
		$(MAKE) -C $$f $@; \
	done
endef

# Pattern rules
%.html: %.md
	$(MARKDOWN) $< > $@

# Tell make about phony targets
.PHONY: doc clean distclean
