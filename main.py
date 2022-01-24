import os
from pathlib import Path
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QFileDialog, QWidget
from PyQt5.QtGui import QBrush, QPainter, QPen, QColor, QResizeEvent
from PyQt5.QtCore import QPoint, QRect, Qt, QObject, pyqtSignal
import typing
import sys
from color_adjust_tool import ColorAdjustWidget

# my modules
from utils import resource_path
from drawing_canvas import DrawingCanvas
from spot_repairing_tool import SpotRepairingWidget

# from hw2_playground import Playground, Point2D
main_ui_path = resource_path("./qtui/main.ui")
main_ui_class, main_window_class = uic.loadUiType(main_ui_path)


class MyMainWindow(main_window_class):
    def __init__(self, main_ui_class) -> None:
        super().__init__()
        self.is_using_thread = False
        self.is_auto_predict = False
        self.auto_run_thread = None

        self.main_ui = main_ui_class()
        self.main_ui.setupUi(self)

        self._setUpExtraWidgets()
        self._setUpUiEvent()

    def _agentPredictAction(self):
        return self.playground_agent.get_action(self.drawingCanvas.state)

    def _setUpExtraWidgets(self):

        # tool frame widget
        self.spotRepaingTool = SpotRepairingWidget()
        self.colorAdjustTool = ColorAdjustWidget()

        self.canvas = DrawingCanvas(self.spotRepaingTool, self.colorAdjustTool)
        self.main_ui.main_canvas_holder.addWidget(self.canvas.c)

    def _setUpUiEvent(self):

        # change tool btns
        self.main_ui.spot_repairing_btn.clicked.connect(lambda: self.selectTool("斑點修補", self.spotRepaingTool))
        self.main_ui.color_adjust_btn.clicked.connect(lambda: self.selectTool("顏色調整", self.colorAdjustTool))

        self.main_ui.read_image_btn.clicked.connect(self.readImage)
        self.main_ui.save_image_btn.clicked.connect(self.saveImage)

        # self.canvas.eventHandler.onMouseReleaseEvent.connect()

    def QselectFileDialog(self):
        fname = QFileDialog.getOpenFileName(self, "選擇資料庫檔案", os.getcwd(), "Image files (*.jpg *.jpeg *.png *.bmp)")
        if len(fname[0]) == 0:
            return

        filepath = Path(fname[0])
        if filepath.exists():
            return filepath
        else:
            print("file not exist")

    def QsaveFileDialog(self):
        fname = QFileDialog.getSaveFileName(
            self, "選擇資料夾並命名", os.getcwd(), "Image files (*.jpg *.jpeg);;點陣圖(*.bmp);;PNG (*.png)"
        )

        if len(fname[0]) == 0:
            return None

        filepath = Path(fname[0])

        return str(filepath)

    def saveImage(self):
        if not self.canvas.hasImage():
            return

        fname = self.QsaveFileDialog()
        if fname is not None:
            self.canvas.getCurrentIm().save(fname)

    def readImage(self):
        filepath = self.QselectFileDialog()
        if filepath is not None:
            self.canvas.readImage(str(filepath))

    def selectTool(self, toolName, toolFrameWidget):
        # print(self.main_ui.current_tool_vl.count())

        if self.main_ui.current_tool_vl.count() == 3:
            widget = self.main_ui.current_tool_vl.itemAt(1).widget()
            if widget is not None:
                widget.setParent(None)

        self.main_ui.selected_tool_lb.setText(toolName)
        self.main_ui.current_tool_vl.insertWidget(1, toolFrameWidget)


class MyHw2App(QApplication):
    def __init__(self, argv: typing.List[str]) -> None:
        super().__init__(argv)

        # create ui and window obj after app created
        self.main_window = MyMainWindow(main_ui_class)
        # self.main_window.setDevicePixelRatio(self.devicePixelRatio())
        # self.main_window.canvas.c.setDevicePixelRatio(self.devicePixelRatio())

    def start(self):
        self.main_window.show()
        self.exec()


def main():

    app = MyHw2App(sys.argv)
    app.start()


if __name__ == "__main__":
    main()
