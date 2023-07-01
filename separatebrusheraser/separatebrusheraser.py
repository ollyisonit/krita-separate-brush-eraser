# type: ignore
from krita import *
from PyQt5.QtWidgets import QWidget, QAction
from functools import partial

BRUSH_ACTION = "dninosores_activate_brush"
ERASE_ACTION = "dninosores_activate_eraser"
MENU_LOCATION = "tools/scripts/brush and eraser"


class SeparateBrushEraserExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def activate_brush(self):
        pass

    def activate_eraser(self):
        pass

    def setup(self):
        pass

    def createActions(self, window):
        activate_brush_action = window.createAction(
            BRUSH_ACTION, "Activate Brush", MENU_LOCATION
        )
        activate_eraser_action = window.createAction(
            ERASE_ACTION, "Activate Eraser", MENU_LOCATION
        )
        activate_brush_action.triggered.connect(self.activate_brush)
        activate_eraser_action.triggered.connect(self.activate_eraser)


Krita.instance().addExtension(ExportRegionExtension(Krita.instance()))
