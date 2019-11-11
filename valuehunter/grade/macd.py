from finta import TA
from valuehunter.grade import general

def hi_thresh_macd(macd_df, factor) -> float:
    return general.hi_thresh(macd_df['MACD'], factor)

def lo_thresh_macd(macd_df, factor) -> float:
    return general.lo_thresh(macd_df['MACD'], factor)

def score_hi_thresh_macd(macd_df, factor) -> float:
    val_series = macd_df['MACD']
    d = hi_thresh_macd(macd_df, factor)
    if d == 0: d = .00000001 # sets thresh output to very small number if 0 to avoid DBZ
    return val_series.iloc[-1] / d

def score_lo_thresh_macd(macd_df, factor) -> float:
    val_series = macd_df['MACD']
    d = lo_thresh_macd(macd_df, factor)
    if d == 0: d = .00000001 # sets thresh output to very small number if 0 to avoid DBZ
    return val_series.iloc[-1] / d

def score_thresh_macd(macd_df, factor) -> float:
    hi = score_hi_thresh_macd(macd_df, factor)
    lo = score_lo_thresh_macd(macd_df, factor)
    large = hi if hi > lo else lo * -1
    return large

def histogram_chain(r_hist, istart) -> int:
    o1 = istart
    o2 = istart + 1
    hist1 = r_hist.iloc[o1]
    hist2 = r_hist.iloc[o2]
    chain = 0
    if hist1 > hist2: # bearish chain head
        while hist1 >= hist2:
            o1 += 1
            o2 += 1
            hist1 = r_hist.iloc[o1]
            hist2 = r_hist.iloc[o2]
            chain += 1
    else: # bullish chain head (covers equals case)
        while hist1 <= hist2:
            o1 += 1
            o2 += 1
            hist1 = r_hist.iloc[o1]
            hist2 = r_hist.iloc[o2]
            chain -= 1
    return chain
        
def histogram_reversal_chain(macd_df, l=2, rev_only=True) -> int:
    values = []
    r_macd_data = macd_df.iloc[::-1]
    r_hist = r_macd_data['HISTOGRAM']
    for i in range(l):
        if rev_only: # will only consider lo-hi-lo or hi-lo-hi
            t1 = r_hist.iloc[i]
            t2 = r_hist.iloc[i+1]
            t3 = r_hist.iloc[i+2]
            if (t2 < t1 and t2 < t3) or (t1 < t2 and t3 < t2): # check 3 sequential values for reversal pattern
                values.append(histogram_chain(r_hist, i+1))
        else:
            values.append(histogram_chain(r_hist, i))
    
    values.append(0) # ensure that there is at least 1 value in list for max()
    abs_vals = [abs(val) for val in values]
    max_index = abs_vals.index(max(abs_vals))
    return values[max_index]
    