DEBUG=yes
# Set the base folder of all styles, less, css, and min.css
STYLES_DIR=blacktechies/static/styles/blacktechies

# Path for less sources relative to STYLES_DIR
LESS_DIR=$(STYLES_DIR)/src/less

# Path for uncompressed css files
CSS_DIR=$(STYLES_DIR)/css
MINCSS_DIR=$(STYLES_DIR)/min-css


# Less files are in the LESS_DIR and end in '.less'
LESS_FILES=$(wildcard $(LESS_DIR)/*.less)
# By changind src/less to css and .less to .css, we derive the names
# of the uncompressed CSS files and compressed CSS files
CSS_FILES=$(patsubst $(LESS_DIR)/%.less,$(CSS_DIR)/%.css,$(LESS_FILES))
MINCSS_FILES=$(patsubst $(LESS_DIR)/%.less, $(MINCSS_DIR)/%.min.css, $(LESS_FILES))

# How we invoke our less compiler. This assumes it's on your path.
# AKA `npm install -g less`, and node binaries are on your path...
LESSC=lessc

# This rule dictates how to change from a less file to a css file,
# including the directory change
# $(CSS_DIR)/%.css : $(LESS_DIR)/%.less
# 	$(LESSC) $< > $@

$(CSS_FILES):$(LESS_FILES) css-dir
	$(LESSC) $< > $@

$(MINCSS_FILES):$(LESS_FILES)
	$(LESSC) --yui-compress $<  >$@

css-dir:
	mkdir -p $(CSS_DIR)

min-css-dir:
	mkdir -p $(MINCSS_DIR)

css: css-dir $(CSS_FILES)

min-css: min-css-dir $(MINCSS_FILES)

clean-css:
	rm -rf $(CSS_DIR)

clean-min-css:
	rm -rf $(MINCSS_DIR)

clean: clean-css clean-min-css

all: min-css
