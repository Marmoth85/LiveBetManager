from PyQt5.QtWidgets import QMainWindow, QMessageBox, QAction
from PyQt5.QtCore import pyqtSlot

from gen_files import ui_mainwindow
from . import bettracker, dice_calculator, dice_simulator


class MainWindow(QMainWindow, ui_mainwindow.Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.my_bet_tracker = 0
        self.my_gambling_calculator = 0
        self.my_gambling_simulator = 0

    @pyqtSlot(QAction)
    def proceed_action(self, action):
        if action == self.actionShowEvents:
            self.show_open_events()
        elif action == self.actionCalculator:
            self.save_current_work()
            self.show_gambling_calculator()
        elif action == self.actionSimulator:
            self.save_current_work()
            self.show_gambling_simulator()
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

    def show_gambling_calculator(self):
        self.my_gambling_calculator = dice_calculator.DiceCalculator(self)
        self.setCentralWidget(self.my_gambling_calculator)
        
    def show_gambling_simulator(self):
        self.my_gambling_simulator = dice_simulator.DiceSimulator(self)
        self.setCentralWidget(self.my_gambling_simulator)
