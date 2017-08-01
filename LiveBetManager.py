from PyQt5 import QtWidgets

import sys

from core import mainwindow


class LiveBinaryBetManager(mainwindow.MainWindow):
    def __init__(self):
        super(LiveBinaryBetManager, self).__init__()


def main():
    app = QtWidgets.QApplication(sys.argv)
    form = LiveBinaryBetManager()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
