from PyQt5 import QtGui, QtWidgets
import sys

from gen_files import qmainwindow

class LiveBinaryBetManager(QtWidgets.QMainWindow, qmainwindow.Ui_MainWindow):

	def __init__(self, parent=None):
		super(LiveBinaryBetManager, self).__init__(parent)
		self.setupUi(self)
		
def main():
	app = QtWidgets.QApplication(sys.argv)
	form = LiveBinaryBetManager()
	form.show()
	app.exec_()
	
if __name__ == '__main__':
	main()