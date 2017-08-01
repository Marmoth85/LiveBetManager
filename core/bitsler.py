from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot

from gen_files import ui_bitsler


class Bitsler(QWidget, ui_bitsler.Ui_Bitsler):
    def __init__(self, parent=None):

        super(Bitsler, self).__init__(parent)
        self.setupUi(self)

    @pyqtSlot()
    def update_calculation(self):
        pass

    @pyqtSlot()
    def calculate_bankruptcy(self):
        pass

    @pyqtSlot()
    def update_bankruptcy_display(self):
        pass