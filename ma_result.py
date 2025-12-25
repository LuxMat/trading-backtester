class MAResult():
    def __init__(self, df_trades, pairname, params):
        self.pairname = pairname
        self.df_trades = df_trades
        self.params = params

    def result_ob(self):
        d = {
            'pair' : self.pairname,
            'num_trades' : self.df_trades.shape[0],
            'total_gain' : self.df_trades.GAINS.sum(),
            'mean_gain' : self.df_trades.GAINS.mean(),
            'min_gain' : self.df_trades.GAINS.min(),
            'max_gain' : self.df_trades.GAINS.max()
        }

        for k,v in self.params.items():          #whut?
            d[k] = v

        return d