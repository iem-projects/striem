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


import configuration

class streamer:
    def __init__(self):
        self.cfgbak=configuration.configuration()
        self.cfgbak.dump()
        self.cfg=configuration.configuration(self.cfgbak)
        self.cfg.dump()
    def teardown(self):
        self.cfg.save()
        pass

    def apply(self):
        self.cfgbak=configuration.configuration(self.cfg)
        self.cfgbak.dump()

    def revert(self):
        self.cfg=configuration.configuration(self.cfgbak)
        self.cfg.dump()

        self.changeGain(self.cfg.get("audio", "gain"))
        self.changeDelay(self.cfg.get("audio", "delay"))

        for id in [ "piece", "composer", "interpreter" ]:
            face=self.cfg.get(id, "text.face")
            size=self.cfg.get(id, "text.size")
            x=self.cfg.get(id, "text.X")
            y=self.cfg.get(id, "text.Y")
            self.changeText(id, face, size)
            self.changeTextPosition(id, x, y)


    def changeGain(self, value):
        print("gain: %s" % (value))
        self.cfg.set("audio", "gain", value)
    def changeDelay(self, value):
        print("delay: %s" % (value))
        self.cfg.set("audio", "delay", value)
    def changeText(self, id, face, size):
        desc=str(face)+ " " + str(size)
        self.cfg.set(id, "text.face", face)
        self.cfg.set(id, "text.size", size)
        print("Font['%s']: %s" %( id, desc))
    def changeTextPosition(self, id, x, y):
        self.cfg.set(id, "text.X", x)
        self.cfg.set(id, "text.Y", y)
        print("Font['%s']: %f/%f" %( id, x,y))

    def getGain(self):
        v= self.cfg.get("audio", "gain")
        self.cfg.dump()
        return v


    def getDelay(self):
        return self.cfg.get("audio", "delay")
    def getTextt(self):
        face=self.cfg.get(id, "text.face")
        size=self.cfg.get(id, "text.size")
        return (face, size)
    def getTextPosition(self):
        face=self.cfg.get(id, "text.X")
        size=self.cfg.get(id, "text.Y")
        return (face, size)
