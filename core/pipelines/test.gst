videotestsrc pattern="snow"
! video/x-raw-yuv,width=1920,height=1080
! queue
! textoverlay name=previewtextcomposer text="blurp" font-desc="Sans 72"
! ffmpegcolorspace
! videoscale
! video/x-raw-rgb,width=320,height=180
! ximagesink name=preview
videotestsrc pattern="smpte100" horizontal-speed=1
! video/x-raw-yuv,width=1920,height=1080
! queue
! textoverlay name=livetextcomposer text="oops" font-desc="Sans 32"
! ffmpegcolorspace
! videoscale
! video/x-raw-rgb,width=320,height=180
! ximagesink name=live
audiotestsrc
! audioamplify name=amp amplification=0.1
! autoaudiosink
