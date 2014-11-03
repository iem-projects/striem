videotestsrc pattern=18
! video/x-raw,pixel-aspect-ratio=(fraction)1/1, interlace-mode=(string)progressive, framerate=30/1, width=1280, height=720
! frei0r-filter-delay0r name=vdelay delaytime=0
! videomixer name=mix sink_0::alpha=1 sink_1::alpha=0.5
! textoverlay font-desc="Sans 72" shaded-background=True name=previewtextpiece       text="Goldberg Variation #5"
! textoverlay font-desc="Sans 72" shaded-background=True name=previewtextcomposer    text="J.S.Bach"
! textoverlay font-desc="Sans 72" shaded-background=True name=previewtextinterpreter text="Hanns Müller"
! tee name=vout
! queue
! videoconvert
! videoscale
! xvimagesink name=preview
videotestsrc pattern=21
! videoconvert
! video/x-raw,pixel-aspect-ratio=(fraction)1/1, interlace-mode=(string)progressive, framerate=30/1, width=1280, height=720
! queue
! mix.
vout.
! queue
! videoconvert
! x264enc bitrate=4000 key-int-max=60 bframes=0 byte-stream=false aud=true tune=zerolatency
! h264parse
! video/x-h264,level=(string)4.1,profile=main
! queue
! mux.
jackaudiosrc
! audio/x-raw,channels=2
! volume name=again
! audiodelay name=adelay max-delay=1000000000 delay=0
! volume name=amute
! audioconvert
! audio/x-raw,format=(string)S16LE,endianness=(int)1234,signed=(boolean)true,width=(int)16,depth=(int)16,rate=(int)44100,channels=(int)2
! queue
! faac bitrate=128000
! aacparse
! audio/mpeg,mpegversion=4,stream-format=raw
! queue
! flvmux streamable=true name=mux
! queue
! fakesink
