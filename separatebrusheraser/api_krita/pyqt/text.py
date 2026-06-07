# SPDX-FileCopyrightText: © 2022-2023 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass, field
from ...qt_compat import QtGui
QColor = QtGui.QColor


@dataclass
class Text:
    """Text along with its color."""

    value: str
    color: QColor = field(default_factory=lambda: QColor("white"))
