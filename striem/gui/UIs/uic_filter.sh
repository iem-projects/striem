#!/bin/sh

# filter all connections (we want to set them up manually)
grep -v QtCore.QMetaObject.connectSlotsByName | \
grep -v QtCore.QObject.connect | \
cat > ../$1
