from krita import Krita, Extension  # type: ignore
from PyQt5.QtWidgets import QToolBar, QToolButton, QMenu
from PyQt5 import QtGui
from PyQt5.QtCore import QTimer, QObject, QEvent, Qt
from functools import partial
from .api_krita import Krita as KritaAPI
from .api_krita.enums import Tool

KRITA_ERASE_ACTION = "erase_action"
BRUSH_ACTION = "dninosores_activate_brush"
ERASE_ACTION = "dninosores_activate_eraser"
ERASE_ON_ACTION = "dninosores_eraser_on"
ERASE_OFF_ACTION = "dninosores_eraser_off"
ERASE_TOGGLE_ACTION = "dninosores_eraser_toggle"
MENU_LOCATION = "tools/scripts"
MENU_GROUP_NAME = "SeparateBrushEraser"
BRUSH_MODE = "BRUSH"
ERASER_MODE = "ERASER"

DEBUG = False


def print_dbg(msg):
    if DEBUG:
        print(msg)


def get_action(name: str):
    """Wrapper for non-type-safe getting action from Krita instance."""
    return Krita.instance().action(name)


class BrushSettings:

    def loadSettings(self):
        self.preset = KritaAPI.get_active_view().brush_preset
        self.size = KritaAPI.get_active_view().brush_size
        self.flow = KritaAPI.get_active_view().flow
        self.opacity = KritaAPI.get_active_view().opacity
        return self

    def applySettings(self):
        KritaAPI.get_active_view().brush_preset = self.preset
        KritaAPI.get_active_view().brush_size = self.size
        KritaAPI.get_active_view().flow = self.flow
        KritaAPI.get_active_view().opacity = self.opacity
        return self


class BrushState:
    # Store a brush state for each view
    eraser_on: bool = False
    brush_settings: BrushSettings | None = None
    eraser_settings: BrushSettings | None = None


