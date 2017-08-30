from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import pyqtSlot

import numpy as np

from gen_files import ui_dice_simulator
from . import gambling


class DiceSimulator(QWidget, gambling.Gambling, ui_dice_simulator.Ui_DiceSimulator):
    
    def __init__(self, parent=None):
        
        print("DiceSimulator : On entre dans le constructeur")
        super(DiceSimulator, self).__init__(parent)
        self.setupUi(self)

        self._number_simulation = 0
        
        self._result_failed_method = 0
        self._result_global_win = 0.
        self._result_global_loss = 0.
        self._result_global = 0.
        self._result_mean_lost_bets_in_row = 0.
        
        self.currency_changed("Bitcoin")
        self.precision_changed()
        print("DiceSimulator : On sort du le constructeur")
    
    @pyqtSlot('QString')
    def currency_changed(self, string):
        """Ce SLOT est activé lorsque l'utilisateur change de monnaie dans le combobox.
        Il s'agit alors d'ajuster la précision des double_spin_box de la trésorerie et des paris, de façon à ce que les
        incréments correspondent à la "force" des monnaies choisies"""
        
        print("DiceSimulator: On entre dans le SLOT currency_changed")

        self._currency = string
        self.update_cash_precision()
        self.spinBox_precision_input_cash.setValue(self._cash_precision_spinbox)
        self.update_bet_precision()
        self.spinBox_precision_input_bet.setValue(self._bet_precision_spinbox)
        
        print("DiceSimulator: On sort du SLOT currency_changed")
    
    @pyqtSlot()
    @pyqtSlot(int)
    def precision_changed(self):
        """Ce SLOT est déclenché lorsque l'un des spinBox de précision est modifié. Il sert à modifier les incréments
        par défaut des spinbox d'entrée, de façon à pouvoir cliquer sur up et down un nombre restreint de fois."""
        
        print("DiceSimulator: On entre dans le SLOT precision_changed")

        self.doubleSpinBox_input_cash.setSingleStep(10 ** self.spinBox_precision_input_cash.value())
        self.doubleSpinBox_input_bet.setSingleStep(10 ** self.spinBox_precision_input_bet.value())
        self.doubleSpinBox_input_proba_event.setSingleStep(10 ** self.spinBox_precision_input_proba_event.value())
        self.doubleSpinBox_input_payout.setSingleStep(10 ** self.spinBox_precision_input_payout.value())
        self.doubleSpinBox_win_bet.setSingleStep(10 ** self.spinBox_precision_win_bet.value())
        self.doubleSpinBox_lose_bet.setSingleStep(10 ** self.spinBox_precision_lose_bet.value())
        self.spinBox_input_dice_number.setSingleStep(10 ** self.spinBox_precision_input_dice_number.value())
        self.spinBox_simulation.setSingleStep(10 ** self.spinBox_precision_simulation.value())
        
        print("DiceSimulator: On sort du SLOT precision_changed")
    
    @pyqtSlot()
    def compute_expectation(self):
        """Cette méthode est un SLOT déclenché par le bouton "Calculer".
        On calcule les paramètres théoriques souhaités ainsi que ceux, pragmatiques, quand la trésorerie réelle ne
        correspond pas à ce que nous voudrions sur un plan purement théorique."""
        
        print("DiceSimulator: On entre dans le SLOT compute_expectation")

        self.load_input_data()
        
        if self.check_inputs():
            
            dice_list = self.create_dice_list()
            win_lost_dice = self.compute_win_lost_list(dice_list)
            self.calculate_mean_lost_in_row(win_lost_dice)
            self.compute_strategy(win_lost_dice)
            
            self.update_result_data()
        
        print("DiceSimulator: On sort du SLOT compute_expectation")
        
    @pyqtSlot()
    def bet_clicked(self):
        """Ce SLOT est déclenché par un des radioButton liés à la stratégie des mises lors de paris gagnés ou perdus.
        Ici, on s'assure qu'un seul radioButton ne peut être activé pour un pari gagnant et pour un pari perdant."""

        print("DiceSimulator: On entre dans le SLOT bet_clicked")
        
        def switch_button_state(button_1, button_2):
            if button_1.isChecked():
                button_2.setChecked(False)
            else:
                button_2.setChecked(True)
                
        sender = self.sender()
        
        if sender == self.radioButton_win_bet_base:
            switch_button_state(self.radioButton_win_bet_base, self.radioButton_win_modify_bet)
        elif sender == self.radioButton_win_modify_bet:
            switch_button_state(self.radioButton_win_modify_bet, self.radioButton_win_bet_base)
        elif sender == self.radioButton_lose_bet_base:
            switch_button_state(self.radioButton_lose_bet_base, self.radioButton_lose_modify_bet)
        elif sender == self.radioButton_lose_modify_bet:
            switch_button_state(self.radioButton_lose_modify_bet, self.radioButton_lose_bet_base)
        
        print("DiceSimulator: On sort du SLOT bet_clicked")
    
    def load_input_data(self):
        """Cette méthode récupère les informations depuis l'IHM pour les stocker dans les attributs d'objets,
                afin de pouvoir les exploiter facilement dans les calculs qui suivront."""

        print("DiceSimulator: On entre dans le SLOT load_input_data")
        
        self._cash = self.doubleSpinBox_input_cash.value()
        self._bet = self.doubleSpinBox_input_bet.value()
        self._event_probability = self.doubleSpinBox_input_proba_event.value() / 100
        self._payout = self.doubleSpinBox_input_payout.value()
        self._wished_dices = self.spinBox_input_dice_number.value()
        self._number_simulation = self.spinBox_simulation.value()
        self._increase_decrease_on_loss = "base"
        self._increase_decrease_on_win = "base"
        
        if self.radioButton_lose_modify_bet.isChecked():
            self._increase_decrease_on_loss = 1 + self.doubleSpinBox_lose_bet.value() / 100
        
        if self.radioButton_win_modify_bet.isChecked():
            self._increase_decrease_on_win = 1 + self.doubleSpinBox_win_bet.value() / 100

        print("DiceSimulator: On sort du SLOT load_input_data")

    def update_result_data(self):
        """Cette méthode récupère les résultats des calculs effectués pour les afficher dans l'IHM"""

        print("DiceSimulator: On entre dans le SLOT update_result_data")
        
        lose_part = 100 * (self._result_failed_method / self._number_simulation)
        win_part = 100 - lose_part
        self.label_output_lost_strategies.setText(str("%.2f") % lose_part + " %")
        self.label_output_won_strategies.setText(str("%.2f") % win_part + " %")

        won_strategies = self._number_simulation - self._result_failed_method
        
        if won_strategies != 0:
            mean_per_won = self._result_global_win / won_strategies
            self.label_output_benefits_win.setText(str("%.8f") % mean_per_won)
            self.label_output_relative_benefits.setText(str("%.2f") %
                                                        (lambda x: 100 * x / self._cash)(mean_per_won) + " %")
        else:
            self.label_output_benefits_win.setText(str("NA"))
            self.label_output_relative_benefits.setText(str("NA"))
            
        if self._result_failed_method != 0:
            mean_per_loss = self._result_global_loss / self._result_failed_method
            self.label_output_deficits_lose.setText(str("%.8f") % mean_per_loss)
            self.label_output_relative_deficits.setText(str("%.2f") %
                                                        (lambda x: 100 * x / self._cash)(mean_per_loss) + " %")
        else:
            self.label_output_deficits_lose.setText(str("NA"))
            self.label_output_relative_deficits.setText(str("NA"))
        
        global_result = self._result_global_win - self._result_global_loss
        self.label_output_global_result.setText(str("%.8f") % global_result)
        self.label_output_relative_global_result.setText(str("%.2f") %
                                                         (lambda x: 100 * x / self._cash)(global_result) + " %")
        
        self.label_output_mean_streak.setText(str("%.2f") % self._result_mean_lost_bets_in_row)
        
        print("DiceSimulator: On sort du SLOT update_result_data")

    def check_inputs(self):
        """Cette méthode a pour objet de vérifier que les inputs soient cohérents.
                Aucun calcul ne doit être lancé sans être assuré de la bonne forme des paramètres d'entrée"""

        print("DiceSimulator: On entre dans le SLOT check_inputs")

        message = ""
        test = True
        if self._cash == 0:
            message += "La trésorerie ne peut pas être nulle pour pouvoir jouer...\n"
            test = False
        if self._bet == 0 or self._bet > self._cash:
            message += "Le montant du pari ne peut ni être nul, ni supérieur à la trésorerie disponible...\n"
            test = False
        if self._wished_dices == 0:
            message += "Le nombre de dés à jouer ne peut pas être égal à zéro...\n"
            test = False
        if self._number_simulation == 0:
            message += "Le nombre de simulations à effectuer ne peut pas être nul... \n"
            test = False
        if self._payout <= 1:
            message += "Le payout ne peut pas être inférieur ou égal à un... \n"
            test = False
        if not test:
            QMessageBox.critical(self, "Erreur dans les paramètres saisis!", message)
        
        print("DiceSimulator: On sort du SLOT check_inputs")
        return test

    def create_dice_list(self):
        """
        Cette méthode crée une liste contenant les N tirages correspondant au test de la stratégie que l'on met en place.
        N dépend du nombre de simulation et du nombre de dés par simulations (produit des deux).
        :return: une liste contenant les valeurs des dés N simulés.
        """
        
        print("DiceSimulator : create_dice_list IN")
        dices = np.random.randint(0, 10000, int(self._number_simulation * self._wished_dices * 1.1))
        print("DiceSimulator : create_dice_list OUT")
        return dices
    
    def compute_win_lost_list(self, dice_list):
        return []
    
    def calculate_mean_lost_in_row(self, dice_list):
        pass
    
    def compute_strategy(self, dice_list):
        pass
