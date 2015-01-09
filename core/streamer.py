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

## build a pipeline,
### basic configuration: URL,sources,...
### - attach controllers
###   - gain, delay, positions
### -


import configuration, pipeline

import math

_db=math.log(10)/20

class streamer:
    def __init__(self, configfile=None, configvalues={}, pipedefaults={}):
        self.cfgbak=configuration.configuration(filename=configfile, defaultvalues=configvalues)
        self.cfg=configuration.configuration(self.cfgbak)
        pipefile=self.cfg.get("stream", "pipeline")
        if not pipefile:
            pipefile="core/pipelines/striem.gst"

        self.pip = pipeline.pipeline(pipefile)
        self.setGui = self.pip.setGui
        self.run    = self.pip.run
        self.addEventKeyHandlers = self.pip.setEventKeys
        if pipedefaults:
            for k,v in pipedefaults.iteritems():
                (element,_,property) = k.partition('.')
                self.pip.setControl(k, v)
                self.pip.setProperty(element, property, v)

    def teardown(self):
        self.cfg.save()
        self.pip.run(False)

    def apply(self):
        self.cfgbak=configuration.configuration(self.cfg)

    def revert(self):
        self.cfg=configuration.configuration(self.cfgbak)

        self.setAGain (self.cfg.get("audio", "gain"))
        self.setADelay(self.cfg.get("audio", "delay"))

        for id in [ "piece", "composer", "interpret" ]:
            face=self.cfg.get(id, "text.face")
            size=self.cfg.get(id, "text.size")
            y=self.cfg.get(id, "text.Y")
            self.setTextFont(id, face, size)
            self.setTextPosition(id, y)
    def setAGain(self, value):
        #print("again: %s" % (value))
        self.cfg.set("audio", "gain", value)
        f=0
        if(value>-100):
            f=math.exp(_db*value)
        self.pip.setControl("audio.gain", f)
    def setADelay(self, value):
        # value in msec, but we need nanosec
        if(value<0):
            value=0
        if(value>1000):
            value=1000
        f=value*1000000
        #print("adelay: %s = %s" % (value, f))
        self.pip.setControl("audio.delay", f)
        self.cfg.set("audio", "delay", value)
    def setVDelay(self, value):
        # value in msec, but we need seconds
        if(value<0):
            value=0
        if(value>1000):
            value=1000
        f=value/1000.
        #print("vdelay: %s = %s" % (value, f))
        self.pip.setControl("video.delay", f)
        self.cfg.set("video", "delay", value)
    def setTextFont(self, id, face, size):
        desc=str(face)+ " " + str(size)
        self.cfg.set(id, "text.face", face)
        self.cfg.set(id, "text.size", size)
        #print("Font['%s']: %s" %( id, desc))
        self.pip.setControl("font."+id, desc)
    def setTextPosition(self, id, y):
        self.cfg.set(id, "text.Y", y)
        #print("Font['%s']: %f" %( id, y))
        self.pip.setControl("posY."+id, y)
    def setText(self, id, txt):
        self.pip.setControl("text."+id, txt)
    def showText(self, state):
        self.pip.setControl("text.hide", not state)
    def showVideo(self, state):
        mute=not state
        ## audio is inverse (it's just a gain), video is ok (it mixes in a second image)
        v=0.
        a=0.
        if not mute:
            v=1.
            a=1.
        #print("showVideo(%s): audio=%s video=%s" % (state, a, v))
        self.pip.setControl("video.mute", v)
        self.pip.setControl("audio.mute", a)
    def getAGain(self):
        v= self.cfg.get("audio", "gain")
        return v
    def getADelay(self):
        return self.cfg.get("audio", "delay")
    def getVDelay(self):
        return self.cfg.get("video", "delay")
    def getTextFont(self, id):
        face=self.cfg.get(id, "text.face")
        size=self.cfg.get(id, "text.size")
        return (face, size)
    def getTextPosition(self, id):
        y=self.cfg.get(id, "text.Y")
        return y
    def streamPause(self, state):
        return self.pip.pause(state, "stream")
    def getConfig(self, section, property):
        res=self.cfg.get(section, property)
        return res
