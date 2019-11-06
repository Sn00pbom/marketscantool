from yahoo_finance_api2.share import Share
from yahoo_finance_api2.exceptions import YahooFinanceError
import pandas as pd
from io import StringIO


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

def get_historical_data(ticker, period_type, period, frequency_type, frequency) -> pd.DataFrame:
        share = Share(ticker)
        try:
            symbol_data = share.get_historical(
                period_type, period,
                frequency_type, frequency                
            )
            
            df = pd.DataFrame(symbol_data)
            assert not df.empty 
            # TODO fix to compute expected number of rows
            assert df.shape[0] is 251
            return df
        except YahooFinanceError as e:
            print(e.message, '-- Ticker:', ticker)
            return None
        except:
            print('Mismatch -- Ticker:', ticker, '...skipping')
            return None


def get_namespace_historical(namespace, period_type, period, frequency_type, frequency) -> dict:
    data_dict = {}
    for ticker in namespace.values:
        down_data = get_historical_data(ticker, period_type, period, frequency_type, frequency)
        if down_data is not None:
            data_dict[ticker] = down_data
    return data_dict

# def get_namespace_historical(namespace, period_type, period, frequency_type, frequency) -> pd.DataFrame:
#     return pd.Panel({ticker:get_historical_data(ticker, period_type, period, frequency_type, frequency) for ticker in namespace})
#     return pd.DataFrame([get_historical_data(ticker, period_type, period, frequency_type, frequency) for ticker in namespace], columns=['ticker', ''])