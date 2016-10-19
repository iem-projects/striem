striem - STReam IEM
===================

this is a simple RTMP audio/video streamer
used at the KUG to stream e.g. the schubert-competition




# building striem

## Prerequisites

### Check out the repository

https://github.com/iem-projects/striem

### install dependencies

TODO

- GStreamer

  - GStreamer-1.0

  - `libgstreamer-plugins-base1.0-dev`

  - FAAC: `libfaac-dev`

- GUI

  - PySide: `pyside-tools`


## build

### building the GUI

    cd gui/UIs
    make all


### building GStreamer modules

    cd gst/audiodelay-1.0
    make