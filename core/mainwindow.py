from PyQt5.QtWidgets import QMainWindow, QMessageBox, QAction
from PyQt5.QtCore import pyqtSlot

from gen_files import ui_mainwindow
from . import bettracker, bitsler


class MainWindow(QMainWindow, ui_mainwindow.Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.my_bet_tracker = 0
        self.my_bitsler_spreadsheet = 0

    @pyqtSlot(QAction)
    def proceed_action(self, action):
        if action == self.actionShowEvents:
            self.show_open_events()
        elif action == self.actionOuvrir_Feuille_de_calcul:
            self.save_current_work()
            self.show_bitsler_spreadsheet()
        elif action == self.actionQuitter:
            self.save_current_work()
            self.close()

    def show_open_events(self):
        self.my_bet_tracker = bettracker.BetTracker(self)
        self.setCentralWidget(self.my_bet_tracker)

    def save_current_work(self):
        """QMessageBox.question(self, "Save Current Work",
                             "Message : La fonctionnalité est prévue mais n'a pas encore implémentée!",
                             QMessageBox.Ok, QMessageBox.Ok)"""
        pass

    def show_bitsler_spreadsheet(self):
        self.my_bitsler_spreadsheet = bitsler.Bitsler(self)
        self.setCentralWidget(self.my_bitsler_spreadsheet)
