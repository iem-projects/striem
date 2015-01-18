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

import os.path
gst_extra_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gst-1.0')

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GLib, GObject
from gi.repository import Gst
from gi.repository import GstVideo, GstController

GObject.threads_init()
Gst.init(None)

## add path to our own gst-1.0 plugins
reg=Gst.Registry().get()
res=reg.scan_path(gst_extra_path)

## build a GStreamer pipeline,
### basic configuration: URL,sources,...
### - attach controllers
###   - gain, delay, positions
### -

# TODO: controllers for gst-1.0
#         -> http://tangopardo.com.ar/2cf7/2013/07/30/using-the-gstreamer-controller-subsystem-from-python


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
    - a dictionary with {NAME: {elementname, [propertyname,]}} mappings
      - listing all properties (propertyname) in element (elementname) that listen to NAME
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
            # prop: xpos
            # ctl : FOO
            if not ctl in controls:
                controls[ctl]={}
            if not name in controls[ctl]:
                controls[ctl][name]=[]
            controls[ctl][name]+=[prop]
    return (' ! '.join(elements), controls)

def _pipeRead(pipefile=None, mydict=dict()):
    if not pipefile:
        print "no pipefile specified for pipe"
        return None
    try:
        with open(pipefile, 'r') as f:
            data=f.read().replace('\\\n', '')
    except IOError:
        return None
    ## replace some macros
    if data:
        for k,v in mydict.items():
            data=data.replace('@%s@' % k, v)
    return data

def _ctrlRead(conffile=None):
    if not conffile:
        return None
    ret={}
    lines=[]
    try:
        with open(conffile, 'r') as f:
            lines=[x.strip().split() for x in f.readlines()]
    except IOError:
        return None

    for line in lines:
        if not line:
            continue
        name=line[0]
        if not name in ret:
            ret[name]={}
        d=ret[name]
        for lp in line[1:]:
            (l,_,p) = lp.partition('.')
            if not l in ret[name]:
                ret[name][l]=[]
            ret[name][l]+=[p]

    return ret

