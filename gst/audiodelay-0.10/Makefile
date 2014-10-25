default: libgstaudiodelay.so

GST_PLUGIN_CFLAGS=$(shell pkg-config --cflags gstreamer-0.10 gstreamer-plugins-base-0.10 gstreamer-audio-0.10 gstreamer-controller-0.10)
GST_PLUGIN_LDFLAGS=$(shell pkg-config --libs gstreamer-0.10 gstreamer-plugins-base-0.10 gstreamer-audio-0.10 gstreamer-controller-0.10)

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
