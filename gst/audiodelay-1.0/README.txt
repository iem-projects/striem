alternative solution:
 - don't need controllable delay
 - can accept delays of multiple-blocks (each 1024 samples or so)

# time in nanosecons
DELTIME=500000000
  queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 min-threshold-time=${DELTIME}

this also works for video!


