import sys

# Try PyQt6 first
try:
    from PyQt6 import QtCore, QtGui, QtWidgets, QtSql
    PYQT6 = True
except ImportError:
    try:
        from PyQt5 import QtCore, QtGui, QtWidgets, QtSql
        PYQT6 = False
    except ImportError:
        # Fallback to avoid breaking completely if imported under typings/tests
        raise ImportError("Neither PyQt6 nor PyQt5 could be imported.")

# Helper to convert enum / flag values to integer (compatible with PyQt5 & PyQt6)
def to_int(val):
    if hasattr(val, "value"):
        return val.value
    return int(val)

# QAction moved from QtWidgets to QtGui in Qt6
if PYQT6:
    QAction = QtGui.QAction
else:
    QAction = QtWidgets.QAction

# QDesktopWidget replacement helper
def get_screen_width() -> int:
    if PYQT6:
        screen = QtGui.QGuiApplication.primaryScreen()
        return screen.geometry().width() if screen else 1920
    else:
        return QtWidgets.QDesktopWidget().screenGeometry(-1).width()

# Wrap Qt to handle different namespaces for enums
class QtWrapper:
    def __init__(self, original_qt):
        self._qt = original_qt

    def __getattr__(self, name):
        try:
            return getattr(self._qt, name)
        except AttributeError:
            pass

        if PYQT6:
            # Map of common enum classes under Qt in PyQt6
            mappers = [
                self._qt.GlobalColor,
                self._qt.PenStyle,
                self._qt.AspectRatioMode,
                self._qt.TransformationMode,
                self._qt.CursorShape,
                self._qt.WindowType,
                self._qt.WidgetAttribute,
                self._qt.Key,
                self._qt.KeyboardModifier,
            ]
            for mapper in mappers:
                if hasattr(mapper, name):
                    return getattr(mapper, name)

        raise AttributeError(f"module 'Qt' has no attribute '{name}'")

# Replace QtCore.Qt with wrapped version
Qt = QtWrapper(QtCore.Qt)

# Subclass QImage and QPainter to add PyQt5 compatibility attributes on PyQt6
class QImage(QtGui.QImage):
    if PYQT6:
        Format_ARGB32 = QtGui.QImage.Format.Format_ARGB32

class QPainter(QtGui.QPainter):
    if PYQT6:
        Antialiasing = QtGui.QPainter.RenderHint.Antialiasing
