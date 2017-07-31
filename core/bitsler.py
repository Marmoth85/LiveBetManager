from PyQt5.QtWidgets import QWidget

from gen_files import ui_bitsler


class Bitsler(QWidget, ui_bitsler.Ui_Bitsler):
    def __init__(self, parent=None):

        super(Bitsler, self).__init__(parent)
        self.setupUi(self)
