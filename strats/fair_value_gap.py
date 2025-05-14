import pandas as pd
import matplotlib.pyplot as plt
#import mplfinance as mpf
import numpy as np
from sklearn.linear_model import LinearRegression as linregress
import random
from scipy.signal import argrelextrema
from strategy import strategy

class FairValueGap(strategy):

    def __init__(self):
        super().__init__()
        self.name = 'Fair Value Gap'

    def load_data(self):
        return super().load_data()
    
    #strategie de fair value Gap
    def strat_FairValue_Gap(self, df):
        # tous ces parametres ont été optimisés par un process de machine learning
        A = 8 #on prend les donnes entre le 8 eme et le 19 eme dernier candle
        B = 19
        F = 1.095 #niveau d'annulation de pose longue
        G = 0.96 #niveau de stop Loss de pose longue
        H = 1.045 #niveau de stop Gain de pose longue
        d1 = 66 #Duree max d'une pose longue
        I = 0.95 #niveau d'annulation de pose courte
        J = 1.02 #niveau de stop Loss de pose courte
        K = 0.965 #niveau de stop Gain de pose courte
        d2 = 49 #Duree max d'une pose courte
        Taillemax = 0 
        Taille = 0
        indice = 0
        for i in range(A,B):
            Taille = max((df.iloc[-B-1+i]['close']-df.iloc[-B-1+i]['open']),(df.iloc[-B-1+i]['open']-df.iloc[-B-1+i]['close'])) #prend la taille du candle
            if Taille > Taillemax : #Si c'est le plus grand candle
                Taillemax = Taille
                indice = i
        #Si la trend est up
        if df.iloc[-B-1+indice]['close']-df.iloc[-B-1+indice]['open'] > 0 : 
            maax = df.iloc[-B+indice]['high'] 
            miin = df.iloc[-B-2+indice]['low'] 
            sup = (maax+miin)/2 #prend le milieu du precedent High et du prochain Low
            mi = df.iloc[-B+indice+1:]['low'].min() 
            if mi > sup : #verifie que le support a pas deja ete touché
                return 1,sup,sup*F,sup*G,sup*H,d1
            else : 
                return 0,0,0,0,0,0
        #fait pareil pour une trend down
        else :
            miin = df.iloc[-B+indice]['open'] 
            maax = df.iloc[-B-2+indice]['close'] 
            res = (maax+miin)/2
            ma = df.iloc[-B+indice+1:]['high'].max()
            if ma < res :
                return -1,res,res*I,res*J,res*K,d2
            else :
                return 0,0,0,0,0,0 

    #code similaire a celui pour le fibonacci horizontale
    def compute_signal(self, src_data : pd.DataFrame , start=None, end=None, limit=None):
        
        if start and end:
            src_data = src_data[start:end]
        elif start:
            src_data = src_data[start:]
        elif end:
            src_data = src_data[:end]
        df = src_data.copy()
        df['signal'] = 0
        result = None
        Position_possible = 0
        Position_active = 0
        nombre_achat = 0
        niveau_achat = 0
        niveau_annulation = 0
        niveau_stop_loss = 0
        niveau_stop_gain = 0
        duree_stop_gain = 0 
        for i, idx in enumerate(df.index):
            if i < 50:
                continue
            data_up_to_idx = df.loc[:idx]
            level = data_up_to_idx['close'].iloc[-1]
            if Position_active == 1:
                duree_stop_gain = duree_stop_gain-1
                if nombre_achat == 1 :
                    if  duree_stop_gain == 0 or level > niveau_stop_gain or level < niveau_stop_loss :
                        Position_possible = 0
                        Position_active = 0
                    else : 
                        df.at[idx, 'signal'] = 1
                else :
                    if  duree_stop_gain == 0 or level < niveau_stop_gain or level > niveau_stop_loss :
                        Position_possible = 0
                        Position_active = 0
                    else :
                        df.at[idx, 'signal'] = -1
            elif Position_possible == 1 :
                if nombre_achat == 1 : 
                    if level > niveau_annulation :
                        Position_possible = 0
                    if level < niveau_achat :
                        Position_active = 1
                        df.at[idx, 'signal'] = 1
                        
                else :
                    if level < niveau_annulation :
                        Position_possible = 0
                    if level > niveau_achat :
                        Position_active = 1
                        df.at[idx, 'signal'] = -1
                        
            else : 
                nombre_achat,niveau_achat,niveau_annulation,niveau_stop_loss,niveau_stop_gain,duree_stop_gain = self.strat_FairValue_Gap(data_up_to_idx)
                if nombre_achat != 0 :
                    Position_possible = 1

        return  df['signal'].shift(1)





