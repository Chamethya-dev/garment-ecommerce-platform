import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta

def get_rfm_segmentation(orders, users):
    """Performs RFM (Recency, Frequency, Monetary) Analysis on customers."""
    if not orders:
        return []

    # Convert SQLAlchemy objects to a Pandas DataFrame
    data = []
    for order in orders:
        data.append({
            'user_id': order.user_id,
            'order_id': order.order_id,
            'order_date': order.order_date,
            'total_amount': float(order.total_amount)
        })

    df = pd.DataFrame(data)

    # Calculate RFM Metrics
    today = datetime.now()
    rfm = df.groupby('user_id').agg({
        'order_date': lambda x: (today - x.max()).days, # Recency (days since last order)
        'order_id': 'count',                            # Frequency (total orders)
        'total_amount': 'sum'                           # Monetary (total spent)
    })

    rfm.columns = ['recency', 'frequency', 'monetary']
    rfm.reset_index(inplace=True)

    # --- ROBUST SCORING FOR SMALL DATASETS ---
    def safe_qcut(series, labels, ascending=True):
        try:
            # rank(method='first') ensures unique values to prevent qcut errors
            ranked = series.rank(method='first', ascending=ascending)
            return pd.qcut(ranked, 3, labels=labels, duplicates='drop')
        except ValueError:
            # Fallback: if dataset is too small for 3 bins, assign middle score (2)
            return pd.Series([2] * len(series), index=series.index)

    # Recency: Lower days = better score (3). So ascending=False for rank.
    rfm['r_score'] = safe_qcut(rfm['recency'], [1, 2, 3], ascending=False)
    # Frequency: Higher = better score (3). ascending=True.
    rfm['f_score'] = safe_qcut(rfm['frequency'], [1, 2, 3], ascending=True)
    # Monetary: Higher = better score (3). ascending=True.
    rfm['m_score'] = safe_qcut(rfm['monetary'], [1, 2, 3], ascending=True)

    # Fill any NaNs just in case and ensure they are integers
    rfm['r_score'] = rfm['r_score'].fillna(2).astype(int)
    rfm['f_score'] = rfm['f_score'].fillna(2).astype(int)
    rfm['m_score'] = rfm['m_score'].fillna(2).astype(int)

    # Assign Segments
    def assign_segment(row):
        r, f, m = int(row['r_score']), int(row['f_score']), int(row['m_score'])
        if r >= 2 and f >= 2 and m >= 2:
            return 'VIP'
        elif f >= 2 and m >= 2:
            return 'Loyal'
        elif r >= 2 and f == 1:
            return 'New'
        elif r == 1 and f >= 2:
            return 'At Risk'
        else:
            return 'Regular'

    rfm['segment'] = rfm.apply(assign_segment, axis=1)

    # Merge with User names
    user_dict = {u.user_id: u.name for u in users}
    rfm['user_name'] = rfm['user_id'].map(user_dict)

    return rfm.to_dict('records')

def forecast_sales(orders):
    """Simple Linear Regression to forecast next 7 days of sales."""
    if len(orders) < 7:
        return None, None # Not enough data

    # Aggregate daily sales
    daily_sales = {}
    for order in orders:
        date_str = order.order_date.strftime('%Y-%m-%d')
        daily_sales[date_str] = daily_sales.get(date_str, 0) + float(order.total_amount)

    # Sort by date
    sorted_dates = sorted(daily_sales.keys())
    y = np.array([daily_sales[d] for d in sorted_dates]).reshape(-1, 1)
    
    # Create sequential X values (0, 1, 2, 3...)
    X = np.array(range(len(sorted_dates))).reshape(-1, 1)

    # Train Model
    model = LinearRegression()
    model.fit(X, y)

    # Predict next 7 days
    future_X = np.array(range(len(sorted_dates), len(sorted_dates) + 7)).reshape(-1, 1)
    predictions = model.predict(future_X)
    
    # Generate future dates
    last_date = datetime.strptime(sorted_dates[-1], '%Y-%m-%d')
    future_dates = [(last_date + timedelta(days=i+1)).strftime('%Y-%m-%d') for i in range(7)]

    return future_dates, predictions.tolist()