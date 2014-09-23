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

import ConfigParser
import os.path


## files listed LATER can overwrite values from earlier files
_configpaths=[
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'), ## built-in
    os.path.join(os.path.expanduser('~'), '.config', 'stream.iem.at'),  ## per-user
    '.',                                                                ## local
    ]


###### configuration

# section: stream
## (string)URL

# section: video
## (string)source

# section: audio
## (string)source
## (float)delay
## (float)gain

# section: piece/composer/interpreter
## (float)text.X, (float)text.Y
## (string)text.face
## (int)text.size


class configuration:
    _typefuns = {
        'URL'      : str,
        'source'   : str,
        'delay'    : (lambda v: int(float(v))),
        'gain'     : float,
        'text.face': str,
        'text.size': float,
        'text.X'   : float,
        'text.Y'   : float
    }
    def __init__(self, filename=None):
        configfiles=[os.path.join(path, "striem.conf") for path in _configpaths]
        self.filename=configfiles[1]

        if filename is not None:
            configfiles+=[filename]
        self._cfg = ConfigParser.ConfigParser()
        files=self._cfg.read(configfiles)
        if files:
            self.filename=files[-1]

    def save(self, filename=None):
        if filename is None:
            filename=self.filename
        if filename is None:
            return False
        with open(filename, 'wb') as configfile:
            self._cfg.write(configfile)
        return True
    def get(self, section, option):
        v=self._cfg.get(section, option)
        if option in configuration._typefuns:
            return configuration._typefuns[option](v)
        return v
    def set(self, section, option, value):
        v=str(value)
        self._cfg.set(section, option, value)





######################################################################
if __name__ == '__main__':
    import sys
    filename=None
    if(len(sys.argv)>1):
        filename=sys.argv[1]
    config=configuration(filename)
    def showConf(cfg, section, option):
        v=config.get(section, option)
        print("config['%s', '%s'] = %s%s" % (section, option, v, type(v)))
    showConf(config, "audio", "delay")
    showConf(config, "audio", "gain")
    showConf(config, "piece", "text.face")
    config.set("stream", "URL", "http://youtube.com")
    config.save("/tmp/striem.cfg")
