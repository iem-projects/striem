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
    def __init__(self, streamer=None, guiparent=None, closefunction=None):
        super(streamcontrols, self).__init__(guiparent)
        self.closefunction=closefunction
        self.setupUi(self)
        self.setupConnections()

    def setupConnections(self):
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.gainSlider .valueChanged.connect(self.gainValue  .setValue)
        self.gainValue  .valueChanged.connect(self.gainSlider .setValue)
        self.delaySlider.valueChanged.connect(self.delayValue .setValue)
        self.delayValue .valueChanged.connect(self.delaySlider.setValue)

        self.gainValue .valueChanged.connect(self._setGain)
        self.delayValue.valueChanged.connect(self._setDelay)

        self.piece_font.currentFontChanged.connect(self._fontPieceChanged)
        self.piece_fontSize.valueChanged.connect(self._fontPieceChanged)
        self.piece_posX.valueChanged.connect(self._fontPieceSize)
        self.piece_posY.valueChanged.connect(self._fontPieceSize)

        self.composer_font.currentFontChanged.connect(self._fontComposerChanged)
        self.composer_fontSize.valueChanged.connect(self._fontComposerChanged)
        self.composer_posX.valueChanged.connect(self._fontComposerSize)
        self.composer_posY.valueChanged.connect(self._fontComposerSize)

        self.interpreter_font.currentFontChanged.connect(self._fontInterpreterChanged)
        self.interpreter_fontSize.valueChanged.connect(self._fontInterpreterChanged)
        self.interpreter_posX.valueChanged.connect(self._fontInterpreterSize)
        self.interpreter_posY.valueChanged.connect(self._fontInterpreterSize)

    def _setGain(self, value):
        print("gain: %d[dB]" % (value))
    def _setDelay(self, value):
        print("delay: %d[ms]" % (value))
    def _fontChanged(self, id, face, size):
        desc=str(face)+ " " + str(size)
        print("font['%s']: %s" %( id, desc))
    def _fontPos(self, id, x, y):
        print("font['%s']: %f/%f" %( id, x,y))

    def _fontPieceChanged(self, value):
        fnt=self.piece_font.currentFont().family()
        sze=self.piece_fontSize.value()
        self._fontChanged("piece", fnt, sze)
    def _fontComposerChanged(self, value):
        fnt=self.composer_font.currentFont().family()
        sze=self.composer_fontSize.value()
        self._fontChanged("composer", fnt, sze)
    def _fontInterpreterChanged(self, value):
        fnt=self.interpreter_font.currentFont().family()
        sze=self.interpreter_fontSize.value()
        self._fontChanged("interpreter", fnt, sze)
    def _fontPieceSize(self, value):
        x=self.piece_posX.value()
        y=self.piece_posY.value()
        self._fontPos("piece", x, y)
    def _fontComposerSize(self, value):
        x=self.composer_posX.value()
        y=self.composer_posY.value()
        self._fontPos("composer", x, y)
    def _fontInterpreterSize(self, value):
        x=self.interpreter_posX.value()
        y=self.interpreter_posY.value()
        self._fontPos("interpreter", x, y)


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
