from PyQt5 import QtGui, QtWidgets
import sys

from gen_files import welcomeview

class LiveBinaryBetManager(QtWidgets.QMainWindow, welcomeview.Ui_WelcomeView):

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