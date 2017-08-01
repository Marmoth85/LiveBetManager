from PyQt5 import QtWidgets

import sys

from core import mainwindow


class LiveBetManager(mainwindow.MainWindow):
    def __init__(self):
        super(LiveBetManager, self).__init__()


def main():
    app = QtWidgets.QApplication(sys.argv)
    form = LiveBetManager()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
