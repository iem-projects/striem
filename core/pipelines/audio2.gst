asplit.src0
! ladspa-amp-mono  Gain=0.5 name=ampR
! ladspa-delay-5s Delay=1
amerge.sink0
jackaudiosrc connect=none client-name=striem
! audio/x-raw-float,channels=2
! queue
! deinterleave name=asplit
! ladspa-amp-mono  Gain=0.5 name=ampL
! ladspa-delay-5s Delay=1
! interleave name=amerge
! audio/x-raw-float,channels=2
! jackaudiosink client-name=striem
