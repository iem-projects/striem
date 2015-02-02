.PHONY: all gui audiodelay

all: gui audiodelay

gui:
	make -C gui/UIs all

audiodelay:
	make -C gst/audiodelay-1.0
