jackaudiosrc connect=none 	! audio/x-raw-float,channels=2	! deinterleave	name=asplit	\
asplit.src1			\
! ladspa-amp-mono  Gain=0.5	\
! ladspa-delay-5s Delay=1	\
amerge.sink1			\
asplit.src2			\
! ladspa-amp-mono  Gain=0.5	\
! ladspa-delay-5s Delay=1	\
amerge.sink2			\
interleave name=amerge		\
! jackaudiosink connect=0

