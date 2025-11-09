import pandas as pd
import yfinance as yf
from datetime import date, timedelta
import matplotlib.pyplot as plt
import numpy as np
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

def get_fixed_date_for_past_years(month, day, years=10):
    """
    Returns a list of pd.Timestamp for the given month/day
    for the past `years` years, starting from the current year (inclusive).
    Example: get_fixed_date_for_past_years(1, 1, 5)
    -> [2025-01-01, 2024-01-01, 2023-01-01, 2022-01-01, 2021-01-01]
    """
    current_year = date.today().year
    dates = [pd.Timestamp(year=y, month=month, day=day)
             for y in range(current_year, current_year - years, -1)]
    return dates
window = 10
stock = "GOLDBEES.NS"
end = date.today()
start = end - timedelta(days=365*20)
data = yf.download(stock, start=start, end=end, interval="1d")
results = event_window_min_max_change(data, get_fixed_date_for_past_years(1, 1) ,window)

for r in results:
    print(f"{r['event_date']} | H {r['highest_price']} on {r['highest_price_date']} | L {r['lowest_price']} on {r['lowest_price_date']} | {r['pct_change']:.2f}%")
