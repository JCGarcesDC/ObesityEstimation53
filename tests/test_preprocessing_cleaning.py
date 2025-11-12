import pandas as pd
import numpy as np
import pytest

from src.preprocessing.cleaning import DataCleaner, OutlierDetector


def test_datacleaner_fit_transform_basic():
    # Use already standardized target labels to match OBESITY_MAPPING
    df = pd.DataFrame({
        'Age': [20, 21, 21, 22, np.nan],
        'Weight': [70, None, 72, 71, 70],
        'Gender': [' Male', 'female ', 'Female', None, 'male'],
        'NObeyesdad': ['normal_weight', 'overweight_level_i', 'normal_weight', 'normal_weight', 'obesity_type_i']
    })

    cleaner = DataCleaner(target_col='NObeyesdad', numeric_impute_strategy='median', standardize_columns=True, standardize_values=True)
    df_clean = cleaner.fit_transform(df)

    # Columns standardized to lowercase with underscores
    assert set(df_clean.columns) >= {'age', 'weight', 'gender', 'nobeyesdad'}

    # No NaNs remain in numeric columns
    assert df_clean['age'].isna().sum() == 0
    assert df_clean['weight'].isna().sum() == 0

    # Categorical standardized (strip/lower/underscore)
    assert set(df_clean['gender'].unique()) <= {'male', 'female', 'none'}

    # Target encoded as integers and within expected range
    assert pd.api.types.is_integer_dtype(df_clean['nobeyesdad'])
    assert df_clean['nobeyesdad'].between(0, 6).all()


def test_outlier_detector_cap_method():
    df = pd.DataFrame({'x': [1, 2, 3, 1000], 'y': [10, 11, 12, -999]})

    det = OutlierDetector(method='iqr', action='cap', iqr_factor=1.5).fit(df)
    df_out = det.transform(df)

    # After capping, extremes should be within learned bounds
    bounds = det.get_params()['bounds']
    for col, (lower, upper) in bounds.items():
        assert df_out[col].between(lower, upper).all()
