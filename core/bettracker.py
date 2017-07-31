from PyQt5.QtWidgets import *

from gen_files import ui_bettracker


class BetTracker(QWidget, ui_bettracker.Ui_BetTracker):
    def __init__(self, parent=None):

        super(BetTracker, self).__init__(parent)
        self.setupUi(self)
