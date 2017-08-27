from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import pyqtSlot

from math import log, ceil, floor
import numpy as np

from gen_files import ui_dice_calculator
from . import gambling


class DiceCalculator(QWidget, gambling.Gambling, ui_dice_calculator.Ui_DiceCalculator):

    def __init__(self, parent=None):
        """Constructeur du DiceCalculator: cette classe hérite de Gambling (qui rassemble tous les inputs).
        On récupère l'initiation des attributs de Gambling et on initialise les attributs spécifiques à cette classe.
        Enfin, on dessine le widget à l'aide de la classe créée par pyuic5: Ui_DiceCalculator."""
        
        super(DiceCalculator, self).__init__(parent)
        self.setupUi(self)
        
        # Définition des attributs spécifiques à la classe DiceCalculator
        self._choosen_method = ""
        self._computed_lost_bet, self._computed_lost_bet_opt = 0, 0
        self._computed_risk_serie, self._computed_risk_serie_opt = 0., 0.
        self._minimal_increase_bet, self._minimal_increase_bet_opt = 0., 0.
        self._maximal_increase_bet, self._maximal_increase_bet_opt = 0., 0.
        self._minimal_cash, self._minimal_cash_opt = 0., 0.
        self._maximal_cash, self._maximal_cash_opt = 0., 0.
        self._streak_probability, self._streak_probability_opt = 0., 0.
        
        self.currency_changed("Bitcoin")
        self.precision_changed()
        
    def load_input_data(self):
        """Cette méthode récupère les informations depuis l'IHM pour les stocker dans les attributs d'objets,
        afin de pouvoir les exploiter facilement dans les calculs qui suivront."""
        
        print("DEBUG : on entre dans DiceCalculator::load_input_data()")
        self._cash = self.doubleSpinBox_input_cash.value()
        self._bet = self.doubleSpinBox_input_bet.value()
        self._event_probability = self.doubleSpinBox_input_proba_event.value() / 100
        self._payout = self.doubleSpinBox_input_payout.value()
        self._wished_dices = self.spinBox_input_dice_number.value()
        self._probability_in_row = (lambda x: 1 / x if x != 0 else 0.0)(self.spinBox_risk_serie.value())
        self._black_in_row = self.spinBox_streak_serie.value()
        self._increase_decrease_on_loss = 1 + self.doubleSpinBox_increase_bet.value() / 100
        self._bankruptcy_probability = self.doubleSpinBox_bankruptcy_probability.value() / 100
        
        if self.radioButton_risk_serie.isChecked():
            self._choosen_method = "Risque de la série négative"
        elif self.radioButton_streak_serie.isChecked():
            self._choosen_method = "Nombre de paris perdus à la suite"
        elif self.radioButton_increase_bet.isChecked():
            self._choosen_method = "Augmentation des mises en cas de pari perdu"
        elif self.radioButton_bankruptcy_probability.isChecked():
            self._choosen_method = "Probabilité maximale de l'échec de la martingale"
        print("DEBUG : on sort de DiceCalculator::load_input_data()")

    def update_result_data(self):
        """Cette méthode récupère les résultats des calculs effectués pour les afficher dans l'IHM"""
        
        print("DEBUG : on entre dans DiceCalculator::update_result_data()")
        self.label_output_choosen_method.setText(self._choosen_method)
        self.label_output_lost_bet.setText(str(self._computed_lost_bet))
        self.label_output_risk_serie.setText(str((lambda x: int(1 / x) if x != 0 else 0.0)(self._computed_risk_serie)))
        self.label_output_minimal_increase_bet.setText(str("%.2f" % (lambda x: (x - 1) * 100
                                                                     )(self._minimal_increase_bet) + " %"))
        self.label_output_maximal_increase_bet.setText(str("%.2f" % (lambda x: (x - 1) * 100
                                                                     )(self._maximal_increase_bet) + " %"))
        self.label_output_minimal_cash.setText(str("%.8f" % self._minimal_cash))
        self.label_output_maximal_cash.setText(str("%.8f" % self._maximal_cash))
        self.label_output_streak_probability.setText(str("%.2f" % (lambda x: 100 * x)(self._streak_probability) + " %"))
        
        self.label_output_lost_bet_opt.setText(str(self._computed_lost_bet_opt))
        self.label_output_risk_serie_opt.setText(str((lambda x: int(1 / x) if x != 0 else 0.0
                                                      )(self._computed_risk_serie_opt)))
        self.label_output_minimal_increase_bet_opt.setText(str("%.2f" % (lambda x: (x - 1) * 100
                                                                         )(self._minimal_increase_bet_opt) + " %"))
        self.label_output_maximal_increase_bet_opt.setText(str("%.2f" % (lambda x: (x - 1) * 100
                                                                         )(self._maximal_increase_bet_opt) + " %"))
        self.label_output_minimal_cash_opt.setText(str("%.8f" % self._minimal_cash_opt))
        self.label_output_maximal_cash_opt.setText(str("%.8f" % self._maximal_cash_opt))
        self.label_output_streak_probability_opt.setText(str("%.2f" % (lambda x: 100 * x
                                                                       )(self._streak_probability_opt) + " %"))
        print("DEBUG : on sort de DiceCalculator::update_result_data()")

    def check_inputs(self):
        """Cette méthode a pour objet de vérifier que les inputs soient cohérents.
        Aucun calcul ne doit être lancé sans être assuré de la bonne forme des paramètres d'entrée"""

        print("DEBUG : on entre dans DiceCalculator::check_inputs()")
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
        if self._choosen_method == "":
            message += "Avant de lancer les calculs, il vous faut choisir une des quatre méthodes proposées...\n"
            test = False
        if self._choosen_method == "Risque de la série négative" and self._probability_in_row == 0:
            message += "Le risque de la série négative est incorrect (division par zéro...)\n"
            test = False
        if self._choosen_method == "Nombre de paris perdus à la suite" and self._black_in_row <= 1:
            message += "La martingale géométrique ne peut être calculée que pour des séries " \
                       "de deux paris perdants ou plus...\n"
            test = False
        if self._choosen_method == "Augmentation des mises en cas de pari perdu" and \
                        self._increase_decrease_on_loss <= 1:
            message += "La valeur saisie dans l'augmentation des mises n'est pas cohérente avec la mise en place " \
                       "d'une martingale géométrique...\n"
            test = False
        if self._choosen_method == "Probabilité maximale de l'échec de la martingale":
            if self._bankruptcy_probability == 0:
                message += "La probabilité de l'échec de la stratégie ne peut pas être nulle...\n"
                test = False
            if self._bankruptcy_probability == 1:
                message += "Choisir une probabilité d'échec de la stratégie égale à 1 est définitivement stupide...\n"
                test = False
        if not test:
            self.display_input_error_message(message)
        print("DEBUG : on sort de DiceCalculator::check_inputs()")
        return test
        
    @pyqtSlot('QString')
    def currency_changed(self, string):
        """Ce SLOT est activé lorsque l'utilisateur change de monnaie dans le combobox.
        Il s'agit alors d'ajuster la précision des double_spin_box de la trésorerie et des paris, de façon à ce que les
        incréments correspondent à la "force" des monnaies choisies"""
        
        print("DEBUG : on entre dans le SLOT currency_changed")
        self._currency = string
        # Mise à jour de la précision du spinbox de la trésorerie
        self.update_cash_precision()
        self.spinBox_precision_input_cash.setValue(self._cash_precision_spinbox)
        # signal valueChanged est déclenché et le slot precision_changed se charge des modification sur les spinboxes.
        self.update_bet_precision()
        self.spinBox_precision_input_bet.setValue(self._bet_precision_spinbox)
        # signal valueChanged est déclenché et le slot precision_changed se charge des modification sur les spinboxes.
        print("DEBUG : on sort du SLOT currency_changed")

    @pyqtSlot()
    def precision_changed(self):
        """Ce SLOT est déclenché lorsque l'un des spinBox de précision est modifié. Il sert à modifier les incréments
        par défaut des spinbox d'entrée, de façon à pouvoir cliquer sur up et down un nombre restreint de fois."""
        
        print("DEBUG : On entre dans le SLOT DiceCalculator::precision_changed()")
        self.doubleSpinBox_input_cash.setSingleStep(10 ** self.spinBox_precision_input_cash.value())
        self.doubleSpinBox_input_bet.setSingleStep(10 ** self.spinBox_precision_input_bet.value())
        self.doubleSpinBox_input_proba_event.setSingleStep(10 ** self.spinBox_precision_input_proba_event.value())
        self.doubleSpinBox_input_payout.setSingleStep(10 ** self.spinBox_precision_input_payout.value())
        self.spinBox_input_dice_number.setSingleStep(10 ** self.spinBox_precision_input_dice_number.value())
        self.spinBox_risk_serie.setSingleStep(10 ** self.spinBox_precision_risk_serie.value())
        self.spinBox_streak_serie.setSingleStep(10 ** self.spinBox_precision_streak_serie.value())
        self.doubleSpinBox_increase_bet.setSingleStep(10 ** self.spinBox_precision_increase_bet.value())
        self.doubleSpinBox_bankruptcy_probability.setSingleStep(10 **
                                                                self.spinBox_precision_bankruptcy_probability.value())
        print("DEBUG : On sort du SLOT DiceCalculator::precision_changed()")
        
    @pyqtSlot()
    def compute_expectation(self):
        """Cette méthode est un SLOT déclenché par le bouton "Calculer".
        On calcule les paramètres théoriques souhaités ainsi que ceux, pragmatiques, quand la trésorerie réelle ne
        correspond pas à ce que nous voudrions sur un plan purement théorique."""

        print("DEBUG : on entre dans le SLOT DiceCalculator::compute_expectation()")
        self.load_input_data()

        if self.check_inputs():
            # Tester le choix de la méthode
            if self._choosen_method == "Risque de la série négative":
                self.compute_risk_serie_method()
            elif self._choosen_method == "Nombre de paris perdus à la suite":
                self.compute_streak_serie_method()
            elif self._choosen_method == "Augmentation des mises en cas de pari perdu":
                self.compute_increase_bet_method()
            elif self._choosen_method == "Probabilité maximale de l'échec de la martingale":
                self.compute_bankruptcy_risk_method()
            self.compute_cash_method()
            self.update_result_data()
        print("DEBUG : on sort du SLOT DiceCalculator::compute_expectation()")

    def display_input_error_message(self, message):
        print("DEBUG : on entre dans DiceCalculator::display_input_error_message()")
        QMessageBox.critical(self, "Erreur dans les paramètres d'entrée", message)
        print("DEBUG : on sort de DiceCalculator::display_input_error_message()")

    def compute_risk_serie_method(self):
        """Cette méthode lance les calculs basés sur notre stratégie fournie en entrée à partir du nombre de paris
        perdus consécutifs, nombre calculé à partir de la probabilité des N paris perdus consécutifs, fournie par
        l'utilisateur."""
    
        print("DEBUG : On entre dans la méthode DiceCalculator::compute_risk_serie_method")
        # Calculer le N_Streak
        self._computed_lost_bet = 1 + int(log(self._probability_in_row) / log(1 - self._event_probability))
        # On lance les calculs à partir du N_Streak
        self.compute_everything_from_streak_number()
        print("DEBUG : On sort de la méthode DiceCalculator::compute_risk_serie_method")
        
    def compute_streak_serie_method(self):
        """Cette méthode lance les calculs basés sur notre stratégie fournie en entrée à partir du nombre de paris
        perdus consécutifs, nombre fourni par l'utilisateur."""
        
        print("DEBUG : On entre dans la méthode DiceCalculator::compute_streak_serie_method")
        self._computed_lost_bet = self._black_in_row
        self.compute_everything_from_streak_number()
        print("DEBUG : On sort de la méthode DiceCalculator::compute_streak_serie_method")
    
    def compute_increase_bet_method(self):
        """Cette méthode lance les calculs basés sur notre stratégie fournie en entrée à partir de l'augmentation
        des mises en cas de paris perdus, valeur fournie par l'utilisateur."""
        
        print("DEBUG : On entre dans la méthode DiceCalculator::compute_increase_bet_method")
        # Calcul du N_Streak
        self._computed_lost_bet = - 1 + int(log(1 + self._cash / self._bet * (self._increase_decrease_on_loss - 1)) /
                                            log(self._increase_decrease_on_loss))
        # Lancement des calculs à partir du N_Streak
        self.compute_everything_from_streak_number()
        print("DEBUG : On sort de la méthode DiceCalculator::compute_increase_bet_method")
    
    def compute_bankruptcy_risk_method(self):

        print("DEBUG : On entre dans la méthode DiceCalculator::compute_bankruptcy_risk_method")
        self.calculate_streak_from_bankruptcy_risk()
        self.compute_everything_from_streak_number()
        # calculs empiriques basés sur la trésorerie disponible?
        print("DEBUG : On sort de la méthode DiceCalculator::compute_bankruptcy_risk_method")
        
    def compute_everything_from_streak_number(self):
        """A partir du nombre de paris perdants consécutifs (calculé au préalable ou fourni par l'utilisateur), cette
        méthode calcule les paramètres suivants:
            - Probabilité des N paris perdants consécutifs
            - Facteur minimal d'augmentation des mises quand un pari est perdu
            - Facteur maximal d'augmentation des mises quand un pari est perdu
            - La trésorerie minimale nécessitée par la stratégie, basée sur le facteur minimal d'augmentation des mises
            - La trésorerie maximale nécessitée par la stratégie, basée sur le facteur maximal d'augmentation des mises.
            - La probabilité d'échec de la stratégie en fonction des K paris perdants consécutifs parmi N paris."""
        
        print("DEBUG : On entre dans la méthode DiceCalculator::compute_everything_from_streak_number")
        self.calculate_streak_event_probability(self._computed_lost_bet)
        possible_values = np.linspace(1, 1.0 / (1 - self._event_probability) ** 5,
                                      100 * int(1.0 / (1 - self._event_probability) ** 5) + 1)
        computed_expression = self.compute_inequality(possible_values, self._computed_lost_bet)
        self.calculate_minimal_increase_factor(possible_values, computed_expression)
        self.calculate_maximal_increase_factor(0.00001, self._computed_lost_bet)
        self._minimal_cash = self.calculate_cash(self._minimal_increase_bet, self._computed_lost_bet)
        self._maximal_cash = self.calculate_cash(self._maximal_increase_bet, self._computed_lost_bet)
        self._streak_probability = self.calculate_probability_of_streak(self._computed_lost_bet)
        # Si on est logique, il faudrait faire ce calcul sur self._computed_lost_bet + 1... à vérifier!!!
        # Dans le doute, on garde ce calcul, qui est le plus prudent... Ne pas prendre de risques inutiles!
        print("DEBUG : On sort de la méthode DiceCalculator::compute_everything_from_streak_number")
    
    def calculate_streak_event_probability(self, n_streak):
        """Calcule la probabilité que n_streak paris perdus consécutifs surviennent"""
        
        print("DEBUG : On entre dans la méthode DiceCalculator::calculate_streak_event_probability")
        self._computed_risk_serie = (1 - self._event_probability) ** n_streak
        print("DEBUG : On sort de la méthode DiceCalculator::calculate_streak_event_probability")
     
    def calculate_cash(self, reason, n_streak):
        """Calcule la trésorerie nécessaire pour encaisser les n_streak paris perdants consécutifs pour un facteur
        d'augmentation des mises en cas de paris perdu donné par la variable reason"""
        
        print("DEBUG : On entre dans la méthode DiceCalculator::calculate_cash()")
        cash = self._bet * (1 - reason ** (n_streak + 1)) / (1 - reason)
        cash = ceil(100000000 * cash) / 100000000
        print("DEBUG : On sort de la méthode DiceCalculator::calculate_cash()")
        return cash
    
    def compute_inequality(self, vector, n_streak):
        """Dans cette méthode, on calcule l'inéquation qui nous assure de ne pas faire de pertes lorsque,
        après n_streak paris perdants consécutifs, le suivant est gagnant. L'idée en est qu'on récupère alors la somme
        des mises en jeu sur les n paris concerné, éventuellement avec bénéfices, mais pas forcément."""
        
        print("DEBUG : On entre dans la méthode DiceCalculator::compute_inequality()")
        val_condition = [0.] * len(vector)
        for i in range(len(vector)):
            if vector[i] != 1:
                val_condition[i] = (vector[i] ** (n_streak + 1)) * (1 - self._payout + self._payout / vector[i]) - 1
                if val_condition[i] < -1e10:
                    val_condition[i+1:] = [-1e+11] * (len(vector) - i)
                    break
            else:
                val_condition[i] = 1
        print("DEBUG : On sort de la méthode DiceCalculator::compute_inequality()")
        return val_condition
    
    def calculate_minimal_increase_factor(self, values, inequality):
        """Cette méthode sert à trouver le plus petit facteur multiplicateur de mise pour lequel
        l'inéquation est vérifiée."""

        print("DEBUG : On entre dans la méthode DiceCalculator::calculate_minimal_increase_factor")
        index = 0
        for i in range(len(inequality)):
            if inequality[i] <= 0:
                index = i
                break
        self._minimal_increase_bet = values[index]
        print("DEBUG : On sort de la méthode DiceCalculator::calculate_minimal_increase_factor")
        
    def calculate_maximal_increase_factor(self, precision, n_streak):
        """Cette méthode sert à calculer le meilleur coefficient multiplicateur de mise en cas de pari perdu.
        Meilleur au sens de nos attentes, et elles peuvent être multiples. Ainsi, suivant nos objectifs basés sur le
        nombre de paris perdants consécutifs, on en déduit par dichotomie le meilleur coefficient de mise associé."""
        
        print("DEBUG : On entre dans la méthode DiceCalculator::calculate_maximal_increase_factor")
        iteration = 0
        borne_inf = 1
        borne_sup = 1.0 / (1 - self._event_probability) ** 5
        multiply_test = 1
        while iteration < 1000000 and self.calculate_cash(borne_sup, n_streak) < self._cash:
            iteration += 1
            borne_sup *= 1.1
            print(str("Modification de la borne sup : itération = %i") % iteration)
        iteration = 0
        while iteration <= 1000000 and borne_sup - borne_inf > precision:
            iteration += 1
            multiply_test = (borne_inf + borne_sup) / 2.0
            cash = self.calculate_cash(multiply_test, n_streak)
            print(str("La valeur du cash est de %.8f") % cash)
            print(str("La valeur du facteur testé est de %.5f") % multiply_test)
            if cash < self._cash:
                borne_inf = multiply_test
            else:
                borne_sup = multiply_test
        self._maximal_increase_bet = multiply_test
        print("DEBUG : On sort de la méthode DiceCalculator::calculate_maximal_increase_factor")
    
    def calculate_probability_of_streak(self, n_streak):
        """Dans cette méthode, on calcule la probabilité, pour n_streak tirages consécutifs, que notre scénario
        catastrophe arrive avec la stratégie que nous avons défini dans le widget, à savoir que le nombre de paris
        perdus consécutifs nous amène à la banqueroute. Plus on joue et logiquement plus cette probabilité augmente."""
        
        print("DEBUG : On entre dans la méthode DiceCalculator::calculate_probability_of_streak")
        num_coins = self._wished_dices              # Nombre de paris total
        min_heads = n_streak                        # Nombre de paris perdants consécutifs
        head_prob = 1 - self._event_probability     # Probabilité du pari perdu

        memo = [0.] * (num_coins + 1)

        for i in range(min_heads, num_coins + 1, 1):
            result = head_prob ** min_heads
            for first_tail in range(1, min_heads + 1, 1):
                pr = memo[i - first_tail]
                result += (head_prob ** (first_tail - 1)) * (1 - head_prob) * pr
            memo[i] = result
        print("DEBUG : On sort de la méthode DiceCalculator::calculate_probability_of_streak")
        return memo[num_coins]

    def calculate_streak_from_bankruptcy_risk(self):
        """Dans cette méthode on calcule le N_streak optimal qui satisfait au risque maximal de banqueroute fixé par
        l'utilisateur et aux autres paramètres fournis en entrée."""
        
        print("DEBUG : On entre dans la méthode DiceCalculator::calculate_streak_from_bankruptcy_risk")
        streak_min = 1
        streak_max = 10
        proba = self._bankruptcy_probability
        while self.calculate_probability_of_streak(streak_max) > proba:
            streak_max *= 2
        counter = 0
        while counter < 1000000 and streak_max - streak_min > 1:
            streak_test = int((streak_min + streak_max) / 2)
            counter += 1
            if self.calculate_probability_of_streak(streak_test) >= proba:
                streak_min = streak_test
            else:
                streak_max = streak_test
        print("DEBUG : On sort de la méthode DiceCalculator::calculate_streak_from_bankruptcy_risk")
        self._computed_lost_bet = streak_max

    def switch_results(self):
        self._computed_lost_bet, self._computed_lost_bet_opt = self._computed_lost_bet_opt, self._computed_lost_bet
        self._computed_risk_serie, self._computed_risk_serie_opt = self._computed_risk_serie_opt, \
                                                                   self._computed_risk_serie
        self._minimal_increase_bet, self._minimal_increase_bet_opt = self._minimal_increase_bet_opt, \
                                                                     self._minimal_increase_bet
        self._maximal_increase_bet, self._maximal_increase_bet_opt = self._maximal_increase_bet_opt, \
                                                                     self._maximal_increase_bet
        self._minimal_cash, self._minimal_cash_opt = self._minimal_cash_opt, self._minimal_cash
        self._maximal_cash, self._maximal_cash_opt = self._maximal_cash_opt, self._maximal_cash
        self._streak_probability, self._streak_probability_opt = self._streak_probability_opt, self._streak_probability

    def compute_cash_method(self):
        self.switch_results()
        self._increase_decrease_on_loss = 1 + 1 / ((1 / self._event_probability) - 1)
        print(self._increase_decrease_on_loss)
        self.compute_increase_bet_method()
        while self._minimal_cash > self._cash:
            self._computed_lost_bet -= 1
            self.compute_everything_from_streak_number()
        self.switch_results()
