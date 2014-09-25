jackaudiosrc connect=0 client-name=delay
! audio/x-raw-float,channels=2
! audioamplify amplification=0.5
! audiodelay   delay=500000000
! jackaudiosink
