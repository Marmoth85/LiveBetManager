class Gambling:
    
    def __init__(self):
        """ On défini les variables que l'on utilisera dans les classes filles """
        self.__currency = ""
        self.__cash = 0.
        self.__cash_precision_spinbox = 0
        self.__bet = 0.
        self.__bet_precision_spinbox = 0
        self.__event_probability = 0.
        self.__payout = 0.
        self.__increase_decrease_on_win = 1.
        self.__increase_decrease_on_loss = 1.
        self.__wished_dices = 0
        self.__black_in_row = 0
        self.__probability_in_row = 0.
        self.__bankruptcy_probability = 0.
        
    def load_input_data(self):
        raise NotImplementedError
    
    def update_result_data(self):
        raise NotImplementedError
    
    def check_inputs(self):
        raise NotImplementedError
    
    def compute_expectation(self):
        raise NotImplementedError
    
    def update_cash_precision(self):
        if self.__currency == "Bitcoin":
            self.__cash_precision_spinbox = -4
        elif self.__currency == "Ethereum":
            self.__cash_precision_spinbox = -3
        elif self.__currency == "Litecoin":
            self.__cash_precision_spinbox = -2
        elif self.__currency == "Euro" or self.__currency == "Dollar":
            self.__cash_precision_spinbox = 0
        elif self.__currency == "Burst" or self.__currency == "Dogecoin":
            self.__cash_precision_spinbox = 3
    
    def update_bet_precision(self):
        if self.__currency == "Bitcoin":
            self.__bet_precision_spinbox = -8
        elif self.__currency == "Ethereum":
            self.__bet_precision_spinbox = -7
        elif self.__currency == "Litecoin":
            self.__bet_precision_spinbox = -6
        elif self.__currency == "Euro" or self.__currency == "Dollar":
            self.__bet_precision_spinbox = -2
        elif self.__currency == "Burst" or self.__currency == "Dogecoin":
            self.__bet_precision_spinbox = 0
