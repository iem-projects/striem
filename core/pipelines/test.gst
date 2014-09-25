videotestsrc pattern="snow"
! ximagesink name=preview
videotestsrc pattern="smpte100" horizontal-speed=1
! ximagesink name=live
audiotestsrc
! audioamplify name=amp amplification=0.5
! autoaudiosink
