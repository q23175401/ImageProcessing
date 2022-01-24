from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QBitmap, QBrush, QImage, QPainter, QPen, QColor, QPixmap, QResizeEvent, QCursor
from PyQt5.QtCore import QPoint, QRect, QSize, Qt, QObject, pyqtSignal
from pathlib import Path

import numpy as np
from IMPS import MyImage
from PIL import ImageQt, Image

# from color_adjust_tool import ColorAdjustWidget
# from spot_repairing_tool import SpotRepairingWidget


class DrawingCanvas:
    class CanvasEventHandler(QObject):
        playgroundChangeEvent = pyqtSignal()
        onMouseReleaseEvent = pyqtSignal()

    def __init__(self, spotPaintWidget, colorAdjustWidget, parent=None):
        self.eventHandler = self.CanvasEventHandler()
        self.spotPaintWidget = spotPaintWidget
        self.colorAdjustWidget = colorAdjustWidget

        # setting canvas
        self.c = QWidget(parent=parent)  # generate a widget to paint
        # self.c.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        self.c.setCursor(QCursor(QPixmap("Resources/Images/cursor.png").scaled(20, 20)))
        self.c.setMouseTracking(True)
        # setting shape, geometry and event
        self._setCanvasBodyColor()
        self._setCanvasBodyEvent()

        self.resetMousePosRecord()
        self.clearImage()

    def getCurrentIm(self):
        return MyImage.fromArray(self.current_im_array)

    @property
    def drawMaskRadius(self):
        return self.spotPaintWidget.getSpotRadius()

    def resetMousePosRecord(self):
        # setting default parameters
        self.px_start = -1
        self.py_start = -1

        self.mouse_pos_x = 0
        self.mouse_pos_y = 0

        self.min_mouse_x = -1
        self.max_mouse_x = -1
        self.min_mouse_y = -1
        self.max_mouse_y = -1

    def hasImage(self):
        return self.image is not None

    def clearImage(self):
        self.image = None
        self.current_im_pixmap = None
        self.current_im_array = None
        self.selected_pix_mask = None
        self.current_im_array_changed = False

    def readImage(self, filename="Resources/Images/horse1.jpg"):
        self.clearImage()
        try:
            images_path = Path(filename)
            one_image = MyImage(str(images_path.absolute()))
            self.image = one_image
            self.setCurrentImArray(one_image.im.copy())
        except Exception as e:
            self.clearImage()
            print(e)
            print("read Image faided")

        self.update()

    def setCurrentImArray(self, arr):
        self.current_im_array = arr
        self.current_im_array_changed = True

    def setCurrentImPixmap(self, pixmap):
        self.current_im_pixmap = pixmap
        self.current_im_array_changed = False

    def geneateCurrentImPixmap(self):
        if self.current_im_array_changed == False:
            return self.current_im_pixmap
        h, w, c = self.image.im.shape
        s = max(h, w)

        im_array = self.current_im_array

        dh = (w - h) // 2 if h < w else 0
        dw = (h - w) // 2 if h > w else 0
        square_im = np.zeros([s, s, c], dtype=np.uint8)
        square_im[dh : dh + h, dw : dw + w, :] = im_array
        qImg = Image.fromarray(square_im).toqimage()
        imgMap = QPixmap.fromImage(qImg).scaled(self.c.width(), self.c.height())

        self.setCurrentImPixmap(imgMap)
        return imgMap

    def update(self):
        self.c.update()

    def _setCanvasBodyColor(self):
        self.c.setStyleSheet("background: black;")

    def _setCanvasBodyEvent(self):
        self.c.paintEvent = self._paintEvent
        self.c.mouseMoveEvent = self._mouseMoveEvent
        self.c.mousePressEvent = self._mousePressEvent
        self.c.mouseReleaseEvent = self._mouseReleaseEvent
        self.c.resizeEvent = self._resizeEvent
        self.c.onHovered = self._onHovered

    def _resizeEvent(self, event: QResizeEvent):
        self.c.update()

    def _paintEvent(self, event):  # paint canvas event after update(clear)

        painter = QPainter()
        painter.begin(self.c)

        if self.image:
            imgMap = self.geneateCurrentImPixmap()
            painter.drawPixmap(0, 0, imgMap.width(), imgMap.height(), imgMap)

            # if self.min_mouse_x > -1:
            #     pen = QPen(QColor(255, 255, 255), 1)
            #     painter.setPen(pen)

            #     f_x, t_x = self.min_mouse_x - self.drawMaskRadius - 10, self.max_mouse_x + self.drawMaskRadius + 10
            #     f_y, t_y = self.min_mouse_y - self.drawMaskRadius - 10, self.max_mouse_y + self.drawMaskRadius + 10
            #     painter.drawRect(f_x, f_y, t_x - f_x, t_y - f_y)

            if self.selected_pix_mask is not None:
                self.c.setMask(self.selected_pix_mask)

            if self.mouse_pos_x > -1 and self.mouse_pos_y > -1:
                pen = QPen(QColor(0, 0, 0), 1)
                painter.setPen(pen)

                painter.drawEllipse(
                    self.mouse_pos_x - self.drawMaskRadius,
                    self.mouse_pos_y - self.drawMaskRadius,
                    self.drawMaskRadius * 2,
                    self.drawMaskRadius * 2,
                )

        painter.end()

    def putCircleOnMask(self, radius, canvas_w, canvas_h):
        if self.selected_pix_mask is None:
            return

        pix_h = canvas_h - radius
        pix_w = canvas_w - radius

        maskPainter = QPainter(self.selected_pix_mask)

        pen = QPen(QColor(255, 255, 255), 1)
        maskPainter.setPen(pen)
        brush = QBrush(QColor(255, 255, 255), Qt.BrushStyle.SolidPattern)
        maskPainter.setBrush(brush)
        maskPainter.drawEllipse(pix_w, pix_h, radius * 2, radius * 2)

    def generateEmptyMask(self) -> QBitmap:
        w, h = self.c.width(), self.c.height()
        mask = QBitmap(w, h)
        mask.fill(QColor(0, 0, 0))

        return mask

    def _mousePressEvent(self, event):
        self.px_start = event.pos().x()
        self.py_start = event.pos().y()
        self.mouse_pos_x = event.pos().x()
        self.mouse_pos_y = event.pos().y()

        self.min_mouse_x = self.mouse_pos_x
        self.max_mouse_x = self.mouse_pos_x
        self.min_mouse_y = self.mouse_pos_y
        self.max_mouse_y = self.mouse_pos_y

        if self.image is not None:
            # h, w, c = self.image.im.shape
            self.selected_pix_mask = self.generateEmptyMask()
            self.putCircleOnMask(self.drawMaskRadius, event.pos().x(), event.pos().y())
            self.c.update()

    def clearMask(self):
        self.selected_pix_mask.clear()
        self.selected_pix_mask = None
        self.c.clearMask()
        pass

    def _mouseReleaseEvent(self, event):
        if self.image is None:
            return

        self.eventHandler.onMouseReleaseEvent.emit()

        f_w, t_w = self.min_mouse_x - self.drawMaskRadius - 10, self.max_mouse_x + self.drawMaskRadius + 10
        f_h, t_h = self.min_mouse_y - self.drawMaskRadius - 10, self.max_mouse_y + self.drawMaskRadius + 10

        if t_w - f_w <= 1 or t_h - f_h <= 1:
            return

        h, w, c = self.current_im_array.shape
        # print(h, w)
        s = max(h, w)
        diff = abs(h - w) // 2
        diff_w = diff if h > w else 0
        diff_h = diff if w > h else 0
        cw = self.c.width()
        ch = self.c.height()

        im_fh = int(f_h * s / ch - diff_h)
        im_th = int(t_h * s / ch - diff_h)
        im_fw = int(f_w * s / cw - diff_w)
        im_tw = int(t_w * s / cw - diff_w)

        im_fh = im_fh if 0 <= im_fh else 0 if im_fh < h else h
        im_th = im_th if 0 <= im_th else 0 if im_th < h else h
        im_fw = im_fw if 0 <= im_fw else 0 if im_fw < w else w
        im_tw = im_tw if 0 <= im_tw else 0 if im_tw < w else w

        selected_im = self.current_im_array[im_fh:im_th, im_fw:im_tw, :]
        # print(selected_im.shape)
        maskIm = self.selected_pix_mask.toImage().scaled(s, s)
        im_mask = np.array(Image.fromqimage(maskIm))

        mk_fh = int(f_h * s / ch)
        mk_th = int(t_h * s / ch)
        mk_fh = mk_fh if diff_h <= mk_fh else diff_h if mk_fh < diff_h + h else diff_h + h
        mk_th = mk_th if diff_h <= mk_th else diff_h if mk_th < diff_h + h else diff_h + h
        mk_fw = int(f_w * s / cw)
        mk_tw = int(t_w * s / cw)

        mk_fw = mk_fw if diff_w <= mk_fw else diff_w if mk_fw < diff_w + w else diff_w + w
        mk_tw = mk_tw if diff_w <= mk_tw else diff_w if mk_tw < diff_w + w else diff_w + w

        selected_im_mask = im_mask[mk_fh:mk_th, mk_fw:mk_tw, :]

        im = MyImage.fromArray(selected_im)
        # im.show()

        selected_im_mask[selected_im_mask > 0] = 1
        selected_im_mask = selected_im_mask.astype(np.bool)

        # processed_im = im.gaussianBlur(mean=0, std=1, kernel_size=(5, 5))
        # processed_im = im.min(kernel_size=(5, 5), mask=selected_im_mask[:, :, 0])
        processed_im = self.spotPaintWidget.repair(im, mask=selected_im_mask[:, :, 0])
        processed_im = self.colorAdjustWidget.colorAdjust(processed_im, mask=selected_im_mask[:, :, 0])
        # processed_im = im.medium(kernel_size=(5, 5), mask=selected_im_mask[:, :, 0])

        self.current_im_array[im_fh:im_th, im_fw:im_tw, :] = processed_im.im
        self.setCurrentImArray(self.current_im_array)

        self.clearMask()
        self.update()

        self.px_start = -1
        self.py_start = -1

    def _onHovered(self, event):
        self.mouse_pos_x = event.pos().x()
        self.mouse_pos_y = event.pos().y()
        print(self.mouse_pos_x, self.mouse_pos_y)

    def _mouseMoveEvent(self, event):
        self.mouse_pos_x = event.pos().x()
        self.mouse_pos_y = event.pos().y()

        if self.selected_pix_mask is not None:
            if self.mouse_pos_x > self.max_mouse_x:
                self.max_mouse_x = self.mouse_pos_x

            if self.mouse_pos_x < self.min_mouse_x:
                self.min_mouse_x = self.mouse_pos_x

            if self.mouse_pos_y > self.max_mouse_y:
                self.max_mouse_y = self.mouse_pos_y

            if self.mouse_pos_y < self.min_mouse_y:
                self.min_mouse_y = self.mouse_pos_y

        self.putCircleOnMask(self.drawMaskRadius, self.mouse_pos_x, self.mouse_pos_y)
        self.update()
