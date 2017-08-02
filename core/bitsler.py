from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot

from math import log, ceil, pow, floor
import numpy as np

from gen_files import ui_bitsler


class Bitsler(QWidget, ui_bitsler.Ui_Bitsler):
    def __init__(self, parent=None):
        super(Bitsler, self).__init__(parent)
        self.setupUi(self)

        # Paramètres d'entrée au départ du pari
        self.cash = 0
        self.bet = 0
        self.proba_win = 0
        self.payout = 0
        self.black_risk = 0
        # Résultats et paramètres théoriques à calculer
        self.goal_black_risk = 0
        self.goal_lost_bet = 0
        self.goal_cash = 0
        self.goal_multiply = 0
        # Résultats et paramètres pratiques à utiliser en raison de la limitation due à la trésorerie actuelle
        self.practical_black_risk = 0
        self.practical_lost_bet = 0
        self.practical_cash = 0
        self.practical_multiply = 0

    def load_input_data(self):
        # Paramètres d'entrée au départ du pari
        self.cash = self.doubleSpinBox_Cash.value()
        self.bet = self.doubleSpinBox_Bet.value()
        self.proba_win = self.doubleSpinBox_Proba.value() / 100
        self.payout = self.doubleSpinBox_Payout.value()
        self.black_risk = self.spinBoxBlackRisk.value()

    def update_results(self):
        # Objectifs théoriques
        self.labelOutputBlackRiskGoal.setText(str(self.goal_black_risk))
        self.labelOutputLostBetGoal.setText(str(self.goal_lost_bet))
        self.labelOutputCashGoal.setText(str("%.8f" % self.goal_cash))
        self.labelOutputMultiplyGoal.setText(str("%.4f" % self.goal_multiply))

        # Empiriquement
        self.labelOutputPracticalRisk.setText(str(self.practical_black_risk))
        self.labelOutputPracticalLostBet.setText(str(self.practical_lost_bet))
        self.labelOutputPracticalCash.setText(str("%.8f" % self.practical_cash))
        self.labelOutputPracticalMultiply.setText(str("%.4f" % self.practical_multiply))

# Si problème avec la conversion des nombres float <-> str : float(machin.text().replace(",", "."))

    def compute_inequality(self, vector, way):
        """To be implemented
        val_condition = mul_vect ^ n_target * (1 - self.payout + self.payout / mul_vect) - 1"""
        val_condition = [0] * len(vector)

        n_target = 1
        if way == "goal":
            n_target = self.goal_lost_bet
        elif way == "practical":
            n_target = self.practical_lost_bet

        for i in range(len(vector)):
            val_condition[i] = pow(vector[i], n_target) * (1 - self.payout + self.payout / vector[i]) - 1

        return val_condition

    def find_minimal_coefficient_index(self, values):
        """To be implemented"""
        index = 0
        for i in range(len(values)):
            if values[i] <= 0:
                index = i
                break
        return index

    def dichotomy(self, precision):
        """To be implemented"""
        return precision + 1.2345678

    @pyqtSlot()
    def compute_parameters(self):
        self.load_input_data()

        # Série noire et nombre de coups perdants consécutifs
        proba_lose = 1 - self.proba_win
        n_bets_max_th = log(1.0/self.black_risk) / log(proba_lose)
        self.goal_lost_bet = ceil(n_bets_max_th)
        self.goal_black_risk = int(1 / pow(proba_lose, self.goal_lost_bet))

        # Calcul du coefficient multiplicateur minimal correspondant
        mul_vect = np.linspace(1.00001, ceil(1.0 / proba_lose) + 1, 100000 * (ceil(1.0 / proba_lose) + 1))
        val = self.compute_inequality(mul_vect, "goal")
        self.goal_multiply = mul_vect[self.find_minimal_coefficient_index(val)]

        # Calcul de la trésorerie nécessaire
        self.goal_cash = self.bet * (1 - pow(self.goal_multiply, self.goal_lost_bet)) / (1 - self.goal_multiply)

        # Contrainte = trésorerie actuelle souvent inférieure à celle qu'on souhaite pour tenter le coup
        self.practical_lost_bet = int(log(self.cash / self.bet * (self.goal_multiply - 1) + 1) / log(self.goal_multiply))
        self.practical_black_risk = int(1 / pow(proba_lose, self.practical_lost_bet))
        self.practical_cash = self.bet * (1 - pow(self.goal_multiply, self.practical_lost_bet)) / (1 - self.goal_multiply)
        self.practical_multiply = float(int(10000 * self.dichotomy(0.00001))) / 10000

        self.update_results()

    @pyqtSlot()
    def compute_bankruptcy(self):
        result = 0.012356

        self.labelOutputBankruptcyRisk.setText(str("%.2f" % (result * 100)).replace(".", ",") + "%")

    @pyqtSlot()
    def update_bankruptcy_display(self):
        self.labelOutputBankruptcyRisk.setText("-- Mettre à jour --")
