import pandas as pd
import utils

class Instrument:
    def __init__(self, ob):
        self.name = ob['name']
        self.ins_type = ob['type']
        self.displayname = ob['displayName']
        self.pipLocation = pow(10, ob['pipLocation']) #10 to the power of pipLocation, -4 -> 0.0001
        self.marginRate = ob['marginRate']
        
    def __repr__(self):
            return str(vars(self))

    @classmethod
    def get_instruments_df(cls):
         return pd.read_csv(utils.get_instruments_data_filename())

    @classmethod
    def get_instruments_list(cls):
        df = cls.get_instruments_df()
        return [Instrument(x) for x in df.to_dict(orient='records')]


    '''
    dict to acess instruments by pair name

    instruments_dict = 
    {

        "EUR_USD": Instrument(...),
        "GBP_USD": Instrument(...),
        "...": Instrument(...), 

    }

    our_instrument = instruments_dict["EUR_USD"]
    '''

    @classmethod
    def get_instruments_dict(cls):
        i_list = cls.get_instruments_list()
        i_keys = [x.name for x in i_list]
        return { k:v for (k,v) in zip(i_keys, i_list) } #zip to pair names and instrument objects

    @classmethod
    def get_instrument_by_name(cls, pairname):
        d = cls.get_instruments_dict()
        if pairname in d:
            return d[pairname]
        else:
            return None


if __name__ == "__main__":
    print(Instrument.get_instruments_df())
    
    #for k,v in Instrument.get_instruments_dict().items():
    #    print(k,v)

    #1st test get_instruments_list
    #df = Instrument.get_instruments_df()

    #ll = df.to_dict(orient='records')
    #for item in ll:
    #    print(item)
