#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright © 2014, IOhannes m zmölnig, IEM

# This file is part of striem
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with striem.  If not, see <http://www.gnu.org/licenses/>.

import pygst
pygst.require("0.10")
import gst


## build a GStreamer pipeline,
### basic configuration: URL,sources,...
### - attach controllers
###   - gain, delay, positions
### -


## pipeline descriptions:
# "element1 ! element2 prop1=bla prop2=@FUZZ@ ! element3 prop[BAX]=12"
# will create a pipeline with three elements
# element2 has 2 properties set, 'prop1' is "bla" and 'prop2' to the expansion of "FUZZ"
# element3 has 1 property 'prop' to '12', and it will be controllable with the name 'BAX':
#    with setControl('BAX', value, time=0)
# if the property is a 'controllable', the value will be interpolated to the target in 'time'
# if the property is only 'writeable', the value will be set
# multiple properties (in multiple elements) can be bound to the same variable

def _pipeParseCtrl(pipestring=""):
    """
    parse a pipestring to extract all ctl.NAME: properties
    returns a tuple containing:
    - a cleaned up pipestring
    - a dictionary with {NAME: (elementname, propertyname)} mappings
    CAVEATS:
      - the elementname-resolving code is experimental. use the "name" property to help it
      - cannot handle white-space in property-values
      - cannot handle quotes properly
    """
    names=set()
    controls={}
    elements=[]
    for element in [x.strip() for x in pipestring.split("!")]:
        name=None
        ctls=[]
        (ename, _, argss)=element.partition(' ')

        element=ename
        for arg in argss.split():
            (prop,_,val)=arg.partition('=')
            (prop,_,ctl)=prop.partition('[')
            if "name"==prop:
                name=val
            if ctl:
                ctls+=[(prop, ctl.rstrip(']'))]
            element+=" %s" % prop
            if val:
                element+="=%s"%val
        if not name:
            idx=0
            name="%s_%d" % (ename, idx)
            while name in names:
                idx+=1
                name="%s_%d" % (ename, idx)
            names.add(name)
            element += " name=%s"%name
        elements+=[element]

        for (prop,ctl) in ctls:
            if not prop in controls:
                controls[prop]=[]
            controls[prop]+=[(name,ctl)]
    return (' ! '.join(elements), controls)

def _pipeRead(pipefile=None, mydict=dict()):
    if not pipefile:
        print "no pipefile specified for pipe"
        return
    with open(pipefile, 'r') as f:
        data=f.read()
    ## replace some macros
    if data:
        for k,v in mydict.items():
            data=data.replace('@%s@' % k, v)
    return data

class pipeline:
    def __init__(self, filename="default.gst", config=dict()):
        self.eventhandlers=dict()
        self.restart   = False
        self.config    =config
        self.pipestring= _pipeRead(filename, config)

        self.setEventHandlers(None)

        self.pipeline  = gst.parse_launch(self.pipestring)
        self.bus       = self.pipeline.get_bus()
        self.bus.add_watch(self._async_handler)


        ## get all controllables
        #
    def teardown(self):
        pass

    def _async_handler (self, bus, message):
        try:
            ret=self.eventhandlers[message.type](bus, message)
        except KeyError:
            ret=self.onEvent(bus, message)
        if ret is None:
            return True
        return bool(ret)
    def _EOS(self, bus, message):
        self.pipeline.set_state(gst.STATE_NULL)
    def onEvent(self, bus, message):
        """catch all events not handled by more specific handlers"""
        pass

    def setEventHandlers(self, handlers=dict()):
        """
        set the event-handlers using a (message.type -> function) mapping.
        e.g. handlers={gst.MESSAGE_EOS: myEOSfun} will call
        myEOSfun(bus, message) for each EOS-msg received on the pipeline.
        handlers are added in cumulative way (calling this functions multiple times
        will add/update the event-handlers for the given msg-types)
        an None handler will reset the event-handlers to the default.
        """
        if handlers is None:
            self.eventhandlers={gst.MESSAGE_EOS: self._EOS}
        else:
            self.eventhandlers.update(handlers)
    def EOS(self):
        self.pipeline.send_event(gst.event_new_eos())
    def run(self, state=True):
        if(state):
            self.pipeline.set_state(gst.STATE_PLAYING)
        else:
            self.pipeline.set_state(gst.STATE_READY)




######################################################################
if __name__ == '__main__':
    import sys,time
    def sleep(t=5, name="zzz"):
        print("%s:sleep(%d)" % (name, t))
        time.sleep(t)
        print("%s:awoke" % (name))
    filename=None
    if(len(sys.argv)>1):
        filename=sys.argv[1]
    d=dict()
    d['streamsource']="fudel"
    d['FUZZ']="fuzz"
    d['BAX']="bax"

    pipestring=_pipeRead(filename, d)
    print _pipeParseCtrl(pipestring)
    sys.exit()

    pip=pipeline(filename, d)
    print("pipeline['%s'] = '%s'" % (filename, pip))
    pip.run(True)
    sleep(10, "running")
    pip.EOS()
    sleep(5, "EOS")
    pip.teardown()
    sleep(5, "bye")
