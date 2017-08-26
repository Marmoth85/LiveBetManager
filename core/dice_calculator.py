from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import pyqtSlot

from math import log, ceil, pow, floor
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
        
        if self._choosen_method == "Probabilité maximale de l'échec de la martingale":
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
        else:
            self.label_output_lost_bet_opt.setText("--")
            self.label_output_risk_serie_opt.setText("--")
            self.label_output_minimal_increase_bet_opt.setText("--")
            self.label_output_maximal_increase_bet_opt.setText("--")
            self.label_output_minimal_cash_opt.setText("--")
            self.label_output_maximal_cash_opt.setText("--")
            self.label_output_streak_probability_opt.setText("--")
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
            # Appeler la procédure correspondante
            self.update_result_data()
        print("DEBUG : on sort du SLOT DiceCalculator::compute_expectation()")

    def display_input_error_message(self, message):
        print("DEBUG : on entre dans DiceCalculator::display_input_error_message()")
        QMessageBox.critical(self, "Erreur dans les paramètres d'entrée", message)
        print("DEBUG : on sort de DiceCalculator::display_input_error_message()")

    def compute_risk_serie_method(self):
        """Cette méthode calcule les paramètres théoriques souhaités ainsi que ceux, pragmatiques, quand la trésorerie
        réelle ne correspond pas à ce que nous voudrions sur un plan purement théorique."""
    
        print("Compute risk_serie_method")
        """self.load_input_data()
    
        vector_coefficient = np.linspace(1, 1.0 / pow(1 - self.__event_probability, 5),
                                         100 * int(1.0 / pow(1 - self.__event_probability, 5)) + 1)
    
        self.compute_streak_goal()
        self.compute_increase_on_loss_goal(vector_coefficient)
        self.compute_cash_goal()
    
        self.compute_streak_practical()
        self.compute_increase_on_loss_practical(vector_coefficient)
        self.compute_cash_practical()"""
        
    def compute_streak_serie_method(self):
        print("Compute streak serie method")
    
    def compute_increase_bet_method(self):
        print("Compute increase bet method")
    
    def compute_bankruptcy_risk_method(self):
        print("Compute bankruptcy risk method")
    
    def calculate_streak_event_probability(self, n_streak):
        """Calcule la probabilité que n_streak paris perdus consécutifs surviennent"""
        print("DEBUG : On entre dans la méthode DiceCalculator::calculate_streak_event_probability")
        self._computed_risk_serie = (1 - self._event_probability) ** n_streak
        print("DEBUG : On sort de la méthode DiceCalculator::calculate_streak_event_probability")

    def compute_increase_on_loss_goal(self, vector):
        """Calcule le coefficient multiplicateur de mise quand on perd un pari"""
        
        val = self.compute_inequality(vector, "theoretical")
        self.__goal_multiply = vector[self.find_minimal_coefficient_index(val)]
     
    def calculate_cash(self, reason):
        """Calcule la trésorerie nécessaire pour encaisser les n_streak paris perdants consécutifs pour un facteur
        d'augmentation des mises en cas de paris perdu donné par la variable reason"""
        
        print("DEBUG : On entre dans la méthode DiceCalculator::calculate_cash()")
        cash = self._bet * (1 - reason ** (self._computed_lost_bet + 1)) / (1 - reason)
        cash = ceil(100000000 * cash) / 100000000
        print("DEBUG : On sort de la méthode DiceCalculator::calculate_cash()")
        return cash

    def compute_streak_practical(self):
        """Calcule le nombre de coups perdants associé au risque pratique (lié au manque de cash) concédé"""

        self.__black_in_row_computed = int(
            log(self.__cash / self.__bet * (self.__goal_multiply - 1) + 1) / log(self.__goal_multiply))
        self.__probability_in_row_computed = int(1 / pow(1 - self.__event_probability, self.__black_in_row_computed))

    def compute_increase_on_loss_practical(self, vector):
        """Calcule les coefficients multiplicateurs de mise quand on perd un pari:
        le minimum possible pour utiliser le moins de cash possible en cas de banqueroute
        et le maximum possible pour utiliser l'intégralité de la trésorerie disponible pour un risque donné."""

        value = self.compute_inequality(vector, "practical")
        self.__practical_multiply_min = vector[self.find_minimal_coefficient_index(value)]
        self.__practical_multiply_max = float(floor(10000 * self.dichotomy(0.00001, "lost bets max"))) / 10000

    def compute_cash_practical(self):
        """Calcule la trésorerie nécessaire pour encaisser les n coups perdants de suite calculés dans deux cas
        possibles. D'abord dans le cas où on augmente les mises avec un coefficient le plus faible possible pour
        conserver le maximum de cash possible en cas de bust, puis le contraire, à savoir, avec le coefficient le
        plus gros possible, de sorte à utiliser l'intégralité du cash ou presque pour le même risque concédé."""

        self.__practical_cash = self.__bet * (
            1 - pow(self.__practical_multiply_min, self.__black_in_row_computed)) / (1 - self.__practical_multiply_min)
        self.__practical_cash = ceil(100000000 * self.__practical_cash) / 100000000

        self.__practical_cash_optimal = self.__bet * (
            1 - pow(self.__practical_multiply_max, self.__black_in_row_computed)) / (1 - self.__practical_multiply_max)
        self.__practical_cash_optimal = ceil(100000000 * self.__practical_cash_optimal) / 100000000
        self.__black_in_row_selected = self.__black_in_row_computed
    
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
    
    def calculate_minimal_increase_factor(self, values):
        """Cette méthode sert à trouver le plus petit facteur multiplicateur de mise pour lequel
        l'inéquation est vérifiée."""

        print("DEBUG : On entre dans la méthode DiceCalculator::calculate_minimal_increase_factor")
        index = 0
        for i in range(len(values)):
            if values[i] <= 0:
                index = i
                break
        self._minimal_increase_bet = values[index]
        print("DEBUG : On sort de la méthode DiceCalculator::calculate_minimal_increase_factor()")
        
    def dichotomy(self, precision, method):
        """Cette méthode sert à calculer le meilleur coefficient multiplicateur de mise en cas de pari perdu.
        Meilleur au sens de nos attentes, et elles peuvent être multiples. Deux cas sont prévus ici: utiliser un
        nombre préconiser de paris perdants consécutifs maximal et en déduire par dichotomie les meilleur
        coefficient de mise associé.
        Ou au contraire, utiliser un nombre de paris perdants consécutifs bien déterminé par l'utilisateur et du
        coup, calculer pour ce nombre, le meilleur coefficient multiplicateur de mises."""
        
        number_bet = 0
        iteration = 0
        borne_inf = 1
        borne_sup = 1.0 / pow((1 - self.__event_probability), 5)
        multiply_test = 1
        if method == "lost bets max":
            number_bet = self.__black_in_row_computed
        elif method == "fixated lost bets":
            number_bet = self.__black_in_row_selected
        while iteration <= 1000000 and borne_sup - borne_inf > precision:
            iteration += 1
            multiply_test = (borne_inf + borne_sup) / 2.0
            cash = self.__bet * (1 - pow(multiply_test, number_bet)) / (1 - multiply_test)
            if cash < self.__cash:
                borne_inf = multiply_test
                value = self.__bet * (1 - pow(borne_sup, number_bet)) / (1 - borne_sup)
                if value < self.__cash:
                    borne_sup *= 1.1
            else:
                borne_sup = multiply_test
        return multiply_test
    
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
    
    @pyqtSlot()
    def update_bankruptcy_display(self):
        """Ce SLOT sert à retirer les précédents calculs de l'affichage en raison de modification(s) dans les
        paramètres d'entrée. Ainsi, on invite l'utilisateur à ne pas prendre de décision trop hâtive et donc à
        relancer le calcul de la probabilité de banqueroute en n'oubliant pas les dernières modifications."""
        
        self.labelOutputBankruptcyRisk.setText("-- Mettre à jour --")

    @pyqtSlot()
    def maximize_increase_on_loss(self):
        """Ce SLOT sert à calculer le plus gros coefficient d'increase de mise possible pour un nombre de paris
        perdants consécutifs défini par l'utilisateur."""
        
        value = self.dichotomy(0.00001, "fixated lost bets")
        self.labelIncreaseOnlossMAX.setText(str("%.4f" % value))

    @pyqtSlot()
    def update_n_break(self):
        """Ce SLOT est déclenché par le spinBox de blocage du nombre de loss in row.
        Il sert à explicitement demander à l'utilisateur de recalculer le coefficient multiplicateur de mises étant
        donné la modification d'un des paramètres d'entrée de la stratégie."""
        
        self.__black_in_row_selected = self.spinBoxBlockNumberBet.value()
        self.labelIncreaseOnlossMAX.setText("-- Mettre à jour --")
