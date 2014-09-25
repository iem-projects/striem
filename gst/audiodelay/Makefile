default: libgstaudiodelay.so

GST_CFLAGS=$(shell pkg-config --cflags gstreamer-0.10)
GST_LDFLAGS=$(shell pkg-config --libs gstreamer-0.10)

GST_PLUGIN_CFLAGS=-DPDGST_PLUGIN $(shell pkg-config --cflags gstreamer-plugins-base-0.10)
GST_PLUGIN_LDFLAGS=-lgstapp-0.10 -lgstaudio-0.10 $(shell pkg-config --libs gstreamer-plugins-base-0.10)

.PHONY: default

audiodelay.o: audiodelay.c audiodelay.h
	$(CC) $(GST_CFLAGS) $(GST_PLUGIN_CFLAGS) -o $@ -c $<

libgstaudiodelay.so: audiodelay.o
	$(CC) -o $@ $^ $(GST_LDFLAGS) $(GST_PLUGIN_LDFLAGS)
