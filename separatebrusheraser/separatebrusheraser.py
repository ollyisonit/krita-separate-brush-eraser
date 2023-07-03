# type: ignore
from krita import *
from PyQt5.QtWidgets import QWidget, QAction
from functools import partial
from pprint import pprint
from .api_krita import Krita as KritaAPI

BRUSH_ACTION = "dninosores_activate_brush"
ERASE_ACTION = "dninosores_activate_eraser"
MENU_LOCATION = "tools/scripts/brush and eraser"
BRUSH_MODE = "BRUSH"
ERASER_MODE = "ERASER"


class BrushSettings:
    preset = None
    size = None
    flow = None
    opacity = None

    def loadSettings(self):
        self.preset = KritaAPI.get_active_view().brush_preset
        self.size = KritaAPI.get_active_view().brush_size
        self.flow = KritaAPI.get_active_view().flow
        self.opacity = KritaAPI.get_active_view().opacity

    def applySettings(self):
        KritaAPI.get_active_view().brush_preset = self.preset
        KritaAPI.get_active_view().brush_size = self.size
        KritaAPI.get_active_view().flow = self.flow
        KritaAPI.get_active_view().opacity = self.opacity


class BrushState:
    # Store a brush state for each view
    eraser_on: bool = False
    brush_settings: BrushSettings = None
    eraser_settings: BrushSettings = None

    def apply():
        # Change the brush to match the settings stored in here
        # Also if the brush switches from eraser, store the eraser settings and same for brush
        # Then return the new brush state I guess
        # Maybe we should just have this method straight up apply the settings as stated
        # And make a different method for tracking what brush_settings and eraser_settings should be?
        # Maybe this method should take in whether the eraser should be on or off, and then it can handle everything else from there
        # Since you can look at the current state of the brush and figure out if the state is changing or not
        # Then apply / save presets if you're switching the state and not do that otherwise
        # Then you can just call this method anywhere you need to set the eraser to be either on or off
        # And it will just exit if the eraser is already in the right state.
        pass


class SeparateBrushEraserExtension(Extension):
    brush_settings: dict[str, BrushSettings] = {}
    eraser_settings: dict[str, BrushSettings] = {}

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
        # Toggles eraser if it isn't in the right state
        if self.eraser_active() != is_on:
            Application.action("erase_action").trigger()

            # (This may not be the right place to check for this)
            # It's possible to have a situation where you have the brush tool active but then you apply a brush preset that turns on the eraser
            # Or you have the eraser active but you apply a brush preset that turns on the brush
            # I actually think the best way around this might be to, each time the eraser is toggled, check that the eraser's status matches the one stored in here
            # Then if it doesn't match, set it back
            # Just generally, we need to figure out how we want this to behave when you toggle the eraser manually by clicking on the eraser icon, as well as when the eraser is
            # activated by a tool preset
            # I think ideally the tool preset should not affect the eraser status, when you activate a preset it should just not change the eraser
            # When you click the eraser icon it should switch to the eraser tool as if you pressed D, which could prove challenging because that would mean we have to infiltrate
            # the top bar
            # So in general calling the "erase_action" should set the eraser to match whatever value is stored here, meaning this plugin has full control over the eraser
            # There could also be another "toggle_eraser" action that essentially copies the brush settings to the eraser or vice versa

            # Implement the straight-line action manually as well

            # Toggles eraser again if applying presets scrambled things
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
