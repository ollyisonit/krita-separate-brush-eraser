# SPDX-FileCopyrightText: © 2022-2023 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from ...qt_compat import Qt, QPainter, QImage, QtGui
QPixmap = QtGui.QPixmap
QBrush = QtGui.QBrush


class PixmapTransform:
    """Utilities for `QPixmap` transformation."""

    @staticmethod
    def make_pixmap_round(pixmap: QPixmap) -> QPixmap:
        """Make corners of the pixmap transparent, to make image a circle."""
        image = pixmap.toImage()
        image.convertToFormat(QImage.Format_ARGB32)

        imgsize = min(image.width(), image.height())
        out_img = QImage(imgsize, imgsize, QImage.Format_ARGB32)
        out_img.fill(Qt.transparent)

        painter = QPainter(out_img)
        painter.setBrush(QBrush(image))
        painter.setPen(Qt.NoPen)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.drawEllipse(0, 0, imgsize, imgsize)
        painter.end()

        return QPixmap.fromImage(out_img)

    @staticmethod
    def scale_pixmap(pixmap: QPixmap, size_px: int) -> QPixmap:
        """Scale a square pixmal to new size."""
        return pixmap.scaled(
            size_px,
            size_px,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
