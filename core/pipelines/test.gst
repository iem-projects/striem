videotestsrc pattern="snow" ! xvimagesink name=preview
videotestsrc pattern="smpte100"  horizontal-speed=1 ! xvimagesink name=live
