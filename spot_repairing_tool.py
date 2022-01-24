from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QBrush, QPainter, QPen, QColor, QResizeEvent
from PyQt5.QtCore import QPoint, QRect, Qt, QObject, pyqtSignal
import numpy as np
from numpy import ndarray
from IMPS import MyImage

# my modules
from utils import resource_path
from drawing_canvas import DrawingCanvas

# from hw2_playground import Playground, Point2D
ui_path = resource_path("./qtui/spotReparingTool.ui")
ui_class, window_class = uic.loadUiType(ui_path)


class SpotRepairingWidget(window_class):
    def __init__(self) -> None:
        super().__init__()

        self.ui = ui_class()
        self.ui.setupUi(self)

        self._setUpExtraWidgets()
        self._setUpUiEvent()

    def _setUpExtraWidgets(self):
        pass

    def _setUpUiEvent(self):
        pass

    def getSpotRadius(self):
        return self.ui.pen_size_slider.value()

    def repair(self, myIm: MyImage, mask: ndarray = None):
        """
        Args:
            imageArray: shape [w, h, c] 0~255
            repairMask: shape [w, h]    bool
        Retuens:
            repairedArray:  shape [w, h, c] 0~255
        """
        kernel_size = (self.ui.width_sb.value(), self.ui.height_sb.value())

        method = self.ui.selected_algo_cbox.currentText().lower()
        if method == "mean":
            return myIm.mean(kernel_size, mask=mask)
        elif method == "max":
            return myIm.max(kernel_size, mask=mask)
        elif method == "min":
            return myIm.min(kernel_size, mask=mask)
        elif method == "gaussianblur":
            return myIm.gaussianBlur(mean=0, std=1, kernel_size=kernel_size, mask=mask)
        elif method == "medium":
            return myIm.medium(kernel_size, mask=mask)
        elif method == "unsharp_mean":
            return myIm.unsharp(kernel_size, mask=mask, method="mean")
        elif method == "unsharp_gaussian":
            return myIm.unsharp(kernel_size, mask=mask, method="gaussian", gaussian_mean=0, gaussian_std=1)
        elif method == "histogram equalization":
            return myIm.histogramEqualization(mask=mask)
        elif method == "nothing":
            return myIm.copy()
        else:
            raise NotImplementedError("this method has not implemented")

        # image.
