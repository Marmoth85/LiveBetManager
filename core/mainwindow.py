from PyQt5 import QtWidgets

from gen_files import mainwindow

class MainWindow(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):

	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		self.setupUi(self)