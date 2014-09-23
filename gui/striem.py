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

from PySide import QtGui
import streamcontrols

import striem_ui

class striem(QtGui.QMainWindow, striem_ui.Ui_striem):
    def __init__(self):
        super(striem, self).__init__()
        self.setupUi(self)
        self.setupConnections()

    def setupConnectins(self):
        self.actionQuit.activated.connect(self.exit)
        self.actionStreamStart.toggled.connect(self.stream)
        self.actionStreamControls.activated(self.open_streamcontrol)
        self.actionStreamPrefs.activated(self.open_streamprefs)

    def exit(self):
        print("Bye bye")
        sys.exit()

    def stream(self, on):
        print("stream: %s" % (on))
    def open_streamcontrol(self);
        self.streamcontrol.show()
    def open_streamprefs(self);
        self.streamprefs.show()


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    window = striem()
    window.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
