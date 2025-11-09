import pandas as pd
import yfinance as yf
from datetime import date, timedelta
import matplotlib.pyplot as plt
import numpy as np
import os

stock = "GOLDBEES.NS"
def export_event_windows(data, event_dates, window, output_file=f"{stock}.csv"):
    # os.makedirs(os.path.dirname(output_file), exist_ok=True)
    all_data = []

    # Flatten multi-index columns (e.g. ('Close', 'LT.NS') → 'Close')
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [c[0] for c in data.columns]

    for event_date in event_dates:
        if not isinstance(event_date, pd.Timestamp):
            event_date = pd.to_datetime(event_date)

        window_start = event_date - pd.Timedelta(days=window)
        window_end = event_date + pd.Timedelta(days=window)
        window_data = data[(data.index >= window_start) & (data.index <= window_end)].copy()

        if window_data.empty:
            continue

        # Include real trading date + event info
        window_data = window_data.reset_index().rename(columns={'Date': 'Trading_Date'})
        window_data["Offset"] = (pd.to_datetime(window_data["Trading_Date"]) - event_date).dt.days
        window_data["Event_Date"] = event_date.strftime('%Y-%m-%d')
        window_data["Stock"] = stock

        # Reorder for readability
        cols = ["Trading_Date", "Event_Date", "Stock", "Offset", "Open", "High", "Low", "Close", "Volume"]
        window_data = window_data[[c for c in cols if c in window_data.columns]]

        all_data.append(window_data)

    # ✅ Combine everything into one file
    if all_data:
        combined = pd.concat(all_data)
        combined.to_csv(output_file, index=False)
        print(f"Saved all event windows to: {output_file}")
def event_window_min_max_change(data, event_dates, window):
    """
    For each event date, monitor price for +/- window days and return:
    - Event date,
    - Highest price, highest price date,
    - Lowest price, lowest price date,
    - % change (positive if high comes after low, negative if low comes after high)
    - sign: +1 (up then down), -1 (down after top)
    """
    results = []
    for event in event_dates:
        if not isinstance(event, pd.Timestamp):
            event = pd.to_datetime(event)
        window_start = event - pd.Timedelta(days=window)
        window_end = event + pd.Timedelta(days=window)
        window_data = data[(data.index >= window_start) & (data.index <= window_end)]
        if window_data.empty:
            continue
        min_idx = window_data['Low'].idxmin()
        if isinstance(min_idx, (pd.Series, pd.Index)):
            min_idx_val = min_idx[0]
        else:
            min_idx_val = min_idx
        min_val = window_data.loc[min_idx_val, 'Low']
        if isinstance(min_val, (pd.Series, pd.DataFrame)):
            min_price = float(min_val.iloc[0])
        else:
            min_price = float(min_val)
        min_idx_date = pd.to_datetime(min_idx_val)
        max_idx = window_data['High'].idxmax()
        if isinstance(max_idx, (pd.Series, pd.Index)):
            max_idx_val = max_idx[0]
        else:
            max_idx_val = max_idx
        max_val = window_data.loc[max_idx_val, 'High']
        if isinstance(max_val, (pd.Series, pd.DataFrame)):
            max_price = float(max_val.iloc[0])
        else:
            max_price = float(max_val)
        max_idx_date = pd.to_datetime(max_idx_val)
        # Determine sign and percent change based on event order
        if max_idx_date > min_idx_date:
            pct_change = ((max_price - min_price) / min_price) * 100
            sign = +1
        else:
            pct_change = -((min_price - max_price) / max_price) * 100
            sign = -1
        results.append({
            'event_date': event.strftime('%Y-%m-%d'),
            'highest_price': max_price,
            'highest_price_date': max_idx_date.strftime('%Y-%m-%d'),
            'lowest_price': min_price,
            'lowest_price_date': min_idx_date.strftime('%Y-%m-%d'),
            'pct_change': pct_change*sign,
        })
    return results

# def get_event_dates_for_month_day(data, month, day):
#     """
#     Returns a descending (latest first) list of pd.Timestamp for the given month, day for all years in data's index.
#     Example: get_event_dates_for_month_day(data, 4, 12) -> every 12th April in the data's years, latest first.
#     """
#     if not isinstance(data.index, pd.DatetimeIndex):
#         dt_idx = pd.to_datetime(data.index)
#     else:
#         dt_idx = data.index
#     years = sorted(dt_idx.year.unique(), reverse=True)  # Descending
#     event_dates = []
#     for y in years:
#         try:
#             ts = pd.Timestamp(year=y, month=month, day=day)
#             # Allow for same day as today if it exists in index
#             if ts in dt_idx:
#                 event_dates.append(ts)
#         except Exception:
#             continue  # skip invalid dates (e.g., Feb 29)
#     return event_dates

end = date.today()
start = end - timedelta(days=365*20)
data = yf.download(stock, start=start, end=end, interval="1d")
event_dates = [
    pd.Timestamp('2025-10-20'),  # Diwali 2025
    pd.Timestamp('2024-11-01'),  # Diwali 2024
    pd.Timestamp('2023-11-12'),  # Diwali 2023
    pd.Timestamp('2022-10-24'),  # Diwali 2022
    pd.Timestamp('2021-11-04'),  # Diwali 2021
    pd.Timestamp('2020-11-14'),  # Diwali 2020
    pd.Timestamp('2019-10-27'),  # Diwali 2019
    pd.Timestamp('2018-11-07'),  # Diwali 2018
    pd.Timestamp('2017-10-19'),  # Diwali 2017
    pd.Timestamp('2016-10-30'),  # Diwali 2016
    pd.Timestamp('2015-11-11'),  # Diwali 2015
    pd.Timestamp('2014-10-23'),  # Diwali 2014
    pd.Timestamp('2013-11-03'),  # Diwali 2013
    pd.Timestamp('2012-11-13'),  # Diwali 2012
    pd.Timestamp('2011-10-26'),  # Diwali 2011
    pd.Timestamp('2010-11-05'),  # Diwali 2010
    pd.Timestamp('2009-10-17'),  # Diwali 2009
    pd.Timestamp('2008-10-28'),  # Diwali 2008
    pd.Timestamp('2007-11-09'),  # Diwali 2007
    pd.Timestamp('2006-10-21'),  # Diwali 2006
    pd.Timestamp('2005-11-01'),  # Diwali 2005
    pd.Timestamp('2004-11-12'),  # Diwali 2004
    pd.Timestamp('2003-10-25'),  # Diwali 2003
    pd.Timestamp('2002-11-04'),  # Diwali 2002
    pd.Timestamp('2001-11-14'),  # Diwali 2001
    pd.Timestamp('2000-10-26'),  # Diwali 2000
    pd.Timestamp('1999-11-07'),  # Diwali 1999
    pd.Timestamp('1998-10-19'),  # Diwali 1998
    pd.Timestamp('1997-10-30'),  # Diwali 1997
    pd.Timestamp('1996-11-12'),  # Diwali 1996
]
window = 10
results = event_window_min_max_change(data, event_dates ,window)
export_event_windows(data, event_dates, window)

for r in results:
    print(f"{r['event_date']} | H {r['highest_price']} on {r['highest_price_date']} | L {r['lowest_price']} on {r['lowest_price_date']} | {r['pct_change']:.2f}%")

