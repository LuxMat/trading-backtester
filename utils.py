
timeframe = granularity = "M5" #timeframe for historical data
def get_his_data_filename(pair, timeframe): #utility function to get historical data filename, måste fixa
    return f"data/his_data_{pair}_{timeframe}.csv" #här bestämmer vi var filen ska sparas, slipper byta flera ställen.

def get_instruments_data_filename(): #utility function to get instruments data filename
    return "instruments.csv"

if __name__ == "__main__":
    print(get_his_data_filename("EUR_USD", timeframe))
    print(get_instruments_data_filename())