videotestsrc pattern="snow"
! video/x-raw,format=YUY2,width=1920,height=1080
! queue
! textoverlay name=previewtextpiece text="Goldberg Variation #5" font-desc="Sans 72"
! textoverlay name=previewtextcomposer text="J.S.Bach" font-desc="Sans 72"
! textoverlay name=previewtextinterpreter text="Hanns Müller" font-desc="Sans 72"
! videoconvert
! videoscale
! video/x-raw,width=320,height=180
! ximagesink name=preview
videotestsrc pattern="smpte100" horizontal-speed=1
! video/x-raw,format=YUY2,width=1920,height=1080
! queue
! textoverlay name=livetextcomposer text="oops" font-desc="Sans 32"
! videoconvert
! videoscale
! video/x-raw,width=320,height=180
! ximagesink name=live
audiotestsrc
! audioamplify name=amp amplification=0.1
! autoaudiosink
