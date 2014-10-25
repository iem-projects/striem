default: libgstaudiodelay.so

GST_PLUGIN_CFLAGS=$(shell pkg-config --cflags gstreamer-1.0 gstreamer-plugins-base-1.0 gstreamer-audio-1.0 gstreamer-controller-1.0)
GST_PLUGIN_LDFLAGS=$(shell pkg-config --libs gstreamer-1.0 gstreamer-plugins-base-1.0 gstreamer-audio-1.0 gstreamer-controller-1.0)

.PHONY: default test

audiodelay.o: audiodelay.c audiodelay.h
	$(CC) $(CFLAGS) -fPIC -DPIC $(GST_PLUGIN_CFLAGS) -o $@ -c $<

libgstaudiodelay.so: audiodelay.o
	$(CC) $(LDFLAGS) -fPIC -shared -o $@ $^ $(GST_PLUGIN_LDFLAGS)


test:
	@echo CFLAGS : $(GST_PLUGIN_CFLAGS)
	@echo LDFLAGS: $(GST_PLUGIN_LDFLAGS)


clean:
	-rm *.o *.so
