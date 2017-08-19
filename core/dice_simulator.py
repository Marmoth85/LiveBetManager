from PyQt5.QtWidgets import QWidget
# from PyQt5.QtCore import pyqtSlot

from gen_files import ui_dice_simulator


class DiceSimulator(QWidget, ui_dice_simulator.Ui_DiceSimulator):
    
    def __init__(self, parent=None):
        super(DiceSimulator, self).__init__(parent)
        self.setupUi(self)
