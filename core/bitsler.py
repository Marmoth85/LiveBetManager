from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot

from gen_files import ui_bitsler


class Bitsler(QWidget, ui_bitsler.Ui_Bitsler):
    def __init__(self, parent=None):

        super(Bitsler, self).__init__(parent)
        self.setupUi(self)

    """
    estimate <- function (cash=0.00000300, bet=0.00000001, proba_win=0.475, payout=10){
      #proba_win <- 31.99 / 100
      proba_lose <- 1 - proba_win
      fgain <- payout
      
      #cash <- 0.00000391
      #bet <- 0.00000001
      
      n_tokens <- cash/bet
      
      # 1 chance sur 1 000 pour une série noire
      Pmc <- 1/1000
      nbets <- log(1/1000) / log(proba_lose)
      n_target <- ceiling(nbets)
      
      # Calcul du a minimal satisfaisant le gain au N_TARGET ième coup
      a <- seq(1.0001, ceiling(1 / proba_lose) + 1, by = 0.0001)
      value <- a^n_target * (1 - fgain + fgain / a) - 1
      a_min <- a[min(which(value <= 0))]
      
      # Calcul de la trésorerie nécessaire
      cash_need <- bet * (1 - a_min^n_target) / (1 - a_min)
      
      # Calcul du nombre de coups possible avec le cash (+ proba associée)
      n_avail <- log(cash / bet * (a_min - 1) + 1) / log (a_min)
      n_poss <- floor(n_avail)
      Pmc_cash <- proba_lose^n_poss
      cash_poss <- bet * (1 - a_min^n_poss) / (1 - a_min)
      
      dichotomie_a <- function(binf=1.0001, bsup=10, x=1, n=2, prec=0.00001, cash=300)
      {
        iter <- 0;
        while(iter < 1000000 & bsup - binf > prec)
        {
          iter <- iter + 1;
          a_test <- (binf + bsup) / 2;
          cash_poss <- x * (1 - a_test^n) / (1 - a_test);
          if(cash_poss < cash)
          {
            binf <- a_test;
          } else {
            bsup <- a_test;
          }
        }
        return(a_test);
      }
      a_new <- dichotomie_a(a_min, 2*a_min, bet, n_poss, 0.00001, cash)
      
      return(list(Pmc_cash=Pmc_cash, n_poss=n_poss, a_new=a_new))
    }
    
    PMCCASH <- rep(0,94)
    NPOSS <- rep(0,94)
    ANEW <- rep(0,94)
    
    for(i in 1:94){
      res <- estimate(cash = 0.00000391, bet = 0.00000001, proba_win = i/100);
      PMCCASH[i] <- res$Pmc_cash
      NPOSS[i] <- res$n_poss
      ANEW[i] <- res$a_new
    }
    
    bankrupcy <- function(proba_win=0.5, times=10, games=100, nsim=1000){
      r <- 10000;
      x <- matrix(sample(c(0,1), games*nsim, prob=c(proba_win, 1-proba_win), replace=TRUE), nrow=games, ncol=nsim, byrow = FALSE);
      y <- matrix(rep(0, games*nsim), nrow=games, ncol=nsim);
      
      y[1,] <- x[1,]
      
      for (i in 1:nsim){
        for(j in 2:games){
          y[j, i] <- (y[j-1, i] + x[j, i]) * x[j, i];
        }
      }
      m <- apply(y, 2, max);
      return(m)
    }
    
    m <- estimate(cash = 0.00021609, bet = 0.00000005, proba_win = .099,  payout=10)
    l <- bankrupcy(proba_win = 0.099, times=m$n_poss, games=500, nsim=100000)
    length(which(l>=m$n_poss))/length(l)
    """
    @pyqtSlot()
    def update_calculation(self):
        pass

    @pyqtSlot()
    def calculate_bankruptcy(self):
        pass

    @pyqtSlot()
    def update_bankruptcy_display(self):
        pass