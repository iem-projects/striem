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
import streamcontrols, streampreferences

import striem_ui

class noWidget():
    def __init__(self):
        pass
    def winId(self):
        return None

class striem(QtGui.QMainWindow, striem_ui.Ui_striem):
    def __init__(self, app=None, streamer=None, closeable=False):
        super(striem, self).__init__()
        self.allowClose=closeable
        self.lockTextEditor=False
        self.previewWidget=noWidget()
        self.liveWidget=noWidget()
        self.app=app
        self.streamer=streamer
        self.streamcontrol = streamcontrols.streamcontrols(streamer=streamer, guiparent=self)
        self.streamprefs = streampreferences.streampreferences(streamer=streamer, guiparent=self)

        self.setupUi(self)
        self.setupConnections()

        # ignore Alt-F4 and window-close events
        if self.allowClose:
            self.actionQuit.setShortcut("Ctrl+Q")
        else:
            self.closeEvent=self._closeEvent

        self.streamcontrol.reject()
        self.streamprefs  .reject()


    def _closeEvent(self, event):
        print("close event: %s" % (self.allowClose))
        if not self.allowClose:
            event.ignore()
        else:
            print("exit!")
            self.exit()
            print("gracefully")
    def setupConnections(self):
        self.actionQuit.activated.connect(self.exit)
        self.actionStreamStart.toggled.connect(self.stream)
        self.actionStreamControls.activated.connect(self.open_streamcontrol)
        self.actionStreamPrefs.activated.connect(self.open_streamprefs)
        self.actionStreamPrefs.activated.connect(self.open_streamprefs)
        #self.showTextButton.clicked.connect(self.runningTick)
        #self.hideTextButton.clicked.connect(self._resetTick)
        self.showTextButton.toggled.connect(self._showText)
        self.blackoutButton.toggled.connect(self._showVideo)
        self.titleEdit.editingFinished.connect(self._setPiece)
        self.composerEdit.editingFinished.connect(self._setComposer)
        self.interpretEdit.editingFinished.connect(self._setInterpreter)
    def _showText(self, state):
        if self.streamer:
            self.streamer.showText(state)
        self._textLock()
    def _showVideo(self, state):
        if self.streamer:
            self.streamer.showVideo(not state)

    def _resetTick(self):
        self.runningTick(False)
    def exit(self):
        print("Bye bye")
        if self.streamer:
            self.streamer.teardown()
        import sys
        sys.exit()

    def stream(self, on):
        print("stream: %s" % (on))
        res=self.streamer.streamPause(not on)
        print("paused: %s" % (res))
        self.actionStreamPrefs.setEnabled(not on)
    def open_streamcontrol(self):
        self.streamcontrol.show()
    def open_streamprefs(self):
        self.streamprefs.show()

    def runningTick(self, on=True):
        # streamstatus: when streaming this should display a progress-bar in the bottom-line
        if on:
            ## increment by one percent
            v=self.streamstatusMeter.value()+1
            if(v>self.streamstatusMeter.maximum()):
                v=self.streamstatusMeter.minimum()
                inverted=self.streamstatusMeter.invertedAppearance()
                self.streamstatusMeter.setInvertedAppearance(not inverted)

            self.streamstatusMeter.setValue(v)
        else:
            self.streamstatusMeter.reset()

    def getWindow(self, name):
        if self.app:
            self.app.syncX();
        wdg=None
        if "preview" == name:
            wdg=self.previewWidget
        elif "live" == name:
            wdg=self.liveWidget

        if wdg:
            return wdg.winId()
        return None
    def changedText(self, id, txt):
        self.streamer.setText(id, txt)
    def _setPiece(self):
        self.changedText("piece", self.titleEdit.text())
    def _setComposer(self):
        self.changedText("composer", self.composerEdit.text())
    def _setInterpreter(self):
        self.changedText("interpret", self.interpretEdit.text())
    def textLock(self, value):
        self.lockTextEditor=bool(value)
        self._textLock()
    def _textLock(self):
        dolock=self.lockTextEditor
        if not dolock:
            self.textFrame.setEnabled(True)
            return
        shown=self.showTextButton.isChecked()
        self.textFrame.setEnabled(dolock and not shown)

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    window = striem()
    window.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
