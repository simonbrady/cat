MARKDOWN=markdown2

all: doc

doc: README.html

%.html: %.md
	$(MARKDOWN) $< > $@

.PHONY: doc
