import pandas as pd
import utils
import instrument
import ma_result
pd.set_option('display.max_columns', None) #show all columns when printing dataframe


def is_trade(row):
    if row.DIFF >= 0 and row.DIFF_PREV < 0:
        return 1  # Buy
    elif row.DIFF < 0 and row.DIFF_PREV >= 0:
        return -1  # Sell
    else:
        return 0  # No trade


def get_ma_col(ma):
    return f"MA_{ma}"


def evaluate_pair(i_pair, ma_short, ma_long, price_data):

    price_data['DIFF'] = price_data[get_ma_col(ma_short)] - price_data[get_ma_col(ma_long)]
    price_data['DIFF_PREV'] = price_data['DIFF'].shift(1)
    price_data['IS_TRADE'] = price_data.apply(is_trade, axis=1)

    df_trades = price_data[price_data['IS_TRADE'] != 0].copy()
    #df_trades['DELTA'] = (df_trades.close.diff()/i_pair.pipLocation).shift(-1)  #calculate difference between trade prices, shifted by 1 to avoid lookahead bias
    df_trades['DELTA'] = df_trades.close.diff().shift(-1)
    df_trades['GAINS'] = df_trades["DELTA"] * df_trades["IS_TRADE"]  #calculate gains based on trade direction


    #print(f'{i_pair.pairname} MA Short: {ma_short}, MA Long: {ma_long}, Trades:{df_trades.shape[0]}, Total Gains: {df_trades["Gains"].sum():.0f}')
    ##print(f'USD_BCT, MA Short: {ma_short}, MA Long: {ma_long}, Trades:{df_trades.shape[0]}, Total Gains: {df_trades["GAINS"].sum():.0f}')

    return ma_result.MAResult(
        df_trades=df_trades,
        pairname=i_pair.name,
        #pairname='BTC_USD',
        params={'mashort' : ma_short, 'malong' : ma_long}
    )



def get_price_data(pairname, granularity):
    df = pd.read_csv(utils.get_his_data_filename(pairname, granularity))
    df[["open_time", "close_time"]] = df[["open_time", "close_time"]].apply(pd.to_datetime, utc=True)            #to be deleted...
    non_cols = ['open_time', 'volume']
    mod_cols = [x for x in df.columns if x not in non_cols]
    df[mod_cols] = df[mod_cols].apply(pd.to_numeric)

    return df[['open_time', 'close']]



def processs_data(ma_short, ma_long, price_data):
    ma_list = set(ma_short + ma_long)

    for ma in ma_list:
        price_data[get_ma_col(ma)] = price_data['close'].rolling(window=ma).mean()

    return price_data


def process_results(results):
    results_list = [r.result_ob() for r in results]
    final_df = pd.DataFrame.from_dict(results_list)

    final_df.to_csv('ma_test_res.csv')
    print(final_df.shape, final_df.num_trades.sum())
    

'''''' 
def get_test_pairs(pair_str):
    existing_pairs = instrument.Instrument.get_instruments_dict().keys()
    pairs = pair_str.split(",")
    
    test_list = []
    for p1 in pairs:
        for p2 in pairs:
            p = f'{p1}_{p2}'
            if p in existing_pairs:
                test_list.append(p)

    print(test_list)
    return test_list


def run():
    currencies = 'BTC,USD,ETH' #add more!
    granularity = "1m"
    ma_short = [8, 10, 12]
    ma_long = [21, 34, 55]
    test_pairs = get_test_pairs(currencies)

    results = []
    for pairname in test_pairs:
        print("running..", pairname)
        i_pair = instrument.Instrument.get_instruments_dict()[pairname]

        price_data = get_price_data(pairname, granularity)
        price_data = processs_data(ma_short, ma_long, price_data)

        #iterate through all combinations of ma_short and ma_long to find the best performing pair.
        for _malong in ma_long:
            for _mashort in ma_short:
                if _mashort >= _malong:
                    continue
                results.append(evaluate_pair(i_pair, _mashort, _malong, price_data.copy())) #result 

    process_results(results)

if __name__ == "__main__":
    run()
    #get_test_pairs('BTC,USD,EUR,CHF,ETH')