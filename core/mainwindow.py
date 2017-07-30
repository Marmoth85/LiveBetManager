import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from gen_files import ui_mainwindow

class MainWindow(QMainWindow, ui_mainwindow.Ui_MainWindow):
			
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		self.setupUi(self)
			
	@pyqtSlot(QAction)	
	def proceedAction(self, action):
		# sender = self.sender()
		if(action == self.actionShowEvents):
			self.showOpenEvents()
		# print(sender)
		# print(action.text())
	
	def showOpenEvents(self):
		QMessageBox.question(self, "Titre", "Message : Le menu a bien été cliqué, mais la fonction n'est pas encore implémentée", QMessageBox.Ok, QMessageBox.Ok)