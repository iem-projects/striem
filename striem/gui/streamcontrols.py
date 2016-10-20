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
from . import streamcontrols_ui
import logging
log = logging.getLogger(__name__)


class streamcontrols(QtGui.QDialog, streamcontrols_ui.Ui_streamControls):
    def __init__(self, streamer=None, guiparent=None, closefunction=None):
        super(streamcontrols, self).__init__(guiparent)
        self.streamer = streamer

        self.aLevel = None

        if self.streamer:
            self._setAGain = self.__setAGain
            self._setADelay = self.__setADelay
            self._setVDelay = self.__setVDelay
            self._fontChanged = self.__fontChanged
            self._fontPos = self.__fontPos

        self.striem = guiparent
        if self.striem:
            self._textLock = self.__textLock

        self.closefunction = closefunction
        self.setupUi(self)
        self.setupConnections()

    def setupConnections(self):
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.againSlider .valueChanged.connect(self.againValue  .setValue)
        self.againValue  .valueChanged.connect(self.againSlider .setValue)
        self.adelaySlider.valueChanged.connect(self.adelayValue .setValue)
        self.adelayValue .valueChanged.connect(self.adelaySlider.setValue)
        self.vdelaySlider.valueChanged.connect(self.vdelayValue .setValue)
        self.vdelayValue .valueChanged.connect(self.vdelaySlider.setValue)

        self.againValue .valueChanged.connect(self._setAGain)
        self.adelayValue.valueChanged.connect(self._setADelay)

        self.vdelayValue.valueChanged.connect(self._setVDelay)

        self.textLock.stateChanged.connect(self._textLock)

        self.piece_font.currentFontChanged.connect(self._fontPieceChanged)
        self.piece_fontSize.valueChanged.connect(self._fontPieceChanged)
        self.piece_posY.valueChanged.connect(self._fontPieceSize)

        self.composer_font.currentFontChanged.connect(
            self._fontComposerChanged)
        self.composer_fontSize.valueChanged.connect(self._fontComposerChanged)
        self.composer_posY.valueChanged.connect(self._fontComposerSize)

        self.interpreter_font.currentFontChanged.connect(
            self._fontInterpreterChanged)
        self.interpreter_fontSize.valueChanged.connect(
            self._fontInterpreterChanged)
        self.interpreter_posY.valueChanged.connect(self._fontInterpreterSize)

    def _setAGain(self, value):
        log.info("audio gain: %d[dB]" % (value))

    def __setAGain(self, value):
        self.streamer.setAGain(value)

    def _setADelay(self, value):
        log.info("audio delay: %d[ms]" % (value))

    def __setADelay(self, value):
        self.streamer.setADelay(value)

    def _setVDelay(self, value):
        log.info("video delay: %d[ms]" % (value))

    def __setVDelay(self, value):
        self.streamer.setVDelay(value)

    def __textLock(self, value):
        self.striem.textLock(value)
        log.info("text lock: %s" % (value))

    def _fontChanged(self, id, face, size):
        desc = str(face) + " " + str(size)
        log.info("font['%s']: %s" % (id, desc))

    def __fontChanged(self, id, face, size):
        self.streamer.setTextFont(id, face, size)

    def _fontPos(self, id, y):
        log.info("font['%s']: %f" % (id, y))

    def __fontPos(self, id, y):
        self.streamer.setTextPosition(id, y)

    def _fontPieceChanged(self, value):
        fnt = self.piece_font.currentFont().family()
        sze = self.piece_fontSize.value()
        self._fontChanged("piece", fnt, sze)

    def _fontComposerChanged(self, value):
        fnt = self.composer_font.currentFont().family()
        sze = self.composer_fontSize.value()
        self._fontChanged("composer", fnt, sze)

    def _fontInterpreterChanged(self, value):
        fnt = self.interpreter_font.currentFont().family()
        sze = self.interpreter_fontSize.value()
        self._fontChanged("interpret", fnt, sze)

    def _fontPieceSize(self, value):
        y = self.piece_posY.value()
        self._fontPos("piece", y)

    def _fontComposerSize(self, value):
        y = self.composer_posY.value()
        self._fontPos("composer", y)

    def _fontInterpreterSize(self, value):
        y = self.interpreter_posY.value()
        self._fontPos("interpret", y)

    def updateValues(self):
        if not self.streamer:
            return false
        oldstate = self.blockSignals(True)
        self.againValue.setValue(self.streamer.getAGain())
        self.adelayValue.setValue(self.streamer.getADelay())
        self.vdelayValue.setValue(self.streamer.getVDelay())
        for (id, _font, _size, _y) in [
                ("piece",
                 self.piece_font,
                 self.piece_fontSize,
                 self.piece_posY
                 ),
                ("composer",
                 self.composer_font,
                 self.composer_fontSize,
                 self.composer_posY
                 ),
                ("interpret",
                 self.interpreter_font,
                 self.interpreter_fontSize,
                 self.interpreter_posY
                 )
        ]:

            (face, size) = self.streamer.getTextFont(id)
            y = self.streamer.getTextPosition(id)
            font = QtGui.QFont(face)
            _font.setCurrentFont(font)
            _size.setValue(size)
            _y.setValue(y)

        self.blockSignals(oldstate)
        return True

    def accept(self, ok=True):
        if self.streamer:
            if ok:
                self.streamer.apply()
            else:
                self.streamer.revert()

        self.updateValues()

        self.hide()
        if self.closefunction is not None:
            self.closefunction(ok)

    def reject(self):
        self.accept(False)

    def setAudioLevels(self, rmsvalues, _):
        rmsdb = max(rmsvalues)
        vclipped = min(max(rmsdb + 100, 0), 100)
        log.debug("level(%s): %s -> %s = > %s" %
                  (self.aLevel, rmsvalues, rmsdb, vclipped))
        if self.aLevel:
            self.aLevel.setValue(vclipped)

######################################################################
if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    form = streamcontrols(closefunction=sys.exit)

    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
