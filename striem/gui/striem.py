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

from PySide import QtGui, QtCore
import codecs
import re

from . import streamcontrols
from . import streampreferences

from . import striem_ui

import logging
log = logging.getLogger(__name__)

ESCAPE_SEQUENCE_RE = re.compile(r'''
    ( \\U........      # 8-digit hex escapes
    | \\u....          # 4-digit hex escapes
    | \\x..            # 2-digit hex escapes
    | \\[0-7]{1,3}     # Octal escapes
    | \\N\{[^}]+\}     # Unicode characters by name
    | \\[\\'"abfnrtv]  # Single-character escapes
    )''', re.UNICODE | re.VERBOSE)


def decode_escapes(s):
    """decodes escape-sequences"""
    def decode_match(match):
        return codecs.decode(match.group(0), 'unicode-escape')

    try:
        return ESCAPE_SEQUENCE_RE.sub(decode_match, s)
    except UnicodeDecodeError:
        return s.decode('string_escape')


class noWidget():
    def __init__(self):
        pass

    def winId(self):
        return None


class striem(QtGui.QMainWindow, striem_ui.Ui_striem):
    def __init__(self, app=None, streamer=None, closeable=None):
        super(striem, self).__init__()
        self.textinserts = []
        self.allowClose = bool(closeable)
        self.lockTextEditor = False
        self.previewWidget = noWidget()
        self.liveWidget = noWidget()
        self.app = app
        self.streamer = streamer
        self.streamcontrol = streamcontrols.streamcontrols(
            streamer=streamer,
            guiparent=self)
        self.streamprefs = streampreferences.streampreferences(
            streamer=streamer,
            guiparent=self)
        self.titleDecoration = None
        self.composerDecoration = None
        self.interpreterDecoration = None

        self.setupUi(self)
        self.setupConnections()

        if self.streamer:
            if closeable is None:
                foo = self.streamer.getConfig(
                    "GUI", "allowquit")
                if foo is not None:
                    self.allowClose = bool(int(foo))

            self.streamer.addEventKeyHandlers(
                {'rms': self.streamcontrol.setAudioLevels})

        # ignore Alt-F4 and window-close events
        if self.allowClose:
            self.actionQuit.setShortcut("Ctrl+Q")
        else:
            self.closeEvent = self._closeEvent

        self.streamcontrol.reject()
        self.streamprefs  .reject()

    def _closeEvent(self, event):
        log.info("close event: %s" % (self.allowClose))
        if not self.allowClose:
            event.ignore()
        else:
            log.warn("exit!")
            self.exit()
            log.info("gracefully")

    def setupConnections(self):
        self.actionLoadTexts.activated.connect(self._loadTextFile)

        self.actionQuit.activated.connect(self.exit)
        self.actionStreamStart.toggled.connect(self.stream)
        self.actionStreamControls.activated.connect(self.open_streamcontrol)
        self.actionStreamPrefs.activated.connect(self.open_streamprefs)
        self.actionStreamPrefs.activated.connect(self.open_streamprefs)
        # self.showTextButton.clicked.connect(self.runningTick)
        # self.hideTextButton.clicked.connect(self._resetTick)
        self.showTextButton.toggled.connect(self._showText)
        self.blackoutButton.toggled.connect(self._muteVideo)
        self.titleEdit.editingFinished.connect(self._setTitle)
        if self.titleDecoration:
            self.titleDecoration.toggled.connect(self._setTitle)
        self.composerEdit.editingFinished.connect(self._setComposer)
        if self.composerDecoration:
            self.composerDecoration.toggled.connect(self._setComposer)
        self.interpreterEdit.editingFinished.connect(self._setInterpreter)
        if self.interpreterDecoration:
            self.interpreterDecoration.toggled.connect(self._setInterpreter)
        self.selectText.activated.connect(self._selectInsert)

    def _showText(self, state):
        if self.streamer:
            self.streamer.showText(state)
        self._textLock()

    def _muteVideo(self, state):
        if self.streamer:
            self.streamer.showVideo(not state)

    def _resetTick(self):
        self.runningTick(False)

    def exit(self):
        log.info("Bye bye")
        if self.streamer:
            self.streamer.teardown()
        import sys
        sys.exit()

    def stream(self, on):
        log.info("stream: %s" % (on))
        res = False
        if self.streamer:
            res = self.streamer.streamPause(not on)
        log.info("paused: %s" % (res))
        self.actionStreamPrefs.setEnabled(not on)

    def open_streamcontrol(self):
        self.streamcontrol.show()

    def open_streamprefs(self):
        self.streamprefs.show()

    def runningTick(self, on=True):
        # streamstatus:
        #   when streaming this should display a progress-bar
        #   in the bottom-line
        if on:
            # increment by one percent
            v = self.streamstatusMeter.value() + 1
            if(v > self.streamstatusMeter.maximum()):
                v = self.streamstatusMeter.minimum()
                inverted = self.streamstatusMeter.invertedAppearance()
                self.streamstatusMeter.setInvertedAppearance(not inverted)

            self.streamstatusMeter.setValue(v)
        else:
            self.streamstatusMeter.reset()

    def getWindow(self, name):
        if self.app:
            self.app.syncX()
        wdg = None
        if "preview" == name:
            wdg = self.previewWidget
        elif "live" == name:
            wdg = self.liveWidget

        if wdg:
            return wdg.winId()
        return None

    def changedText(self, id, txt):
        if self.streamer:
            self.streamer.setText(id, decode_escapes(txt))

    def _setTitle(self):
        t = self.titleEdit.text()
        if ((t and
             self.titleDecoration and
             self.titleDecoration.isChecked())):
            # decoration: put piece in quotes
            t = u'„' + t + u'“'
        self.changedText("piece", t)

    def _setComposer(self):
        t = self.composerEdit.text()
        if ((t and
             self.composerDecoration and
             self.composerDecoration.isChecked())):
            # decoration: put composer in parantheses
            t = u'(' + t + u')'
        self.changedText("composer", t)

    def _setInterpreter(self):
        t = self.interpreterEdit.text()
        if ((t and
             self.interpreterDecoration and
             self.interpreterDecoration.isChecked())):
            # no decoration for interpreter
            pass
        self.changedText("interpret", t)

    def textLock(self, value):
        self.lockTextEditor = bool(value)
        self._textLock()

    def _textLock(self):
        dolock = self.lockTextEditor
        if not dolock:
            self.textFrame.setEnabled(True)
            return
        shown = self.showTextButton.isChecked()
        self.textFrame.setEnabled(dolock and not shown)

    def _loadTextFile(self, filename="inserts.txt"):
        # hmm, on some machines opening the QFileDialog simply segfaults
        # so we load a standard-file instead
        if filename:
            self.loadTextFile("inserts.txt")
        else:
            fileName = (
                QtGui.QFileDialog.getOpenFileName(
                    self,
                    "Open Textinserts",
                    "",
                    "TextInsert Files (*.txt)")
            )
            if fileName:
                fname = fileName[0]
                self.loadTextFile(fname)

    def loadTextFile(self, filename):
        lines = []
        with codecs.open(filename, mode='r', encoding='utf-8') as f:
            lines = f.readlines()

        # array of [composer, piece, interpret] tuples
        data = [re.split(r'\t+', x, 2) for x in lines if x]
        # data = [x.strip().split('\t') for x in lines if x]
        self.setTextInserts([x for x in data if len(x) == 3])

    def setTextInserts(self, composerTitleInterpret=[]):
        self.selectText.clear()
        self.textinserts = []
        for (c, t, i) in composerTitleInterpret:
            c = c.strip()
            t = t.strip()
            i = i.strip()
            comboline = i
            if t or c:
                comboline += ': '
                if t:
                    comboline += t + ' '
                if c:
                    comboline += '(' + c + ')'
            self.selectText.addItem(comboline)
            self.textinserts += [[c, t, i]]

    @QtCore.Slot(int)
    def _selectInsert(self, index):
        try:
            (c, t, i) = self.textinserts[index]
            self.titleEdit.setText(t)
            self.composerEdit.setText(c)
            self.interpreterEdit.setText(i)
            self._setTitle()
            self._setComposer()
            self._setInterpreter()
        except IndexError:
            log.exception("cannot find index %s in textinserts (size = %s)"
                          % (index, len(self.textinserts)))

    def resizeEvent(self, event):
        h = self.previewWidget.height()
        w = int(h * 16. / 9.)
        self.previewWidget.setMinimumWidth(w)
        self.previewWidget.setMaximumWidth(w)


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    window = striem()
    window.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
