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
import streamcontrols_ui

class streamcontrols(QtGui.QDialog, streamcontrols_ui.Ui_streamcontrols):
    def __init__(self, guiparent=None, closefunction=None):
        super(streamcontrols, self).__init__(guiparent)
        self.closefunction=closefunction
        self.setupUi(self)
        self.setupConnections()

    def setupConnections(self):
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)


    def accept(self, ok=True):
        self.hide()
        if self.closefunction is not None:
            self.closefunction(ok)
    def reject(self):
        self.accept(False)



######################################################################
if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    form = streamcontrols(closefunction=sys.exit)

    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
