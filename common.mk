# Common definitions included by all Makefiles

# Markdown to HTML converter
MARKDOWN=markdown_py

%.html: %.md
	$(MARKDOWN) $< > $@
