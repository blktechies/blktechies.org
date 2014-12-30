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

# Path to locate JS files
JS_BASE_DIR=blacktechies/static/scripts
JS_FILES=$(filter-out %.min.js, \
	$(wildcard $(JS_BASE_DIR)/*.js) \
	$(wildcard $(JS_BASE_DIR)/*/*.js) \
	$(wildcard $(JS_BASE_DIR)/vendor/*.js) \
	$(wildcard $(JS_BASE_DIR)/vendor/*/*.js) \
	$(wildcard $(JS_BASE_DIR)/vendor/*/*/*.js))
JS_MINIFIED = $(JS_FILES:.js=.min.js)
JS_COMPRESSOR=uglifyjs
JS_FLAGS= -p relative

.PHONY: minify-js minify-css minified-css-dir uncompressed-css-dir

minify-js: $(JS_FILES) $(JS_MINIFIED)

%.min.js: %.js
	$(JS_COMPRESSOR) $(JS_FLAGS) $< \
		--source-map $*.min.map \
		--output $@

# This rule dictates how to change from a less file to a css file,
# including the directory change

$(CSS_FILES):$(LESS_FILES) css-dir
	$(LESSC) $< > $@

$(MINCSS_FILES):$(LESS_FILES)
	$(LESSC) --yui-compress $<  >$@

unompressed-css-dir:
	mkdir -p $(CSS_DIR)

minified-css-dir:
	mkdir -p $(MINCSS_DIR)

css: uncompressed-css-dir $(CSS_FILES)

minify-css: minified-css-dir $(MINCSS_FILES)

clean-css:
	rm -rf $(CSS_DIR)

clean-min-css:
	rm -rf $(MINCSS_DIR)

clean: clean-css clean-min-css

all: min-css
