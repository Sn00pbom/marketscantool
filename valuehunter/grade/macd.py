from finta import TA
from valuehunter.grade import general

def hi_thresh_macd(macd_df, factor) -> float:
    return general.hi_thresh(macd_df['MACD'], factor)

def lo_thresh_macd(macd_df, factor) -> float:
    return general.lo_thresh(macd_df['MACD'], factor)

def score_hi_thresh_macd(macd_df, factor) -> float:
    val_series = macd_df['MACD']
    return val_series.iloc[-1] / hi_thresh_macd(macd_df, factor)

def score_lo_thresh_macd(macd_df, factor) -> float:
    val_series = macd_df['MACD']
    return val_series.iloc[-1] / lo_thresh_macd(macd_df, factor)

def score_thresh_macd(macd_df, factor) -> float:
    hi = score_hi_thresh_macd(macd_df, factor)
    lo = score_lo_thresh_macd(macd_df, factor)
    large = hi if hi > lo else lo * -1
    return large

# TODO implement histogram_chain()
    
def histogram_reversal_chain(macd_df, l=2) -> int:
    values = []
    r_macd_data = macd_df.iloc[::-1]
    r_hist = r_macd_data['HISTOGRAM']
    
    # Bear to Bull Reversal
    for i in range(l):
        # Check is reversal
        o1 = i
        o2 = i + 1
        hist1 = r_hist.iloc[o1]
        hist2 = r_hist.iloc[o2]
        if hist1 < hist2:
            # Compute chain length
            o1 += 1
            o2 += 1
            hist1 = r_hist.iloc[o1]
            hist2 = r_hist.iloc[o2]
            chain = 0
            while hist1 >= hist2:
                chain += 1
                o1 += 1
                o2 += 1
                hist1 = r_hist.iloc[o1]
                hist2 = r_hist.iloc[o2]
            values.append(chain)

    # Bull to Bear Reversal
    for i in range(l):
        # Check is reversal
        o1 = i
        o2 = i + 1
        hist1 = r_hist.iloc[o1]
        hist2 = r_hist.iloc[o2]
        if hist1 > hist2:
            # Compute chain length
            o1 += 1
            o2 += 1
            hist1 = r_hist.iloc[o1]
            hist2 = r_hist.iloc[o2]
            chain = 0
            while hist1 <= hist2:
                chain += 1
                o1 += 1
                o2 += 1
                hist1 = r_hist.iloc[o1]
                hist2 = r_hist.iloc[o2]
            values.append(chain * -1)
    values.append(0) # ensure that there is at least 1 value in list for max()
    abs_vals = [abs(val) for val in values]
    max_index = abs_vals.index(max(abs_vals))
    return values[max_index]
    