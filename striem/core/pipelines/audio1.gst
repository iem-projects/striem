jackaudiosrc connect=none client-name=striem
! audio/x-raw-float,channels=2	! deinterleave name=asplit
! ladspa-amp-mono  Gain=0.5 name=ampL
! ladspa-delay-5s Delay=1
! interleave name=amerge
! jackaudiosink client-name=striem
