# type: ignore
from krita import *
from PyQt5.QtWidgets import QWidget, QAction
from functools import partial
from pprint import pprint

BRUSH_ACTION = "dninosores_activate_brush"
ERASE_ACTION = "dninosores_activate_eraser"
MENU_LOCATION = "tools/scripts/brush and eraser"
BRUSH_MODE = "BRUSH"
ERASER_MODE = "ERASER"


class SeparateBrushEraserExtension(Extension):
    mode = BRUSH_MODE
    brush_active_tool = False

    def __init__(self, parent):
        super().__init__(parent)

    def switch_to_brush(self):
        Krita.instance().action("KritaShape/KisToolBrush").trigger()
        self.set_brush_settings()

    def eraser_active(self):
        return Application.action("erase_action").isChecked()

    def set_eraser_mode(self, is_on):
        if self.eraser_active() != is_on:
            Application.action("erase_action").trigger()

    def activate_brush(self):
        self.mode = BRUSH_MODE
        self.switch_to_brush()

    def activate_eraser(self):
        self.mode = ERASER_MODE
        self.switch_to_brush()

    def set_brush_settings(self):
        """Assuming brush is the current tool, sets brush settings to match current state."""
        if self.mode == BRUSH_MODE:
            self.set_eraser_mode(False)
        elif self.mode == ERASER_MODE:
            self.set_eraser_mode(True)

    def on_brush_toggled(self, toggled):
        brush_active_tool = toggled
        # Triggers when krita switches to/from the brush tool for any reason. Does not trigger if the brush tool is already selected.
        if toggled:
            self.set_brush_settings()
        else:
            if self.eraser_active():
                self.mode == ERASER_MODE
            else:
                self.mode == BRUSH_MODE
            self.set_eraser_mode(False)

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

        QTimer.singleShot(500, self.bind_brush_toggled)

    def bind_brush_toggled(self):
        success = False
        for docker in Krita.instance().dockers():
            if docker.objectName() == "ToolBox":
                for item, level in IterHierarchy(docker):
                    if item.objectName() == "KritaShape/KisToolBrush":
                        brush_tool = item
                        brush_tool.toggled.connect(self.on_brush_toggled)
                        success = True
        if not success:
            print("Binding eraser toggle to brush button failed. Try restarting Krita.")


class IterHierarchy:
    queue = []

    def __init__(self, root):
        self.root = root
        self.queue = []

    def __iter__(self):
        self.queue = self.walk_hierarchy(self.root)
        return self

    def walk_hierarchy(self, item, level=0, acc=[]):
        acc.append((item, level))
        for child in item.children():
            self.walk_hierarchy(child, level + 1, acc)
        return acc

    def __next__(self):
        if len(self.queue) > 0:
            cur_item = self.queue.pop(0)
            return cur_item[0], cur_item[1]
        else:
            raise StopIteration


Krita.instance().addExtension(SeparateBrushEraserExtension(Krita.instance()))
