# type: ignore
from krita import *
from PyQt5.QtWidgets import QWidget, QAction
from functools import partial
from pprint import pprint

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

    def on_brush_toggled(self, toggled):
        # When we toggle the brush off and switch to a different tool
        # The eraser should be disabled
        if not toggled:
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
