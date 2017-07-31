from PyQt5.QtWidgets import QMainWindow, QMessageBox, QAction
from PyQt5.QtCore import *

from gen_files import ui_mainwindow
from . import bettracker


class MainWindow(QMainWindow, ui_mainwindow.Ui_MainWindow):

    my_bet_tracker = 0

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

    @pyqtSlot(QAction)
    def proceed_action(self, action):
        # sender = self.sender()
        if action == self.actionShowEvents:
            self.show_open_events()
            # print(sender)
            # print(action.text())

    def show_open_events(self):
        QMessageBox.question(self, "Titre",
                             "Message : Le menu a bien été cliqué, mais la fonction n'est pas encore implémentée",
                             QMessageBox.Ok, QMessageBox.Ok)
        my_bet_tracker = bettracker.BetTracker(self)
        self.setCentralWidget(my_bet_tracker)
