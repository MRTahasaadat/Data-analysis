import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error, r2_score

def mean_absolute_percentage_error(y_true, y_pred):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    mask = y_true != 0
    y_true = y_true[mask]
    y_pred = y_pred[mask]

    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


def evaluate_regression(y_true, y_pred):
    # تبدیل به سری‌های پانداز برای فیلتر کردن راحت‌تر
    y_true = pd.Series(y_true).reset_index(drop=True)
    y_pred = pd.Series(y_pred).reset_index(drop=True)
    
    # پیدا کردن سطرهایی که هیچ‌کدام NaN نیستند
    mask = y_true.notna() & y_pred.notna()
    y_true_clean = y_true[mask]
    y_pred_clean = y_pred[mask]
    
    # اگر بعد از حذف NaNها داده‌ای باقی نمانده بود
    if len(y_true_clean) == 0:
        return {"MAE": np.nan, "RMSE": np.nan, "MAPE": np.nan, "R2": np.nan}
        
    mae = mean_absolute_error(y_true_clean, y_pred_clean)
    rmse = np.sqrt(mean_squared_error(y_true_clean, y_pred_clean))
    mape = mean_absolute_percentage_error(y_true_clean, y_pred_clean)
    r2 = r2_score(y_true_clean, y_pred_clean)
    
    return {
        "MAE": mae,
        "RMSE": rmse,
        "MAPE": mape,
        "R2": r2
    }
