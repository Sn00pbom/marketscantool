from pandas import DataFrame


# def hi_thresh(dataframe, factor) -> DataFrame:
#     return dataframe.max() * factor
    
# def lo_thresh(dataframe, factor) -> DataFrame:
#     return dataframe.min() * factor

def hi_thresh(series, factor) -> float:
    return series.max() * factor

def lo_thresh(series, factor) -> float:
    return series.min() * factor
