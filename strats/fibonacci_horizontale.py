from strategy import strategy
import pandas as pd

class fibonacci_horizontale(strategy):

    def __init__(self):
        super().__init__()
        self.name = 'fibonacci horizontale'

    def load_data(self):
        return super().load_data()
    
    #fonction qui detecte si il y a, le plus grand un max local entre la b1 ème et b2 ème derniere valeur
    def detect_max(self, df,b1,b2,window): 
        subset = df.iloc[-b2-1 : -b1 if b1 != 0 else None]  
        n = subset['high'].max()
        date_of_max = subset['high'].idxmax()
        recent_highs = df.iloc[-b2-window:]['high']
        if (recent_highs <= n).all():
            return n,date_of_max
        else :
            return 0,0

    #fonction qui detecte si il y a, le plus grand un min local entre la b1 ème et b2 ème derniere valeur
    def detect_min(self,df,b1,b2,window):
        subset = df.iloc[-b2-1 : -b1 if b1 != 0 else None]
        n = subset['low'].min()
        date_of_min = subset['low'].idxmin()
        recent_low = df.iloc[-b2-window:]['low']
        if (recent_low >= n).all():
            return n,date_of_min
        else :
            return 0,0


    #fonction qui etablie l'analyse au vue de la strategie basé sur des niveaux de resistance et de support horizontale
    def strat_fibonacci(self, df):
        # tous ces parametres ont été optimisés par un process de machine learning
        X = 5 #defini le b1 (ci dessus)
        Y = 37 #defini le b2 (ci dessus)
        Z = 5 #defini la windows des max/min locaux
        x1 = 1.02 #defini un niveau d'annulation (si le cours atteint ce montant * valeur du swing High, sans avoir touche le support)
        x2 = 1.075 #Stop Gain et Loss pour une position longue
        x3 = 43 #duree maximale d'une pose longue
        y1 = 0.98 #defini un niveau d'annulation (si le cours atteint ce montant * valeur du swing Low, sans avoir touche la resistance)
        y2 = 0.95 #Stop Gain et Loss pour une position courte
        y3 = 17 #duree maximale d'une pose courte
        level = df['close'].iloc[-1] #recupere le dernier niveau
        a,d1 = self.detect_max(df,X,Y,Z) #recupere l'indice et le niveau du swing high
        b,d2 = self.detect_min(df,X,Y,Z) #recupere l'indice et le niveau du swing low
        if a==0 or b==0: #si le swing high ou low n'existe pas, renvoie rien
            return 0,0,0,0,0,0
        if d1 > d2 : 
            Trend = "up"
        else : 
            Trend = "down"
        n1 = 0.236 * (a-b) + b
        n2 = 0.382 * (a-b) + b
        n3 = 0.5 * (a-b) + b
        n4 = 0.618 * (a-b) + b
        n5 = 0.786 * (a-b) + b
        #pose tes niveaux de fibonacci (#23,6% - 38,2% - 50% - 61,8% - 78,6% )
        if Trend == "up":
            mi = df.iloc[df.index > d1]['low'].min() 
            if mi < n4 : #verifie que le support a pas deja ete atteinte une fois
                return 0,0,0,0,0,0
            else : 
                nombre_achat = 1
                niveau_achat = n4
                niveau_annulation = a*x1
                niveau_stop_loss = n3+(n2-n3)*0.1
                niveau_stop_gain = n4*x2
                duree_stop_gain = x3
                return nombre_achat,niveau_achat,niveau_annulation,niveau_stop_loss,niveau_stop_gain,duree_stop_gain
        else : 
            ma = df.loc[df.index > d2]['high'].max()

            if ma > n2 : #verifie que le support a pas deja ete atteinte une fois
                return 0,0,0,0,0,0
            else : 
                nombre_achat = -1
                niveau_achat = n2
                niveau_annulation = b*y1
                niveau_stop_loss = n3+(n4-n3)*0.1
                niveau_stop_gain = n2*y2
                duree_stop_gain = y3
                return nombre_achat,niveau_achat,niveau_annulation,niveau_stop_loss,niveau_stop_gain,duree_stop_gain


    def compute_signal(self, src_data : pd.DataFrame , start=None, end=None, limit=None):

        if start and end:
            src_data = src_data[start:end]
        elif start:
            src_data = src_data[start:]
        elif end:
            src_data = src_data[:end]
        df = src_data.copy()
        df['signal'] = 0 #initie la position a neutre
        result = None
        Position_possible = 0 #defini si une prise de position est possible (resistance ou support en attente d'etre touché)
        Position_active = 0 #defini si une possition est prise
        nombre_achat = 0 #position longue ou courte
        niveau_achat = 0 #Niveau du support/resistance a toucher
        niveau_annulation = 0
        niveau_stop_loss = 0
        niveau_stop_gain = 0
        duree_stop_gain = 0 
        for i, idx in enumerate(df.index): #fais la simulation jour par jour
            if i < 50: #Ne pas prendre les 50 premiers elements car elles servent a appliquer la strategie
                continue
            data_up_to_idx = df.loc[:idx] #prend la partie qui nous interesse
            level = data_up_to_idx['close'].iloc[-1]
            # Si une position est deja en cours
            if Position_active == 1:
                duree_stop_gain = duree_stop_gain-1 #diminue la duree max de la pose restante
                if nombre_achat == 1 : #cas pose longue
                    if  duree_stop_gain == 0 or level > niveau_stop_gain or level < niveau_stop_loss : 
                        # On ferme la position
                        Position_possible = 0
                        Position_active = 0
                    else : #on garde la position
                        df.at[idx, 'signal'] = 1
                else : #cas pose courte
                    if  duree_stop_gain == 0 or level < niveau_stop_gain or level > niveau_stop_loss : 
                        # On ferme la position
                        Position_possible = 0
                        Position_active = 0
                    else : #on garde la position
                        df.at[idx, 'signal'] = -1
            elif Position_possible == 1 :
                if nombre_achat == 1 : 
                    if level > niveau_annulation : #Si on atteint le niveau d'annulation sans avoir toucher le support
                        Position_possible = 0
                    if level < niveau_achat : #Si on atteint le support
                        Position_active = 1
                        df.at[idx, 'signal'] = 1
                        
                else :
                    if level < niveau_annulation : #Si on atteint le niveau d'annulation sans avoir toucher la resistance
                        Position_possible = 0
                    if level > niveau_achat : #Si on atteint la resistance
                        Position_active = 1
                        df.at[idx, 'signal'] = -1
                        
            else : #Appeler la strategie si rien n'est en cours
                nombre_achat,niveau_achat,niveau_annulation,niveau_stop_loss,niveau_stop_gain,duree_stop_gain = self.strat_fibonacci(data_up_to_idx)
                if nombre_achat != 0 : #Si une opportunité est detecté
                    Position_possible = 1

        return  df['signal'].shift(1)