class SeparateBrushEraserExtension(Extension):
    brush_state = None
    # Toggled on when the line tool is temporarily activated by modifier key
    tmp_line_activation: bool = False

    def __init__(self, parent):
        super().__init__(parent)
        self.filter = LineModifierFilter(self, Qt.Key.Key_Shift)

    def switch_to_brush(self):
        KritaAPI.trigger_action("KritaShape/KisToolBrush")

    def eraser_active(self):
        return get_action(KRITA_ERASE_ACTION).isChecked()

    def get_current_brush_state(self):
        if (not KritaAPI.get_active_view() or not Krita.instance().
                activeWindow().activeView().currentBrushPreset()):
            return None
        if self.brush_state:
            return self.brush_state
        else:
            current_state = BrushState()
            current_state.eraser_on = self.eraser_active()
            current_state.brush_settings = BrushSettings().loadSettings()
            current_state.eraser_settings = BrushSettings().loadSettings()
            self.brush_state = current_state
            return current_state

    def apply_brush_state(self, state: BrushState) -> BrushState:
        """Sets brush settings to match the given state"""
        if self.eraser_active() == state.eraser_on:
            return state

        current_settings = BrushSettings().loadSettings()
        # toggling the eraser on
        if state.eraser_on:
            if state.eraser_settings:
                state.eraser_settings.applySettings()
            state.brush_settings = current_settings
        else:
            state.eraser_settings = current_settings
            if state.brush_settings:
                state.brush_settings.applySettings()
        self.verify_eraser_state()
        return state

    def apply_current_brush_state(self):
        state = self.get_current_brush_state()
        if state:
            return self.apply_brush_state(state)

    def activate_brush(self, switchTool=True):
        if not self.get_current_brush_state():
            return
        self.get_current_brush_state().eraser_on = False  # type: ignore
        if switchTool:
            self.switch_to_brush()
        self.apply_current_brush_state()
        QTimer.singleShot(0, self.verify_eraser_state)

    def activate_eraser(self, switchTool=True):
        if not self.get_current_brush_state():
            return
        self.get_current_brush_state().eraser_on = True  # type: ignore
        if switchTool:
            self.switch_to_brush()
        self.apply_current_brush_state()
        QTimer.singleShot(0, self.verify_eraser_state)

    def on_brush_toggled(self, toggled):
        current_brush_state = self.get_current_brush_state()
        if not current_brush_state:
            return
        # Triggers when krita switches to/from the brush tool for any reason. Does not trigger if the brush tool is already selected.
        if toggled:
            pass
        # Don't switch eraser state if we're activating the line tool temporarily with modifier key
        elif self.tmp_line_activation:
            pass
        else:
            current_brush_state.eraser_on = False
            self.apply_current_brush_state()

    def verify_eraser_state(self):
        current_brush_state = self.get_current_brush_state()
        if current_brush_state:
            desired_state = current_brush_state.eraser_on
            if desired_state != self.eraser_active():
                KritaAPI.trigger_action(KRITA_ERASE_ACTION)

    def on_eraser_action(self, toggled):
        pass
        # self.get_eraser_button().setChecked(self.eraser_active())
        # self.verify_eraser_state()

    def classic_krita_eraser_toggle_auto(self):
        if self.brush_state:
            self.classic_krita_eraser_toggle(not self.brush_state.eraser_on)

    def classic_krita_eraser_toggle(self, toggled):
        # self.verify_eraser_state()
        # toggled = self.get_current_brush_state().eraser_on
        if toggled:
            self.activate_eraser(False)
        else:
            self.activate_brush(False)

    def on_eraser_button_clicked(self, toggled):
        # print(f"Clicked with value {toggled}")
        # Actually I think it would be better if this toggled like regular krita
        # i.e. swap the brush presets, then toggle eraser without switching tool
        # actually don't swap the brush presets but to toggle eraser without switching tool
        self.classic_krita_eraser_toggle(toggled)

    def on_eraser_button_toggled(self, toggled):
        # print(f"Button toggled with value {toggled}")'
        eraser_button = self.get_eraser_button()
        if eraser_button:
            eraser_button.setChecked(self.eraser_active())
        # self.verify_eraser_state()

    def setup(self):
        pass

    def createActions(self, window):

        # menu = QMenu(MENU_GROUP_NAME, window.qwindow())
        # actions should be:
        # Switch to brush / switch to eraser, which activate the brush tool
        # Activate brush / eraser, which switch without activating the brush tool
        # Toggle, which toggles between the two options without switching the tool
        # A 'when you hold shift temporarily switch to the line tool without deactivating eraser' action
        menu_action = window.createAction(
            MENU_GROUP_NAME, MENU_GROUP_NAME,
            MENU_LOCATION + "/" + MENU_GROUP_NAME)
        menu = QMenu(MENU_GROUP_NAME, window.qwindow())
        menu_action.setMenu(menu)
        activate_brush_action = window.createAction(
            BRUSH_ACTION, "Switch to Freehand Brush",
            MENU_LOCATION + "/" + MENU_GROUP_NAME)
        activate_eraser_action = window.createAction(
            ERASE_ACTION, "Switch to Freehand Eraser",
            MENU_LOCATION + "/" + MENU_GROUP_NAME)
        enable_eraser_action = window.createAction(
            ERASE_ON_ACTION, "Activate Eraser Preset for Current Tool",
            MENU_LOCATION + "/" + MENU_GROUP_NAME)
        disable_eraser_action = window.createAction(
            ERASE_OFF_ACTION, "Activate Brush Preset for Current Tool",
            MENU_LOCATION + "/" + MENU_GROUP_NAME)
        toggle_eraser_action = window.createAction(
            ERASE_TOGGLE_ACTION, "Toggle Eraser Preset for Current Tool",
            MENU_LOCATION + "/" + MENU_GROUP_NAME)

        activate_brush_action.triggered.connect(
            partial(self.activate_brush, True))
        activate_eraser_action.triggered.connect(
            partial(self.activate_eraser, True))
        enable_eraser_action.triggered.connect(
            partial(self.activate_eraser, False))
        disable_eraser_action.triggered.connect(
            partial(self.activate_brush, False))
        toggle_eraser_action.triggered.connect(
            self.classic_krita_eraser_toggle_auto)

        appNotifier = KritaAPI.instance.notifier()
        appNotifier.setActive(True)

        def installLineModifierFilter(_view: QObject):
            for item, level in IterHierarchy(
                    KritaAPI.instance.activeWindow().qwindow()):
                if item.metaObject().className() == "Viewport":
                    print_dbg("Installing line modifier filter")
                    item.removeEventFilter(self.filter)
                    item.installEventFilter(self.filter)

        appNotifier.viewCreated.connect(installLineModifierFilter)

        QTimer.singleShot(500, self.bind_brush_toggled)

    def get_eraser_button(self) -> QToolButton | None:
        qwin = KritaAPI.get_active_qwindow()
        pobj = qwin.findChild(QToolBar, 'BrushesAndStuff')
        eraser_button = None
        for item, depth in IterHierarchy(pobj):
            try:
                if item.defaultAction() == get_action(KRITA_ERASE_ACTION):
                    eraser_button = item
            except Exception:
                pass
        return eraser_button

    def print_state(self):
        current_brush_state = self.get_current_brush_state()
        eraser_button = self.get_eraser_button()
        if current_brush_state:
            desired_state = current_brush_state.eraser_on
            print(f"Eraser should be {desired_state}")
            if eraser_button:
                print(f"Button checked is {eraser_button.isChecked()}")
            else:
                print("Eraser button not found!")
            print(f"Eraser action is {self.eraser_active()}")
            print("\n")

    def bind_brush_toggled(self):
        success = False
        Krita.instance().action(KRITA_ERASE_ACTION).triggered.connect(
            self.on_eraser_action)
        for docker in Krita.instance().dockers():
            if docker.objectName() == "ToolBox":
                for item, level in IterHierarchy(docker):
                    if item.objectName() == "KritaShape/KisToolBrush":
                        brush_tool = item
                        brush_tool.toggled.connect(self.on_brush_toggled)
                        success = True
        if not success:
            print(
                "Binding eraser toggle to brush button failed. Try restarting Krita."
            )
        eraser_button = self.get_eraser_button()
        if eraser_button:
            eraser_button.toggled.connect(self.on_eraser_button_toggled)
            eraser_button.clicked.connect(self.on_eraser_button_clicked)
        else:
            print(
                "Binding eraser toggle to erase button failed. Try restarting Krita."
            )
        timer = QTimer(KritaAPI.get_active_qwindow())
        timer.timeout.connect(self.verify_eraser_state)
        timer.start(1)


class LineModifierFilter(QObject):
    """EventFilter that listens for a certain modifier key and tells the extension to temporarily switch to the line tool when it the key is pressed."""
    extension: SeparateBrushEraserExtension
    modifier_key: int = Qt.Key.Key_Shift

    def __init__(self, extension: SeparateBrushEraserExtension,
                 modifier_key: int):
        super().__init__()
        self.extension = extension
        self.modifier_key = modifier_key

    def eventFilter(self, a0: QObject | None, a1: QEvent | None) -> bool:
        event = a1
        if event and isinstance(event, QtGui.QKeyEvent):
            if KritaAPI.active_tool == Tool.FREEHAND_BRUSH and event.key(
            ) == self.modifier_key and event.type() == QEvent.Type.KeyPress:
                print_dbg("event filter activated")
                self.extension.tmp_line_activation = True
                KritaAPI.active_tool = Tool.LINE
            if KritaAPI.active_tool == Tool.LINE and event.key(
            ) == self.modifier_key and event.type() == QEvent.Type.KeyRelease:
                print_dbg("event filter activated")
                if self.extension.tmp_line_activation:
                    KritaAPI.active_tool = Tool.FREEHAND_BRUSH
                    self.extension.tmp_line_activation = False
        return False


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
