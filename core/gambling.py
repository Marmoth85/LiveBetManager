class Gambling:
    
    def __init__(self):
        """ On défini les variables que l'on utilisera dans les classes filles """
        
        print("DEBUG : On entre dans le constructeur de Gambling")
        self._currency = ""
        self._cash = 0.
        self._cash_precision_spinbox = 0
        self._bet = 0.
        self._bet_precision_spinbox = 0
        self._event_probability = 0.
        self._payout = 0.
        self._increase_decrease_on_win = 1.
        self._increase_decrease_on_loss = 1.
        self._wished_dices = 0
        self._black_in_row = 0
        self._probability_in_row = 0.
        self._bankruptcy_probability = 0.
        print("DEBUG : On sort du constructeur de Gambling")
        
    def load_input_data(self):
        raise NotImplementedError
    
    def update_result_data(self):
        raise NotImplementedError
    
    def check_inputs(self):
        raise NotImplementedError
    
    def compute_expectation(self):
        raise NotImplementedError
    
    def update_cash_precision(self):
        
        print("DEBUG : On entre dans la méthode Gambling::update_cash_precision")
        if self._currency == "Bitcoin":
            self._cash_precision_spinbox = -4
        elif self._currency == "Ethereum":
            self._cash_precision_spinbox = -3
        elif self._currency == "Litecoin":
            self._cash_precision_spinbox = -2
        elif self._currency == "Euro" or self._currency == "Dollar":
            self._cash_precision_spinbox = 0
        elif self._currency == "Burst" or self._currency == "Dogecoin":
            self._cash_precision_spinbox = 3
        print("DEBUG : On sort de la méthode Gambling::update_cash_precision")
    
    def update_bet_precision(self):
        
        print("DEBUG : On entre dans la méthode Gambling::update_bet_precision")
        if self._currency == "Bitcoin":
            self._bet_precision_spinbox = -8
        elif self._currency == "Ethereum":
            self._bet_precision_spinbox = -7
        elif self._currency == "Litecoin":
            self._bet_precision_spinbox = -6
        elif self._currency == "Euro" or self._currency == "Dollar":
            self._bet_precision_spinbox = -2
        elif self._currency == "Burst" or self._currency == "Dogecoin":
            self._bet_precision_spinbox = 0
        print("DEBUB : On sort de la méthode Gambling::update_bet_precision")