class pipeline:
    def __init__(self, filename="default.gst", config=dict()):
        conffile=None
        #print("pipefile: %s" % (filename))

        extension=".gst"
        if filename.endswith(extension):
            conffile=filename[:-len(extension)]+".ctl"
        self.eventhandlers=dict()
        self.eventkeys=dict()
        self.restart   = False
        self.config    = config

        #(self.pipestring, ctrls) = _pipeParseCtrl(_pipeRead(filename, config))
        self.pipestring = _pipeRead(filename, config)
        ctrls=_ctrlRead(conffile)

        #print("pipeline: %s" % (self.pipestring))
        #print("ctrls: %s" % (ctrls))

        self.setEventHandlers({Gst.MessageType.EOS: self._EOS})
        self.setEventHandlers({Gst.MessageType.ELEMENT: self._handleElementEvent})

        self.setEventKeys(None)

        self.pipeline  = Gst.parse_launch(self.pipestring)
        self.bus       = self.pipeline.get_bus()
        self.bus.add_watch(GLib.PRIORITY_DEFAULT, self._async_handler, None)
        Gst.Bus.add_signal_watch(self.bus)

        self.previewOut = None
        self.liveOut    = None

        self.previewOut = self.pipeline.get_by_name("preview")
        self.liveOut = self.pipeline.get_by_name("preview")
        self.recorder = self.pipeline.get_by_name("recorder")

        print("OUT: %s\t%s", self.previewOut, self.liveOut)

        ## get all controllables
        control_dict={}
        for lmn in self.pipeline.iterate_elements():
            for p in lmn.props:
                if False and p.flags & Gst.PARAM_CONTROLLABLE:
                    if not lmn.props.name in control_dict:
                        control_dict[lmn.props.name]=[]
                    control_dict[lmn.props.name]+=[p.name]

        self.controller={}
        self.setter={}
        if ctrls:
            for ctl,elemprop in ctrls.iteritems():
                ## ctl = 'FOO'
                ## elemprop = {'textoverlay_3': ['xpos'], 'textoverlay_1': ['ypos', 'xpos']}
                for elem,props in elemprop.iteritems():
                    ## elem = 'textoverlay_3'
                    ## prop = ['xpos']
                    ctlprops=[]
                    setprops=[]
                    for p in props:
                        if (elem in control_dict) and (p in control_dict[elem]):
                            ctlprops+=[p]
                        else:
                            setprops+=[p]
                    lmn=self.pipeline.get_by_name(elem)
                    #print("element '%s' %s" % (elem, lmn))
                    ## create a controller
                    if ctlprops:
                        tmpctl=Gst.Controller(lmn, *ctlprops)
                        for cp in ctlprops:
                            tmpctl.set_interpolation_mode(cp, Gst.INTERPOLATE_LINEAR)
                            v=lmn.get_property(cp)
                            #print("%s: %s" % (ctl, v))
                            tmpctl.set(cp, 0, v)

                        if not ctl in self.controller:
                            self.controller[ctl] = []
                        self.controller[ctl] += [(tmpctl,ctlprops)]
                    ## create setters
                    ## (this is just a list so we remember)
                    if setprops:
                        if not ctl in self.setter:
                            self.setter[ctl] = {}
                        if not lmn in self.setter[ctl]:
                            self.setter[ctl][lmn] = []
                        self.setter[ctl][lmn] += setprops


    def teardown(self):
        self.EOS()

    def _async_handler (self, bus, message, data):
        try:
            ret=self.eventhandlers[message.type](bus, message)
        except KeyError:
            ret=self.onEvent(bus, message)
        if ret is None:
            return True
        return bool(ret)
    def _EOS(self, bus, message):
        self.pipeline.set_state(Gst.State.NULL)
    def onEvent(self, bus, message):
        """catch all events not handled by more specific handlers"""
        pass
    def _handleElementEvent(self, bus, message):
        struct=message.get_structure()
        for key,fun in self.eventkeys.iteritems():
            if struct and struct.has_field(key):
                fun(struct.get_value(key), key)

    def setEventHandlers(self, handlers=dict()):
        """
        set the event-handlers using a (message.type -> function) mapping.
        e.g. handlers={Gst.MESSAGE_EOS: myEOSfun} will call
        myEOSfun(bus, message) for each EOS-msg received on the pipeline.
        handlers are added in cumulative way (calling this functions multiple times
        will add/update the event-handlers for the given msg-types)
        an None handler will reset the event-handlers to the default.
        """
        if handlers is None:
            self.eventhandlers={Gst.MessageType.EOS: self._EOS}
        else:
            self.eventhandlers.update(handlers)
    def setEventKeys(self, handlers=dict()):
        if handlers is None:
            self.eventkeys=dict()
        else:
            self.eventkeys.update(handlers)

    def EOS(self):
        print("EOS")
        self.pipeline.send_event(gst.Event.new_eos())
    def run(self, state=True):
        if(state):
            self.pipeline.set_state(Gst.State.PLAYING)
        else:
            self.pipeline.set_state(Gst.State.READY)
    def record(self, filename=None):
        ## controls the element named 'record'
        ### if a filename is given, start recording to this name
        ###   recorder.set_state(gst.STATE_PLAYING)
        ### if no filename is given, stop recording
        ###   recorder.send_event(gst.event_new_eos())
        print("recording in %s: %s" % (self.recorder, filename))
        if not self.recorder:
            return False
        ## TODO: check current state of recorder
        if filename:
            self.recorder.set_state(Gst.State.PLAYING)
        else:
            self.recorder.send_event(Gst.Event.new_eos())
            self.recorder.set_state(Gst.State.PAUSED)

    def setControl(self, name, value, time=0):
        gsttime=time*Gst.SECOND
        if name in self.controller:
            for (ctl,props) in self.controller[name]:
                for p in props:
                    ctl.set(p, gsttime, value)
        if name in self.setter:
            for (lmn, props) in self.setter[name].iteritems():
                #print("lmn[%s] %s:%s" % (name, lmn, props))
                if not lmn:
                    continue
                for p in props:
                    (ppad, _, prop) = p.partition("::")
                    if prop:
                        havepads = [pad for pad in lmn.pads if pad.name == ppad]
                        if havepads:
                            lmn=havepads[0]
                    else:
                        prop=p
                    lmn.set_property(prop, value)
    def setProperty(self, element, prop, value):
        lmn=self.pipeline.get_by_name(element)
        if not lmn:
            #continue
            return
        ## try to guess the correct type for the given property
        ## we do that by iterating through a few known types, namely:
        ## - the original type (whatever that was)
        ## - str
        ## - float
        ## - int
        ## and stop after the first one that doesn't throw an error
        for fun in [lambda arg:arg, str, float, lambda arg: int(float(arg))]:
            try:
                x=fun(value)
                try:
                    lmn.set_property(prop, x)
                    break # success, let's exit the type-guessing loop
                except TypeError:
                    ## this happens if set_property doesn't like the given type
                    continue
            except ValueError:
                ## this happens if the conversion to the target type fails
                continue

    def setGui(self, gui):
        # http://stackoverflow.com/questions/1873113/how-to-implement-a-video-widget-in-qt-that-builds-upon-gstreamer
        #gst_x_overlay_set_xwindow_id(GST_X_OVERLAY(sink), widget->winId());
        if not gui:
            return
        if self.previewOut:
            winid=gui.getWindow("preview")
            if winid:
                #print("preview: 0x%X" % (winid))
                self.previewOut.set_window_handle(winid)
            else:
                #print("preview: %s" % (winid))
                pass
        if self.liveOut:
            winid=gui.getWindow("live")
            if winid:
                #print("live: 0x%X" % (winid))
                self.liveOut.set_window_handle(winid)
            else:
                #print("live: %s" % (winid))
                pass
    def pause(self, _state, elementname=None):
        if not elementname:
            state=Gst.State.PAUSED
            if _state:
                state=Gst.State.PLAYING
            self.pipeline.set_state(state)
            #print("pipeline :: %s" % (self.pipeline.get_state(0)))
            return _state
        lmn=self.pipeline.get_by_name(elementname)
        if lmn:
            if _state:
                lmn.set_state(Gst.State.PAUSED)
            else:
                lmn.sync_state_with_parent ()
            #print("lmn=%s :: %s" % (lmn, lmn.get_state(0)))
            return _state
        return False

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
    #sys.exit()

    pip=pipeline(filename, d)
    print("pipeline['%s'] = '%s'" % (filename, pip))
    pip.run(True)
    sleep(5, "running")
    pip.setControl("COLOR", 0xFFFF0000, 5)
    sleep(10, "fading")
    pip.EOS()
    sleep(5, "EOS")
    pip.teardown()
    sleep(5, "bye")
