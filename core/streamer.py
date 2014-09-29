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
    def __init__(self):
        self.cfgbak=configuration.configuration()
        self.cfg=configuration.configuration(self.cfgbak)
        self.pip = pipeline.pipeline("core/pipelines/test.gst")

        self.setGui = self.pip.setGui
        self.pip.run(True)
    def teardown(self):
        self.cfg.save()
        self.pip.run(False)

    def apply(self):
        self.cfgbak=configuration.configuration(self.cfg)

    def revert(self):
        self.cfg=configuration.configuration(self.cfgbak)

        self.setGain(self.cfg.get("audio", "gain"))
        self.setDelay(self.cfg.get("audio", "delay"))

        for id in [ "piece", "composer", "interpreter" ]:
            face=self.cfg.get(id, "text.face")
            size=self.cfg.get(id, "text.size")
            x=self.cfg.get(id, "text.X")
            y=self.cfg.get(id, "text.Y")
            self.setTextFont(id, face, size)
            self.setTextPosition(id, x, y)
    def setGain(self, value):
        print("gain: %s" % (value))
        self.cfg.set("audio", "gain", value)
        f=0
        if(value>-100):
            f=math.exp(_db*value)
        self.pip.setControl("GAIN", f, 10.)
    def setDelay(self, value):
        print("delay: %s" % (value))
        self.cfg.set("audio", "delay", value)
    def setTextFont(self, id, face, size):
        desc=str(face)+ " " + str(size)
        self.cfg.set(id, "text.face", face)
        self.cfg.set(id, "text.size", size)
        print("Font['%s']: %s" %( id, desc))
    def setTextPosition(self, id, x, y):
        self.cfg.set(id, "text.X", x)
        self.cfg.set(id, "text.Y", y)
        print("Font['%s']: %f/%f" %( id, x,y))

    def getGain(self):
        v= self.cfg.get("audio", "gain")
        return v
    def getDelay(self):
        return self.cfg.get("audio", "delay")
    def getTextFont(self, id):
        face=self.cfg.get(id, "text.face")
        size=self.cfg.get(id, "text.size")
        return (face, size)
    def getTextPosition(self, id):
        face=self.cfg.get(id, "text.X")
        size=self.cfg.get(id, "text.Y")
        return (face, size)
