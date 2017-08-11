from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot

from math import log, ceil, pow, factorial
import numpy as np
import sys

from gen_files import ui_bitsler

sys.setrecursionlimit(20000)

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
        self.practical_cash_optimal = 0
        self.practical_multiply_min = 0
        self.practical_multiply_max = 0
        self.blocked_bets = 0
    
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
        self.labelOutputPracticalCash.setText(str("%.8f" % self.practical_cash) + str(" - %.8f" % self.practical_cash_optimal))
        self.labelOutputPracticalMultiply.setText(str("%.4f" % self.practical_multiply_min) + str(" - %.4f" % self.practical_multiply_max))
        self.spinBoxBlockNumberBet.setValue(self.blocked_bets)

    def compute_inequality(self, vector, method):
        val_condition = [0.] * len(vector)
        # lost_bet = 1
        if method == "theoretical":
            lost_bet = self.goal_lost_bet
        else:
            lost_bet = self.practical_lost_bet
        for i in range(len(vector)):
            if vector[i] != 1:
                val_condition[i] = pow(vector[i], lost_bet) * (1 - self.payout + self.payout / vector[i]) - 1
                if val_condition[i] < -1e10:
                    val_condition[i+1:] = [-1e+11] * (len(vector) - i)
                    break
            else:
                val_condition[i] = 1

        return val_condition
    
    def find_minimal_coefficient_index(self, values):
        index = 0
        for i in range(len(values)):
            if values[i] <= 0:
                index = i
                break
        return index
        
    def dichotomy(self, precision, method):
        number_bet = 0
        iteration = 0
        borne_inf = 1
        borne_sup = 1.0 / pow((1 - self.proba_win), 5)
        multiply_test = 1
        if method == "lost bets max":
            number_bet = self.practical_lost_bet
        elif method == "fixated lost bets":
            number_bet = self.blocked_bets
        while iteration <= 1000000 and borne_sup - borne_inf > precision:
            iteration += 1
            multiply_test = (borne_inf + borne_sup) / 2.0
            cash = self.bet * (1 - pow(multiply_test, number_bet)) / (1 - multiply_test)
            if cash < self.cash:
                borne_inf = multiply_test
                value = self.bet * (1 - pow(borne_sup, number_bet)) / (1 - borne_sup)
                if value < self.cash:
                    borne_sup *= 1.1
            else:
                borne_sup = multiply_test
        return multiply_test
    
    @pyqtSlot()
    def compute_parameters(self):
        self.load_input_data()
        
        # Série noire et nombre de coups perdants consécutifs
        proba_lose = 1 - self.proba_win
        n_bets_max_th = log(1.0 / self.black_risk) / log(proba_lose)
        self.goal_lost_bet = ceil(n_bets_max_th)
        self.goal_black_risk = int(1 / pow(proba_lose, self.goal_lost_bet))
        
        # Calcul du coefficient multiplicateur minimal correspondant
        mul_vector = np.linspace(1, 1.0 / pow(proba_lose, 5), 100 * int(1.0 / pow(proba_lose, 5)) + 1)
        val = self.compute_inequality(mul_vector, "theoretical")
        self.goal_multiply = mul_vector[self.find_minimal_coefficient_index(val)]

        # Calcul de la trésorerie nécessaire
        self.goal_cash = self.bet * (1 - pow(self.goal_multiply, self.goal_lost_bet)) / (1 - self.goal_multiply)
        self.goal_cash = ceil(100000000 * self.goal_cash)/100000000

        # Contrainte = trésorerie actuelle souvent inférieure à celle qu'on souhaite pour tenter le coup
        self.practical_lost_bet = int(log(self.cash / self.bet * (self.goal_multiply - 1) + 1) / log(self.goal_multiply))
        self.practical_black_risk = int(1 / pow(proba_lose, self.practical_lost_bet))

        val2 = self.compute_inequality(mul_vector, "practical")
        self.practical_multiply_min = mul_vector[self.find_minimal_coefficient_index(val2)]

        self.practical_cash = self.bet * (1 - pow(self.practical_multiply_min, self.practical_lost_bet)) / (1 - self.practical_multiply_min)
        self.practical_cash = ceil(100000000 * self.practical_cash) / 100000000
        self.practical_multiply_max = float(int(10000 * self.dichotomy(0.00001, "lost bets max"))) / 10000
        self.practical_cash_optimal = self.bet * (1 - pow(self.practical_multiply_max, self.practical_lost_bet)) / (1 - self.practical_multiply_max)
        self.practical_cash_optimal = ceil(100000000 * self.practical_cash_optimal) / 100000000
        self.blocked_bets = self.practical_lost_bet

        self.update_results()
    
    @pyqtSlot()
    def compute_bankruptcy(self):

        num_coins = self.spinBoxDiceNumber.value()
        min_heads = self.blocked_bets
        head_prob = 1 - self.proba_win

        memo = [0.] * (num_coins + 1)

        for i in range(min_heads, num_coins + 1, 1):
            result = pow(head_prob, min_heads)
            for first_tail in range(1, min_heads + 1, 1):
                pr = memo[i - first_tail]
                result += pow(head_prob, first_tail - 1) * (1 - head_prob) * pr
            memo[i] = result

        self.labelOutputBankruptcyRisk.setText(str("%.2f" % (memo[num_coins] * 100)).replace(".", ",") + "%")
    
    @pyqtSlot()
    def update_bankruptcy_display(self):
        self.labelOutputBankruptcyRisk.setText("-- Mettre à jour --")

    @pyqtSlot()
    def maximize_increase_on_loss(self):
        value = self.dichotomy(0.00001, "fixated lost bets")
        self.labelIncreaseOnlossMAX.setText(str("%.4f" % value))

    @pyqtSlot()
    def update_n_break(self):
        self.blocked_bets = self.spinBoxBlockNumberBet.value()
        self.labelIncreaseOnlossMAX.setText("-- Mettre à jour --")

    def probOfStreak(self, numCoins, minHeads, headprob):
        memo = [0.] * (numCoins + 1)

        for i in range(minHeads, numCoins + 1, 1):
            result = pow(headprob, minHeads)
            for first_tail in range(1, minHeads + 1, 1):
                pr = memo[i - first_tail]
                result += pow(headprob, first_tail - 1) * (1 - headprob) * pr
            memo[i] = result
        print(memo)

        return memo[numCoins]
