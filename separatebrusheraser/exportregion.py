# type: ignore
from krita import *
from PyQt5.QtWidgets import QWidget, QAction
from pprint import pprint
from functools import partial


class ExportRegionExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    # If part of the document is selected, export the selection.
    # If nothing is selected, export everything in the current layer's bounding box.
    def export_region(self):
        if not Krita.instance().activeDocument():
            return

        clear_at_end = False

        if not Krita.instance().activeDocument().selection():
            Krita.instance().action("selectopaque").trigger()
            clear_at_end = True
        Krita.instance().action("copy_merged").trigger()

        orig_document = Krita.instance().activeDocument()

        Krita.instance().action("paste_new").trigger()

        new_document = Krita.instance().activeDocument()
        Krita.instance().action("file_export_file").trigger()
        new_document.close()

        Krita.instance().setActiveDocument(orig_document)
        if clear_at_end:
            Krita.instance().action("deselect").trigger()

    def setup(self):
        pass

    def createActions(self, window):
        export_region_action = window.createAction(
            "dninosores_export_region", "Export Region...", "file"
        )
        export_region_action.triggered.connect(self.export_region)
        QTimer.singleShot(
            0, partial(self.moveAction, export_region_action, window.qwindow())
        )

    # Take the existing export_region action and move it to be after file_export in the file menu
    def moveAction(self, action, qwindow):
        menu_bar = qwindow.menuBar()
        file_menu_action = next(
            (a for a in menu_bar.actions() if a.objectName() == "file"), None
        )
        if file_menu_action:
            file_menu = file_menu_action.menu()
            for file_action in file_menu.actions():
                if file_action.objectName() == "file_export_advanced":
                    file_menu.removeAction(action)
                    file_menu.insertAction(file_action, action)


Krita.instance().addExtension(ExportRegionExtension(Krita.instance()))
