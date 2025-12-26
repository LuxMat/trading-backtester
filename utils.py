import datetime as dt
from datetime import datetime, timezone
from dateutil.parser import *

#timeframe = granularity = "M5" #timeframe for historical data
def get_his_data_filename(pair, granularity): #utility function to get historical data filename, måste fixa
    return f"data/his_data_{pair}_{granularity}.csv" #här bestämmer vi var filen ska sparas, slipper byta flera ställen.

def get_instruments_data_filename(): #utility function to get instruments data filename
    return "instruments.csv"

def time_utc():
#    return dt.datetime.now(dt.timezone.utc).replace(tzinfo=dt.timezone.utc)
    return dt.datetime.now(dt.timezone.utc)

def get_utc_dt_from_string(date_str):
    d = parse(date_str)
    return d.replace(tzinfo=dt.timezone.utc)

if __name__ == "__main__":
    #print(get_his_data_filename("BTC_USD", '1m'))
    #print(get_instruments_data_filename())
    print(dt.datetime.now(dt.timezone.utc))
    print(time_utc())
    print(get_utc_dt_from_string("2020-02-01 03:00:00"))