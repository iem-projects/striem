pipelines + control config
---

NAME.gst
	pipeline-description (as launched by gst-launch)
	"
NAME.ctl
	controller setup, one controller per line of the form
	"NAME	element1.parm3 element4.parm1"


examples

<test.gst>
videotestsrc
! textoverlay name=txt1
! textoverlay name=txt2
! xvimagesink
</test.gst>

<test.cfg>
textcolor txt1.color txt1.outline-color txt2.color
img	videotestsrc0.pattern
</test.cfg>


NOTE: you should assign names to the elements in the pipeline-description,
to avoid using the wrong auto-generated names (in the example, adding a second
videotestsrc and restructuring the pipeline file (without changing the actual
functionality, might change the auto-assigned names)
