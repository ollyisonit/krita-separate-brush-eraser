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

    def switch_to_brush(self):
        Krita.instance().action("KritaShape/KisToolBrush").trigger()

    def set_eraser_mode(self, is_on):
        kritaEraserAction = Application.action("erase_action")
        if kritaEraserAction.isChecked() != is_on:
            kritaEraserAction.trigger()

    def activate_brush(self):
        self.switch_to_brush()
        self.set_eraser_mode(False)

    def activate_eraser(self):
        self.switch_to_brush()
        self.set_eraser_mode(True)

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


Krita.instance().addExtension(SeparateBrushEraserExtension(Krita.instance()))
