default: usage

## the .ui files should be edited with `designer-qt4`

%_ui.py: %.ui
	pyside-uic $^ | ./uic_filter.sh $@

UIFILES=$(wildcard *.ui)
PYFILES=$(UIFILES:%.ui=%_ui.py)

.PHONY: all usage default

all: $(PYFILES)


usage:
	@echo ""
	@echo "UI: $(UIFILES)"
	@echo "PY: $(PYFILES)"
	@echo "run 'make all' to build all UIs"
	@echo " or 'make <PYfile>' to build specific UIs"
	@echo ""
	@echo "for editing an UI-file use"
	@echo " designer-qt4 $(UIFILES)"
