from PyQt5.QtWidgets import QWidget
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
        self.__choosen_method = ""
        self.__computed_lost_bet, self.__computed_lost_bet_opt = 0, 0
        self.__computed_risk_serie, self.__computed_risk_serie_opt = 0., 0.
        self.__minimal_increase_bet, self.__minimal_increase_bet_opt = 0., 0.
        self.__maximal_increase_bet, self.__maximal_increase_bet_opt = 0., 0.
        self.__minimal_cash, self.__minimal_cash_opt = 0., 0.
        self.__maximal_cash, self.__maximal_cash_opt = 0., 0.
        self.__streak_probability, self.__streak_probability_opt = 0., 0.
        
    def load_input_data(self):
        """Cette méthode récupère les informations depuis l'IHM pour les stocker dans les attributs d'objets,
        afin de pouvoir les exploiter facilement dans les calculs qui suivront."""
        
        self.__cash = self.doubleSpinBox_input_cash.value()
        self.__bet = self.doubleSpinBox_input_bet.value()
        self.__event_probability = self.doubleSpinBox_input_proba_event.value() / 100
        self.__payout = self.doubleSpinBox_input_payout.value()
        self.__wished_dices = self.spinBox_input_dice_number.value()
        self.__probability_in_row = (lambda x: 1 / x if x != 0 else 0.0)(self.spinBox_risk_serie.value())
        self.__black_in_row = self.spinBox_streak_serie.value()
        self.__increase_decrease_on_loss = 1 + self.doubleSpinBox_increase_bet.value() / 100
        self.__bankruptcy_probability = self.doubleSpinBox_bankruptcy_probability.value() / 100
        
        if self.radioButton_risk_serie.isChecked():
            self.__choosen_method = "Risque de la série négative"
        elif self.radioButton_streak_serie.isChecked():
            self.__choosen_method = "Nombre de paris perdus à la suite"
        elif self.radioButton_increase_bet.isChecked():
            self.__choosen_method = "Augmentation des mises en cas de pari perdu"
        elif self.radioButton_bankruptcy_probability.isChecked():
            self.__choosen_method = "Probabilité maximale de l'échec de la martingale"

    def update_result_data(self):
        """Cette méthode récupère les résultats des calculs effectués pour les afficher dans l'IHM"""
        
        self.label_output_choosen_method.setText(self.__choosen_method)
        self.label_output_lost_bet.setText(str(self.__computed_lost_bet))
        self.label_output_risk_serie.setText(str((lambda x: int(1 / x) if x != 0 else 0.0)(self.__computed_risk_serie)))
        self.label_output_minimal_increase_bet.setText(str("%.2f" % (lambda x: (x - 1) * 100)(self.__minimal_increase_bet) + " %"))
        self.label_output_maximal_increase_bet.setText(str("%.2f" % (lambda x: (x - 1) * 100)(self.__maximal_increase_bet) + " %"))
        self.label_output_minimal_cash.setText(str("%.8f" % self.__minimal_cash))
        self.label_output_maximal_cash.setText(str("%.8f" % self.__maximal_cash))
        self.label_output_streak_probability.setText(str("%.2f" % (lambda x: 100 * x)(self.__streak_probability) + " %"))
        
        if self.__choosen_method == "Probabilité maximale de l'échec de la martingale":
            self.label_output_lost_bet_opt.setText(str(self.__computed_lost_bet_opt))
            self.label_output_risk_serie_opt.setText(str((lambda x: int(1 / x) if x != 0 else 0.0)(self.__computed_risk_serie_opt)))
            self.label_output_minimal_increase_bet_opt.setText(str("%.2f" % (lambda x: (x - 1) * 100)(self.__minimal_increase_bet_opt) + " %"))
            self.label_output_maximal_increase_bet_opt.setText(str("%.2f" % (lambda x: (x - 1) * 100)(self.__maximal_increase_bet_opt) + " %"))
            self.label_output_minimal_cash_opt.setText(str("%.8f" % self.__minimal_cash_opt))
            self.label_output_maximal_cash_opt.setText(str("%.8f" % self.__maximal_cash_opt))
            self.label_output_streak_probability_opt.setText(str("%.2f" % (lambda x: 100 * x)(self.__streak_probability_opt) + "    %"))
        else:
            self.label_output_lost_bet_opt.setText("--")
            self.label_output_risk_serie_opt.setText("--")
            self.label_output_minimal_increase_bet_opt.setText("--")
            self.label_output_maximal_increase_bet_opt.setText("--")
            self.label_output_minimal_cash_opt.setText("--")
            self.label_output_maximal_cash_opt.setText("--")
            self.label_output_streak_probability_opt.setText("--")

    def check_inputs(self):
        """Cette méthode a pour objet de vérifier que les inputs soient cohérents.
        Aucun calcul ne doit être lancé sans être assuré de la bonne forme des paramètres d'entrée"""
        
        print("Checking the inputs is not yet implemented")

    @pyqtSlot()
    def compute_expectation(self):
        """Cette méthode est un SLOT déclenché par le bouton "Calculer".
        On calcule les paramètres théoriques souhaités ainsi que ceux, pragmatiques, quand la trésorerie réelle ne
        correspond pas à ce que nous voudrions sur un plan purement théorique."""
    
        self.load_input_data()
        # Tester le choix de la méthode
        # Appeler la procédure correspondante
        self.update_result_data()

    def compute_lose_in_tow_method(self):
        """Cette méthode calcule les paramètres théoriques souhaités ainsi que ceux, pragmatiques, quand la trésorerie
        réelle ne correspond pas à ce que nous voudrions sur un plan purement théorique."""
    
        self.load_input_data()
    
        vector_coefficient = np.linspace(1, 1.0 / pow(1 - self.__event_probability, 5),
                                         100 * int(1.0 / pow(1 - self.__event_probability, 5)) + 1)
    
        self.compute_streak_goal()
        self.compute_increase_on_loss_goal(vector_coefficient)
        self.compute_cash_goal()
    
        self.compute_streak_practical()
        self.compute_increase_on_loss_practical(vector_coefficient)
        self.compute_cash_practical()
        
    def compute_streak_goal(self):
        """Calcule le nombre de coups perdants associé au risque concédé"""
        
        n_bets_max_th = log(1.0 / self.__black_risk) / log(1 - self.__event_probability)
        self.__black_in_row_expected = ceil(n_bets_max_th)
        self.__probability_in_row_expected = int(1 / pow(1 - self.__event_probability, self.__black_in_row_expected))

    def compute_increase_on_loss_goal(self, vector):
        """Calcule le coefficient multiplicateur de mise quand on perd un pari"""
        
        val = self.compute_inequality(vector, "theoretical")
        self.__goal_multiply = vector[self.find_minimal_coefficient_index(val)]
     
    def compute_cash_goal(self):
        """Calcule la trésorerie nécessaire pour encaisser les n coups perdants de suite calculés"""
        
        self.__goal_cash = self.__bet * (
            1 - pow(self.__goal_multiply, self.__black_in_row_expected) ) / (1 - self.__goal_multiply)
        self.__goal_cash = ceil(100000000 * self.__goal_cash) / 100000000

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
    
    def compute_inequality(self, vector, method):
        """Dans cette méthode, on calcule l'inéquation qui nous assure de ne pas faire de pertes lorsque,
        après n-1 paris perdants consécutifs, le n-ième est gagnant. L'idée en est qu'on récupère alors la somme des
        mises en jeu sur les n paris concerné, éventuellement avec bénéfices, mais pas forcément."""

        val_condition = [0.] * len(vector)
        if method == "theoretical":
            lost_bet = self.__black_in_row_expected
        else:
            lost_bet = self.__black_in_row_computed
        for i in range(len(vector)):
            if vector[i] != 1:
                val_condition[i] = pow(vector[i], lost_bet) * (1 - self.__payout + self.__payout / vector[i]) - 1
                if val_condition[i] < -1e10:
                    val_condition[i+1:] = [-1e+11] * (len(vector) - i)
                    break
            else:
                val_condition[i] = 1

        return val_condition
    
    def find_minimal_coefficient_index(self, values):
        """C'est plus une petite fonction utilitaire qu'une méthode à proprement parler.
        Elle sert juste à trouver le premier indice pour lequel notre inéquation est vérifiée."""

        index = 0
        for i in range(len(values)):
            if values[i] <= 0:
                index = i
                break
        return index
        
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
    
    @pyqtSlot()
    def calculate_probability_of_streak(self):
        """Dans ce SLOT, on calcule la probabilité, pour n tirages consécutifs, que notre scénario catastrophe,
        à savoir que le nombre de paris perdus consécutifs nous amène à la banqueroute, arrive avec la stratégie que 
        nous avons défini dans le widget. Plus on joue, plus cette probabilité augmente, ce qui est intuitif."""
        
        self.load_input_data()
        num_coins = self.__wished_dices
        min_heads = self.__black_in_row_selected
        head_prob = 1 - self.__event_probability

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

    @pyqtSlot()
    def currency_changed(self):
        pass
    
    @pyqtSlot()
    def precision_changed(self):
        pass
