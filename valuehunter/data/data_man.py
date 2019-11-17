from yahoo_finance_api2.share import Share
from yahoo_finance_api2.exceptions import YahooFinanceError
import pandas as pd
from io import StringIO

STD_LEN = 0

def benchmark_length(period_type, period, frequency_type, frequency) -> int:
    global STD_LEN
    print('Getting benchmark length...')
    share = Share('ED')
    try:
        symbol_data = share.get_historical(
            period_type, period, frequency_type, frequency
        )
        # return pd.DataFrame(symbol_data).shape[0]
        STD_LEN = pd.DataFrame(symbol_data).shape[0]
        
    except YahooFinanceError as e:
        print(e.message, '-- Benchmark Error')
        STD_LEN = 0
    except:
        print('Benchmark Error')
        STD_LEN = 0

def load_tos_data(path, index='Symbol') -> pd.DataFrame:
    file = open(path, 'r')
    data = file.read()
    file.close()
    data = data.split('\n')
    data = data[3:len(data)-1]
    s = '\n'.join(data)
    df = pd.read_csv(StringIO(s))
    df.set_index(index, inplace=True)
    return df

def get_historical_data(ticker, period_type, period, frequency_type, frequency, standardize=True) -> pd.DataFrame:
    if STD_LEN is 0: 
        benchmark_length(period_type, period, frequency_type, frequency)

    share = Share(ticker)
    try:
        symbol_data = share.get_historical(
            period_type, period,
            frequency_type, frequency                
        )
        
        df = pd.DataFrame(symbol_data)
        assert not df.empty 
        # TODO fix to compute expected number of rows instead of using standard length
        # standardize size
        if standardize:
            assert df.shape[0] is STD_LEN
        # df = df.rename(columns={key:key.capitalize() for key in df}) # capitalize all column names for consistency
        return df
    except YahooFinanceError as e:
        print(e.message, '@ Ticker', ticker)
        return None
    except:
        print('Data Mismatch @ Ticker', ticker, '\t...skipping')
        return None


def get_namespace_historical(namespace, period_type, period, frequency_type, frequency) -> dict:
    data_dict = {}
    for ticker in namespace:
        down_data = get_historical_data(ticker, period_type, period, frequency_type, frequency)
        if down_data is not None:
            data_dict[ticker] = down_data
    return data_dict