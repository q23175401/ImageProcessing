from typing import List, Tuple
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget
from PyQt5.QtGui import QBrush, QPainter, QPen, QColor, QResizeEvent
from PyQt5.QtCore import QPoint, QRect, Qt, QObject, pyqtSignal
import numpy as np

# my modules
from utils import resource_path
from drawing_canvas import DrawingCanvas
from IMPS import MyImage

# from hw2_playground import Playground, Point2D
ui_path = resource_path("./qtui/colorAdjustTool.ui")
ui_class, window_class = uic.loadUiType(ui_path)


class ColorAdjustWidget(window_class):
    def __init__(self) -> None:
        super().__init__()
        self.max_seg_num = 300
        self.seg_num = 30
        self.selectedPoint = None

        self.ui = ui_class()
        self.ui.setupUi(self)
        self._setUpExtraWidgets()
        self._setUpUiEvent()

        # start from linear  mapping
        self.resetAllColorMap()
        self.generateAllMapValues()

    def resetAllColorMap(self):
        self.resetColorMap("r")
        self.resetColorMap("g")
        self.resetColorMap("b")

    def resetColorMap(self, color="r"):
        if color == "r":
            self.r_control_points_dict = {}
        elif color == "g":
            self.g_control_points_dict = {}
        elif color == "b":
            self.b_control_points_dict = {}
        self._addControlPoints([(0, 0), (255, 255)], color)

    def generateAllMapValues(self):
        self.r_map_values = self._generateMappingValues(color="r")
        self.g_map_values = self._generateMappingValues(color="g")
        self.b_map_values = self._generateMappingValues(color="b")

    def _deletePoint(self, color=None, fPoint=None) -> bool:
        if fPoint is None:
            if self.selectedPoint is None:
                return False

            x, y, *_ = self.selectedPoint
            fPoint = (x, y)

        if color is None:
            color = self.ui.color_tv.currentWidget().objectName()[0]

        point_dict = self._selectPointsDict(color)

        ori_value = point_dict.get(fPoint[0], -1)
        if ori_value == -1 or ori_value != fPoint[1]:
            return False

        if fPoint[0] in (0, 255):
            point_dict[fPoint[0]] = fPoint[0]
        else:
            del point_dict[fPoint[0]]
        return True

    def _movePoint(self, color, fPoint: Tuple[int, int], tPoint: Tuple[int, int]) -> bool:
        point_dict = self._selectPointsDict(color)

        if self._deletePoint(color, fPoint):
            point_dict[tPoint[0]] = tPoint[1]
            return True
        else:
            return False

    def _selectPointsDict(self, color="r"):
        if color == "r":
            points = self.r_control_points_dict
        elif color == "g":
            points = self.g_control_points_dict
        elif color == "b":
            points = self.b_control_points_dict
        else:
            raise NotImplementedError("the color is not implemented")
        return points

    def _getSortedPoints(self, color):
        points_dict = self._selectPointsDict(color)
        pairs = sorted(points_dict.items())
        return pairs

    def _getPairPoints(self, color):
        pairs = self._getSortedPoints(color)

        assert len(pairs) >= 2, "not enough points in control points"
        first_x, first_y = pairs[0]
        for pi in range(1, len(pairs)):
            second_x, second_y = pairs[pi]

            yield first_x, first_y, second_x, second_y

            first_x = second_x
            first_y = second_y

    def _generateMappingValues(self, color="r"):
        map_values = np.zeros(256)
        for first_x, first_y, second_x, second_y in self._getPairPoints(color):

            a = (second_y - first_y) / (second_x - first_x)
            b = first_y

            for x in range(first_x, second_x + 1):
                map_values[x] = int(a * (x - first_x) + b)

            # print(first_x, first_y, second_x, second_y, color)
        # print(color, map_values)
        return map_values

    def _addControlPoints(self, points: List[Tuple[int, int]], color="r"):
        if points is None or len(points) == 0:
            return

        points_dict = self._selectPointsDict(color)
        for key, value in points:
            if 0 <= key < 256:
                points_dict[key] = value

    def _setUpExtraWidgets(self):
        pass

    def _setUpUiEvent(self):

        self.ui.red_line_canvas.paintEvent = lambda e: self._paintEvent(e, self.ui.red_line_canvas)
        self.ui.green_line_canvas.paintEvent = lambda e: self._paintEvent(e, self.ui.green_line_canvas)
        self.ui.blue_line_canvas.paintEvent = lambda e: self._paintEvent(e, self.ui.blue_line_canvas)

        self.ui.red_line_canvas.mousePressEvent = lambda e: self._mousePressEvent(e, self.ui.red_line_canvas)
        self.ui.green_line_canvas.mousePressEvent = lambda e: self._mousePressEvent(e, self.ui.green_line_canvas)
        self.ui.blue_line_canvas.mousePressEvent = lambda e: self._mousePressEvent(e, self.ui.blue_line_canvas)

        self.ui.red_line_canvas.mouseReleaseEvent = lambda e: self._mouseReleaseEvent(e, self.ui.red_line_canvas)
        self.ui.green_line_canvas.mouseReleaseEvent = lambda e: self._mouseReleaseEvent(e, self.ui.green_line_canvas)
        self.ui.blue_line_canvas.mouseReleaseEvent = lambda e: self._mouseReleaseEvent(e, self.ui.blue_line_canvas)

        self.ui.red_line_canvas.mouseMoveEvent = lambda e: self._mouseMoveEvent(e, self.ui.red_line_canvas)
        self.ui.green_line_canvas.mouseMoveEvent = lambda e: self._mouseMoveEvent(e, self.ui.green_line_canvas)
        self.ui.blue_line_canvas.mouseMoveEvent = lambda e: self._mouseMoveEvent(e, self.ui.blue_line_canvas)

        self.ui.red_line_canvas.mouseDoubleClickEvent = lambda e: self._doubleClickEvent(e, self.ui.red_line_canvas)
        self.ui.green_line_canvas.mouseDoubleClickEvent = lambda e: self._doubleClickEvent(e, self.ui.green_line_canvas)
        self.ui.blue_line_canvas.mouseDoubleClickEvent = lambda e: self._doubleClickEvent(e, self.ui.blue_line_canvas)

        self.ui.reset_color_btn.clicked.connect(self._onResetOneColor)

        def deletePointUi():
            self._deletePoint()
            self.update()

        self.ui.delete_selected_point_btn.clicked.connect(deletePointUi)

        self._calculateGeomertyProperties(self.ui.blue_line_canvas)

    def _onResetOneColor(self, e):
        color = self.ui.color_tv.currentWidget().objectName()[0]
        self.resetColorMap(color)

        self.update()

    def _getColorByCanvas(self, canvas):
        color = canvas.objectName()[0]
        if color not in ("r", "g", "b"):
            raise NotImplementedError("unknown name selected")

        return color

    def _paintEvent(self, event, canvas):
        color = self._getColorByCanvas(canvas)
        if color == "r":
            line_color = QColor(255, 0, 0)
        elif color == "g":
            line_color = QColor(0, 255, 0)
        elif color == "b":
            line_color = QColor(0, 0, 255)
        else:
            return

        # draw axes
        self._calculateGeomertyProperties(canvas)

        # alias
        max_seg_num = self.max_seg_num
        seg_num = self.seg_num
        w_seg = self.w_seg
        h_seg = self.h_seg

        painter = QPainter()
        painter.begin(canvas)

        pen = QPen(QColor(0, 0, 0), 2)
        brush = QBrush(QColor(0, 0, 0), Qt.BrushStyle.SolidPattern)
        painter.setPen(pen)
        painter.setBrush(brush)

        vl_sx = w_seg * seg_num
        vl_sy = h_seg * seg_num
        vl_tx = w_seg * seg_num
        vl_ty = h_seg * (max_seg_num - seg_num)
        hl_sx = w_seg * seg_num
        hl_sy = h_seg * (max_seg_num - seg_num)
        hl_tx = w_seg * (max_seg_num - seg_num)
        hl_ty = h_seg * (max_seg_num - seg_num)

        # draw stright line
        painter.drawLine(int(vl_sx), int(vl_sy), int(vl_tx), int(vl_ty))

        # draw horizontal line
        painter.drawLine(int(hl_sx), int(hl_sy), int(hl_tx), int(hl_ty))

        # put text 1
        painter.drawText(int(w_seg * (max_seg_num - seg_num + 5)), int(h_seg * (max_seg_num - seg_num + 5)), "1")
        painter.drawText(int(w_seg * (seg_num - 3)), int(h_seg * (seg_num - 5)), "1")
        # put text 0
        painter.drawText(int(w_seg * (seg_num - 3 - 7)), int(h_seg * (max_seg_num - seg_num + 5 + 5)), "0")

        pen = QPen(line_color, 2)
        brush = QBrush(line_color, Qt.BrushStyle.SolidPattern)
        painter.setPen(pen)
        painter.setBrush(brush)

        for first_x, first_y, second_x, second_y in self._getPairPoints(color):
            qsx, qsy, qtx, qty = (
                self._getqx(first_x),
                self._getqy(first_y),
                self._getqx(second_x),
                self._getqy(second_y),
            )
            painter.drawLine(qsx, qsy, qtx, qty)
            # painter.drawRect(qsx, qsy, qtx - qsx, qty - qsy)

        pen = QPen(QColor(229, 200, 27), 1)
        brush = QBrush(QColor(229, 200, 27))
        painter.setPen(pen)
        painter.setBrush(brush)
        for x, y in self._getSortedPoints(color):
            if self.selectedPoint is not None:
                selected_x, selected_y, *_ = self.selectedPoint
                if selected_x == x and selected_y == y:
                    pen = QPen(QColor(255, 255, 255), 1)
                    brush = QBrush(QColor(255, 255, 255))
                    painter.setPen(pen)
                    painter.setBrush(brush)
                else:
                    pen = QPen(QColor(229, 200, 27), 1)
                    brush = QBrush(QColor(229, 200, 27))
                    painter.setPen(pen)
                    painter.setBrush(brush)

            qx, qy = self._getqx(x), self._getqy(y)
            radius = w_seg * 3
            painter.drawEllipse(qx - radius, int(qy - radius * h_seg / w_seg), radius * 2, radius * 2)

        painter.end()

    def _linear(self, a, b, x):
        return a * x + b

    def _mouseReleaseEvent(self, e, canvas):
        # self.selectedPoint = None
        self.update()

    def _mouseMoveEvent(self, e, canvas):
        if self.selectedPoint is None:
            return

        self._calculateGeomertyProperties(canvas)
        mx, my = e.pos().x(), e.pos().y()
        x, y, color, qx, qy = self.selectedPoint

        distance = (qx - mx) ** 2 + (qy - my) ** 2
        if distance >= self.radius ** 2 / 2:

            offy = (my - self.zero_y) / self.ay - y
            new_y = y + offy
            new_y = 0 if new_y < 0 else 255 if new_y > 255 else new_y
            if self._movePoint(color, (x, y), (x, new_y)):
                self.selectedPoint = (x, y + offy, color, qx, self._getqy(new_y))
            else:
                self.selectedPoint = (x, y + offy, color, qx, y)

        self.update()

    def _calculateGeomertyProperties(self, canvas):
        w, h = canvas.width(), canvas.height()
        max_seg_num = self.max_seg_num
        seg_num = self.seg_num

        self.w_seg = w / max_seg_num
        self.h_seg = h / max_seg_num

        self.zero_x = self.w_seg * (seg_num - 3 + 10)
        self.zero_y = self.h_seg * (max_seg_num - seg_num - 10)
        self.max_x = self.w_seg * (max_seg_num - seg_num - 10)
        self.max_y = self.h_seg * (seg_num + 10)

        self.ax = (self.max_x - self.zero_x) / 255
        self.ay = (self.max_y - self.zero_y) / 255
        self.radius = self.w_seg * 3

    def _getqx(self, x):
        return int(self._linear(self.ax, self.zero_x, x))

    def _getqy(self, y):
        return int(self._linear(self.ay, self.zero_y, y))

    def _mousePressEvent(self, event, canvas):
        color = self._getColorByCanvas(canvas)
        self._calculateGeomertyProperties(canvas)

        mx, my = event.pos().x(), event.pos().y()
        touch = False
        for x, y in self._getSortedPoints(color):
            qx, qy = self._getqx(x), self._getqy(y)

            distance = (mx - qx) ** 2 + (my - qy) ** 2
            if distance <= self.radius ** 2:

                self.selectedPoint = (x, y, color, qx, qy)
                touch = True
        if not touch:
            self.selectedPoint = None

        self.update()

    def _doubleClickEvent(self, e, canvas):
        # add points to a color
        if self.selectedPoint is not None:
            return

        self._calculateGeomertyProperties(canvas)

        qmx, qmy = e.pos().x(), e.pos().y()
        mx = int((qmx - self.zero_x) / self.ax)
        if mx < 0 or mx > 255:
            return

        color = self._getColorByCanvas(canvas)
        map_dict = self._selectPointsDict(color)

        value = map_dict.get(mx, -1)
        if value > -1:
            return

        self.generateAllMapValues()
        value_func = self._getValueFuncByColor(color)
        color_y = value_func(mx)
        distance = (qmy - self._getqy(color_y)) ** 2
        if distance <= self.radius ** 2:
            self._addControlPoints([(mx, color_y)], color)
            # print("add point", (mx, color_y))

        self.update()

    def _getValueFuncByColor(self, color="r"):
        if color == "r":
            return self.r_func
        elif color == "g":
            return self.g_func
        elif color == "b":
            return self.b_func
        else:
            raise NotImplementedError("not a color")

    def r_func(self, v):
        return self.r_map_values[v]

    def g_func(self, v):
        return self.g_map_values[v]

    def b_func(self, v):
        return self.b_map_values[v]

    def colorAdjust(self, myIm: MyImage, mask=None):
        self.generateAllMapValues()
        result_im = myIm.colorAdjust([self.r_func, self.g_func, self.b_func], mask=mask)
        return result_im
